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

from invenio_db import db

import backoff
import lxml.etree as ET
import requests
from flask import current_app, url_for
from fs.opener import fsopen
from inspire_schemas.utils import \
    get_validation_errors as _get_validation_errors
from inspire_utils.logging import getStackTraceLogger
from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows.errors import WorkflowsError
from six import text_type
from six.moves.urllib.parse import unquote
from timeout_decorator import TimeoutError, timeout
from simplejson import JSONDecodeError
from inspirehep.modules.workflows.errors import BadGatewayError

from inspirehep.modules.pidstore.utils import (get_endpoint_from_pid_type,
                                               get_pid_type_from_schema)
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.errors import (
    MissingInspireRecordError, MissingUUIDOrRevisionInHEPResponse)
from inspirehep.modules.workflows.errors import InspirehepMissingDataError
from inspirehep.modules.workflows.models import WorkflowsAudit, WorkflowsRecordSources
from inspirehep.utils.url import retrieve_uri
from invenio_workflows import ObjectStatus

LOGGER = getStackTraceLogger(__name__)


@backoff.on_exception(
    backoff.expo,
    requests.packages.urllib3.exceptions.ConnectionError,
    base=4,
    max_tries=5,
)
def json_api_request(url, data, headers=None):
    """Make JSON API request and return JSON response."""
    final_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        final_headers.update(headers)
    current_app.logger.debug(
        "POST {0} with \n{1}".format(url, json.dumps(data, indent=4))
    )
    try:
        response = requests.post(
            url=url,
            headers=final_headers,
            data=json.dumps(data),
        )
    except requests.exceptions.RequestException as err:
        current_app.logger.exception(err)
        raise

    response.raise_for_status()
    return response.json()


def log_workflows_action(
    action, relevance_prediction, object_id, user_id, source, user_action=""
):
    """Log the action taken by user compared to a prediction."""
    if relevance_prediction:
        score = relevance_prediction.get("max_score")  # returns 0.222113
        decision = relevance_prediction.get("decision")  # returns "Rejected"

        # Map actions to align with the prediction format
        action_map = {"accept": "Non-CORE", "accept_core": "CORE", "reject": "Rejected"}

        logging_info = {
            "object_id": object_id,
            "user_id": user_id,
            "score": score,
            "user_action": action_map.get(user_action, ""),
            "decision": decision,
            "source": source,
            "action": action,
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
                obj = kwargs.get("obj", kwargs.get("record"))
            return obj

        def _get_logfn(args, kwargs):
            obj = _get_obj(args, kwargs)
            if hasattr(obj, "log") and hasattr(obj.log, "debug"):
                logfn = obj.log.debug
            elif hasattr(current_app, "logger"):
                logfn = current_app.logger.debug
            else:
                logfn = LOGGER.debug

            return logfn

        def _try_to_log(logfn, *args, **kwargs):
            try:
                logfn(*args, **kwargs)
            except Exception:
                LOGGER.debug(
                    "Error while trying to log with %s:\n%s",
                    logfn,
                    traceback.format_exc(),
                )

        logfn = _get_logfn(args, kwargs)

        _try_to_log(logfn, "Starting %s", func)
        res = func(*args, **kwargs)
        _try_to_log(
            logfn,
            "Finished %s with (single quoted) result '%s'",
            func,
            res,
        )

        return res

    return _decorator


def do_not_repeat(step_id):
    """Decorator used to skip workflow steps when a workflow is re-run.
    Will store the result of running the workflow step in source_data.persistent_data
    after running the first time, and skip the step on the following runs, also applying
    previously recorded 'changes' to extra_data.
    The decorated function has to conform to the following signature:
        def decorated_step(obj: WorkflowObject, eng: WorkflowEngine) -> Dict[str, Any]: ...
    Where obj and eng are usual arguments following the protocol of all workflow steps.
    The returned value of the decorated_step will be used as a patch to be applied on the
    workflow object's source data (which 'replays' changes made by the workflow step).
    Args:
        step_id (str): name of the workflow step, to be used as key in persistent_data
    Returns:
        callable: the decorator
    """

    def decorator(func):
        @wraps(func)
        def _do_not_repeat(obj, eng):
            source_data = obj.extra_data["source_data"]
            is_task_repeated = step_id in obj.extra_data["source_data"].setdefault(
                "persistent_data", {}
            )
            if is_task_repeated:
                extra_data_update = source_data["persistent_data"][step_id]
                obj.extra_data.update(extra_data_update)
                obj.save()
                return

            return_value = func(obj, eng)
            if not isinstance(return_value, dict):
                raise TypeError(
                    "Functions decorated by 'do_not_repeat' must return a "
                    "dictionary compliant to extra_data info"
                )
            source_data["persistent_data"][step_id] = return_value
            obj.save()
            return return_value

        return _do_not_repeat

    return decorator


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
                    "Timeout error while extracting raised from: %s.", func.__name__
                )
                return return_value

        return wrapper

    return decorator


