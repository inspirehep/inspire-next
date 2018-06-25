# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Workflows utils."""

from __future__ import absolute_import, division, print_function

import json
import os
import traceback
from contextlib import closing, contextmanager
from functools import wraps
from six import text_type
from six.moves.urllib.parse import unquote
import backoff
import lxml.etree as ET
import requests
from flask import current_app, url_for
from timeout_decorator import TimeoutError
from fs.opener import fsopen
from invenio_db import db

from inspire_schemas.utils import \
    get_validation_errors as _get_validation_errors
from inspire_utils.logging import getStackTraceLogger

from inspirehep.utils.url import retrieve_uri
from inspirehep.modules.workflows.models import (
    WorkflowsAudit,
    WorkflowsRecordSources,
)


LOGGER = getStackTraceLogger(__name__)


@backoff.on_exception(backoff.expo, requests.packages.urllib3.exceptions.ConnectionError, base=4, max_tries=5)
def json_api_request(url, data, headers=None):
    """Make JSON API request and return JSON response."""
    final_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if headers:
        final_headers.update(headers)
    current_app.logger.debug("POST {0} with \n{1}".format(
        url, json.dumps(data, indent=4)
    ))
    try:
        response = requests.post(
            url=url,
            headers=final_headers,
            data=json.dumps(data),
        )
    except requests.exceptions.RequestException as err:
        current_app.logger.exception(err)
        raise
    if response.status_code == 200:
        return response.json()


def log_workflows_action(action, relevance_prediction,
                         object_id, user_id,
                         source, user_action=""):
    """Log the action taken by user compared to a prediction."""
    if relevance_prediction:
        score = relevance_prediction.get("max_score")  # returns 0.222113
        decision = relevance_prediction.get("decision")  # returns "Rejected"

        # Map actions to align with the prediction format
        action_map = {
            'accept': 'Non-CORE',
            'accept_core': 'CORE',
            'reject': 'Rejected'
        }

        logging_info = {
            'object_id': object_id,
            'user_id': user_id,
            'score': score,
            'user_action': action_map.get(user_action, ""),
            'decision': decision,
            'source': source,
            'action': action
        }
        audit = WorkflowsAudit(**logging_info)
        audit.save()


def with_debug_logging(func):
    """Generate a debug log with info on what's going to run.

    It tries its best to use the logging facilities of the object passed or the
    application context before falling back to the python logging facility.
    """
    @wraps(func)
    def _decorator(*args, **kwargs):
        def _get_obj(args, kwargs):
            if args:
                obj = args[0]
            else:
                obj = kwargs.get('obj', kwargs.get('record'))
            return obj

        def _get_logfn(args, kwargs):
            obj = _get_obj(args, kwargs)
            if hasattr(obj, 'log') and hasattr(obj.log, 'debug'):
                logfn = obj.log.debug
            elif hasattr(current_app, 'logger'):
                logfn = current_app.logger.debug
            else:
                logfn = LOGGER.debug

            return logfn

        def _try_to_log(logfn, *args, **kwargs):
            try:
                logfn(*args, **kwargs)
            except Exception:
                LOGGER.debug(
                    'Error while trying to log with %s:\n%s',
                    logfn,
                    traceback.format_exc()
                )

        logfn = _get_logfn(args, kwargs)

        _try_to_log(logfn, 'Starting %s', func)
        res = func(*args, **kwargs)
        _try_to_log(
            logfn,
            "Finished %s with (single quoted) result '%s'",
            func,
            res,
        )

        return res

    return _decorator


def ignore_timeout_error(return_value=None):
    """Ignore the TimeoutError, returning return_value when it happens.

    Quick fix for ``refextract`` and ``plotextract`` tasks only. It
    shouldn't be used for others!
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                LOGGER.error(
                    'Timeout error while extracting raised from: %s.',
                    func.__name__
                )
                return return_value
        return wrapper
    return decorator


@contextmanager
@with_debug_logging
def get_document_in_workflow(obj):
    """Context manager giving the path to the document attached to a workflow object.

    Arg:
        obj: workflow object

    Returns:
        Optional[str]: The path to a local copy of the document.  If no
        documents are present, it retuns None.  If several documents are
        present, it prioritizes the fulltext. If several documents with the
        same priority are present, it takes the first one and logs an error.
    """
    documents = obj.data.get('documents', [])
    fulltexts = [document for document in documents if document.get('fulltext')]
    documents = fulltexts or documents

    if not documents:
        obj.log.info('No document available')
        yield None
        return
    elif len(documents) > 1:
        obj.log.error('More than one document in workflow, first one used')

    key = documents[0]['key']
    obj.log.info('Using document with key "%s"', key)
    with retrieve_uri(obj.files[key].file.uri) as local_file:
        yield local_file


@with_debug_logging
def copy_file_to_workflow(workflow, name, url):
    url = unquote(url)
    stream = fsopen(url, mode='rb')
    workflow.files[name] = stream
    return workflow.files[name]


@backoff.on_exception(backoff.expo, requests.packages.urllib3.exceptions.ProtocolError, max_tries=5)
def download_file_to_workflow(workflow, name, url):
    """Download a file to a specified workflow.

    The ``workflow.files`` property is actually a method, which returns a
    ``WorkflowFilesIterator``. This class inherits a custom ``__setitem__``
    method from its parent, ``FilesIterator``, which ends up calling ``save``
    on an ``invenio_files_rest.storage.pyfs.PyFSFileStorage`` instance
    through ``ObjectVersion`` and ``FileObject``. This method consumes the
    stream passed to it and saves in its place a ``FileObject`` with the
    details of the downloaded file.

    Consuming the stream might raise a ``ProtocolError`` because the server
    might terminate the connection before sending any data. In this case we
    retry 5 times with exponential backoff before giving up.
    """
    with closing(requests.get(url=url, stream=True)) as req:
        if req.status_code == 200:
            req.raw.decode_content = True
            workflow.files[name] = req.raw
            return workflow.files[name]


def convert(xml, xslt_filename):
    """Convert XML using given XSLT stylesheet."""
    if not os.path.isabs(xslt_filename):
        prefix_dir = os.path.dirname(os.path.realpath(__file__))
        xslt_filename = os.path.join(prefix_dir, "stylesheets", xslt_filename)

    dom = ET.fromstring(xml)
    xslt = ET.parse(xslt_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return ET.tostring(newdom, pretty_print=False)


def read_wf_record_source(record_uuid, source):
    """Retrieve a record from the ``WorkflowRecordSource`` table.

    Args:
        record_uuid(uuid): the uuid of the record
        source(string): the acquisition source value of the record

    Return:
        (dict): the given record, if any or None
    """
    if not source:
        return
    source = get_source_for_root(source)

    entry = WorkflowsRecordSources.query.filter_by(
        record_uuid=str(record_uuid),
        source=source.lower(),
    ).one_or_none()
    return entry


def read_all_wf_record_sources(record_uuid):
    """Retrieve all ``WorkflowRecordSource`` for a given record id.

    Args:
        record_uuid(uuid): the uuid of the record

    Return:
        (list): the ``WorkflowRecordSource``s related to ``record_uuid``
    """
    entries = list(WorkflowsRecordSources.query.filter_by(record_uuid=str(record_uuid)))
    return entries


def insert_wf_record_source(json, record_uuid, source):
    """Stores a record in the WorkflowRecordSource table in the db.

    Args:
        json(dict): the record's content to store
        record_uuid(uuid): the record's uuid
        source(string): the source of the record
    """
    if not source:
        return

    source = get_source_for_root(source)
    record_source = read_wf_record_source(
        record_uuid=record_uuid, source=source)

    if record_source is None:
        record_source = WorkflowsRecordSources(
            source=source.lower(),
            json=json,
            record_uuid=record_uuid,
        )
        db.session.add(record_source)
    else:
        record_source.json = json
    db.session.commit()


def get_source_for_root(source):
    """Source for the root workflow object.

    Args:
        source(str): the record source.

    Return:
        (str): the source for the root workflow object.

    Note:
        For the time being any workflow with ``acquisition_source.source``
        different than ``arxiv`` and ``submitter`` will be stored as
        ``publisher``.
    """
    return source if source in ['arxiv', 'submitter'] else 'publisher'


def get_resolve_validation_callback_url():
    """Resolve validation callback.

    Returns the callback url for resolving the validation errors.

    Note:
        It's using ``inspire_workflows.callback_resolve_validation``
        route.
    """
    return url_for(
        'inspire_workflows_callbacks.callback_resolve_validation',
        _external=True
    )


def get_resolve_merge_conflicts_callback_url():
    """Resolve validation callback.

    Returns the callback url for resolving the merge conflicts.

    Note:
        It's using ``inspire_workflows.callback_resolve_merge_conflicts``
        route.
    """
    return url_for(
        'inspire_workflows_callbacks.callback_resolve_merge_conflicts',
        _external=True
    )


def get_resolve_edit_article_callback_url():
    """Resolve edit_article workflow letting it continue.

    Note:
        It's using ``inspire_workflows.callback_resolve_edit_article``
        route.
    """
    return url_for(
        'inspire_workflows_callbacks.callback_resolve_edit_article',
        _external=True
    )


def get_validation_errors(data, schema):
    """Creates a ``validation_errors`` dictionary.

    Args:
        data (dict): the object to validate.
        schema (str): the name of the schema.

    Returns:
        dict: ``validation_errors`` formatted dict.
    """
    errors = _get_validation_errors(data, schema=schema)
    error_messages = [
        {
            'path': map(text_type, error.absolute_path),
            'message': text_type(error.message),
        } for error in errors
    ]
    return error_messages