def timeout_with_config(config_key):
    """Decorator to set a configurable timeout on a function.
    Args:
        config_key (str): config key with a integer value representing the time in
            seconds after which the decorated function will abort, raising a
            ``TimeoutError``. If the key is not present in the config, a
            ``KeyError`` is raised.
    Note:
        This function is needed because it's impossible to pass a value read
        from the config as an argument to a decorator, as it gets evaluated
        before the application context is set up.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timeout_time = current_app.config[config_key]
            use_signals = current_app.config.get("USE_SIGNALS_ON_TIMEOUT", True)
            return timeout(timeout_time, use_signals=use_signals)(func)(*args, **kwargs)

        return wrapper

    return decorator


@with_debug_logging
def get_document_url_for_reference_extraction(obj):
    documents = obj.data.get("documents", [])
    fulltexts = [document for document in documents if (document.get("fulltext") and document.get("key", "").endswith(".pdf"))]
    documents = fulltexts or documents

    if not documents:
        obj.log.info("No document available")
        return
    elif len(documents) > 1:
        obj.log.error("More than one document in workflow, first one used")

    url = documents[0]["url"]
    obj.log.info('Using document with url "%s"', url)
    return _get_hep_url_for_document(url)


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
    documents = obj.data.get("documents", [])
    fulltexts = [document for document in documents if document.get("fulltext")]
    documents = fulltexts or documents

    if not documents:
        obj.log.info("No document available")
        yield None
        return
    elif len(documents) > 1:
        obj.log.error("More than one document in workflow, first one used")

    key = documents[0]["key"]
    obj.log.info('Using document with key "%s"', key)
    with retrieve_uri(obj.files[key].file.uri) as local_file:
        yield local_file


@with_debug_logging
def copy_file_to_workflow(workflow, name, url):
    url = unquote(url)
    stream = fsopen(url, mode="rb")
    workflow.files[name] = stream
    return workflow.files[name]


@backoff.on_exception(
    backoff.expo,
    (
        requests.packages.urllib3.exceptions.ProtocolError,
        requests.exceptions.HTTPError,
    ),
    max_tries=5,
)
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
    with closing(
        requests.get(
            url=url,
            stream=True,
            timeout=current_app.config['DOWNLOAD_FILE_TO_WORKFLOW_TIMEOUT']
        )
    ) as req:
        req.raise_for_status()
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


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
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
    if current_app.config.get('FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP'):
        headers = _get_headers_for_hep_root_table_request()
        response = requests.get(
            "{inspirehep_url}/literature/workflows_record_sources".format(
                inspirehep_url=current_app.config["INSPIREHEP_URL"]
            ),
            headers=headers,
            data=json.dumps({"record_uuid": str(record_uuid), "source": source.lower()}),
        )
        if response.status_code == 200:
            return response.json()["workflow_sources"][0]
        elif response.status_code == 404:
            return []
        else:
            raise WorkflowsError(
                "Error from inspirehep [{code}]: {message}".format(
                    code=response.status_code, message=response.json()
                )
            )
    else:
        entry = WorkflowsRecordSources.query.filter_by(
            record_uuid=str(record_uuid),
            source=source.lower(),
        ).one_or_none()
        return entry


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_all_wf_record_sources(record_uuid):
    """Retrieve all ``WorkflowRecordSource`` for a given record id.
    Args:
        record_uuid(uuid): the uuid of the record
    Return:
        (list): the ``WorkflowRecordSource``s metadata related to ``record_uuid``
    """
    if current_app.config.get('FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP'):
        inspirehep_url = current_app.config.get("INSPIREHEP_URL")
        headers = _get_headers_for_hep_root_table_request()
        response = requests.get(
            "{inspirehep_url}/literature/workflows_record_sources".format(
                inspirehep_url=inspirehep_url
            ),
            headers=headers,
            data=json.dumps({"record_uuid": record_uuid}),
        )
        if response.status_code == 200:
            return response.json()["workflow_sources"]
        elif response.status_code == 404:
            return []
        else:
            raise WorkflowsError(
                "Error from inspirehep [{code}]: {message}".format(
                    code=response.status_code, message=response.json()
                )
            )
    else:
        entries = list(WorkflowsRecordSources.query.filter_by(record_uuid=str(record_uuid)))
        return entries


def insert_wf_record_source(json_data, record_uuid, source):
    """Stores a record in the WorkflowRecordSource table in the db.
    Args:
        json(dict): the record's content to store
        record_uuid(uuid): the record's uuid
        source(string): the source of the record
    """
    if not source:
        return

    if current_app.config.get('FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP'):
        inspirehep_url = current_app.config.get("INSPIREHEP_URL")
        headers = _get_headers_for_hep_root_table_request()
        response = requests.post(
            "{inspirehep_url}/literature/workflows_record_sources".format(
                inspirehep_url=inspirehep_url
            ),
            headers=headers,
            data=json.dumps(
                {
                    "record_uuid": record_uuid,
                    "source": source.lower(),
                    "json": json_data,
                }
            ),
        )
        if response.status_code != 200:
            LOGGER.error(
                "Failed to save head root for record {record_uuid} and source {source}!".format(
                    record_uuid=str(record_uuid), source=source
                )
            )
            raise WorkflowsError(
                "Error from inspirehep [{code}]: {message}".format(
                    code=response.status_code, message=response.json()
                )
            )
    else:
        source = get_source_for_root(source)
        record_source = read_wf_record_source(
            record_uuid=record_uuid, source=source)

        if record_source is None:
            record_source = WorkflowsRecordSources(
                source=source.lower(),
                json=json_data,
                record_uuid=record_uuid,
            )
            db.session.add(record_source)
        else:
            record_source.json = json_data
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
    return source if source in ["arxiv", "submitter"] else "publisher"


def get_resolve_validation_callback_url():
    """Resolve validation callback.
    Returns the callback url for resolving the validation errors.
    Note:
        It's using ``inspire_workflows.callback_resolve_validation``
        route.
    """
    return url_for(
        "inspire_workflows_callbacks.callback_resolve_validation", _external=True
    )


def get_resolve_merge_conflicts_callback_url():
    """Resolve validation callback.
    Returns the callback url for resolving the merge conflicts.
    Note:
        It's using ``inspire_workflows.callback_resolve_merge_conflicts``
        route.
    """
    return url_for(
        "inspire_workflows_callbacks.callback_resolve_merge_conflicts", _external=True
    )


def get_resolve_edit_article_callback_url():
    """Resolve edit_article workflow letting it continue.
    Note:
        It's using ``inspire_workflows.callback_resolve_edit_article``
        route.
    """
    return url_for(
        "inspire_workflows_callbacks.callback_resolve_edit_article", _external=True
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
            "path": map(text_type, error.absolute_path),
            "message": text_type(error.message),
        }
        for error in errors
    ]
    return error_messages


def _get_headers_for_hep():
    return {
        "accept": "application/vnd+inspire.record.raw+json",
        "content-type": "application/json",
        "Authorization": "Bearer {token}".format(
            token=current_app.config["AUTHENTICATION_TOKEN"]
        ),
    }


def _get_headers_for_hep_root_table_request():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer {token}".format(
            token=current_app.config["AUTHENTICATION_TOKEN"]
        ),
    }


@backoff.on_exception(
    backoff.expo, (requests.exceptions.ConnectionError), base=4, max_tries=5
)
def get_record_from_hep(pid_type, pid_value):
    endpoint = get_endpoint_from_pid_type(pid_type)
    inspirehep_url = current_app.config.get("INSPIREHEP_URL")
    headers = _get_headers_for_hep()
    response = requests.get(
        "{inspirehep_url}/{endpoint}/{control_number}".format(
            inspirehep_url=inspirehep_url, endpoint=endpoint, control_number=pid_value
        ),
        headers=headers,
    )
    response.raise_for_status()
    record_data = response.json()
    if not record_data or "metadata" not in record_data:
        raise MissingInspireRecordError
    if "uuid" not in record_data or "revision_id" not in record_data:
        raise MissingUUIDOrRevisionInHEPResponse

    return record_data


@backoff.on_exception(
    backoff.expo, (requests.exceptions.ConnectionError), base=4, max_tries=5
)
def put_record_to_hep(pid_type, pid_value, data=None, headers=None):
    if not data:
        raise InspirehepMissingDataError

    data.pop("_files", None)

    _headers = _get_headers_for_hep()
    if headers:
        _headers.update(headers)

    endpoint = get_endpoint_from_pid_type(pid_type)
    inspirehep_url = current_app.config.get("INSPIREHEP_URL")
    response = requests.put(
        "{inspirehep_url}/{endpoint}/{control_number}".format(
            inspirehep_url=inspirehep_url, endpoint=endpoint, control_number=pid_value
        ),
        headers=_headers,
        json=data or {},
    )
    response.raise_for_status()
    return response.json()


@backoff.on_exception(
    backoff.expo, (requests.exceptions.ConnectionError), base=4, max_tries=5
)
def post_record_to_hep(pid_type, data=None, headers=None):
    if not data:
        raise InspirehepMissingDataError

    data.pop("_files", None)

    _headers = _get_headers_for_hep()
    if headers:
        _headers.update(headers)
    endpoint = get_endpoint_from_pid_type(pid_type)
    inspirehep_url = current_app.config.get("INSPIREHEP_URL")
    response = requests.post(
        "{inspirehep_url}/{endpoint}".format(
            inspirehep_url=inspirehep_url,
            endpoint=endpoint,
        ),
        headers=_headers,
        json=data or {},
    )
    response.raise_for_status()
    return response.json()


def set_mark(obj, key, value):
    obj.extra_data[key] = value
    return {key: value}


def check_mark(obj, key):
    return bool(obj.extra_data.get(key))


def get_mark(obj, key, default=None):
    return obj.extra_data.get(key) or default


@with_debug_logging
def store_head_version(obj, eng):
    control_number = obj.data["control_number"]
    pid_type = get_pid_type_from_schema(obj.data["$schema"])
    if current_app.config.get("FEATURE_FLAG_ENABLE_HEP_REST_RECORD_PULL"):
        record_data = get_record_from_hep(pid_type, control_number)
        head_uuid = record_data["uuid"]
        revision_id = record_data["revision_id"]
        head_version = revision_id + 1
    else:
        head_uuid = PersistentIdentifier.get(pid_type, control_number).object_uuid
        head_record = InspireRecord.get_record(head_uuid)
        head_version = head_record.model.version_id
    obj.extra_data["head_uuid"] = str(head_uuid)
    obj.extra_data["head_version_id"] = head_version
    obj.save()


def _get_hep_url_for_document(file_url):
    server_name = current_app.config.get("SERVER_NAME")
    protocol = current_app.config.get("PREFERRED_URL_SCHEME", 'http')
    return "{protocol}://{server_name}{file_url}".format(
        protocol=protocol,
        server_name=server_name,
        file_url=file_url
    )


def restart_workflow(obj, restarter_id=None, position=[0]):
    """Restarts workflow

    Args:
        obj: Workflow to restart
        original_workflow: Workflow which restarts
        position: To which position wf should be restarted
    """
    obj.callback_pos = position
    obj.status = ObjectStatus.RUNNING
    obj.extra_data['source_data']['extra_data'][
        'delay'] = current_app.config.get("TASK_DELAY_ON_START", 10)
    if restarter_id:
        obj.extra_data['source_data']['extra_data'].setdefault(
            'restarted-by-wf', []).append(restarter_id)
    obj.save()
    db.session.commit()
    obj.continue_workflow('restart_task', delayed=True)


def create_error(response):
    """Raises exception with message from data returned by the server in response object"""
    if response.status_code == 502:
        raise BadGatewayError()

    try:
        error_msg = response.json()
    except JSONDecodeError:
        error_msg = response.text
    raise WorkflowsError(
        "Error from inspirehep [{code}]: {message}".format(
            code=response.status_code, message=error_msg
        )
    )


def delete_empty_key(obj, key):
    if key in obj.data and len(obj.data[key]) == 0:
        LOGGER.info('Deleting %s from workflow. Key is empty.', key)
        del obj.data[key]
