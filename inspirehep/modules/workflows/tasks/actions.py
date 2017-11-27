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

"""Tasks related to user actions."""

from __future__ import absolute_import, division, print_function

import os
from functools import wraps

from flask import current_app
from werkzeug import secure_filename
from timeout_decorator import TimeoutError

from inspire_schemas.builders import LiteratureBuilder
from inspire_utils.record import get_value
from inspirehep.modules.workflows.utils import (
    get_pdf_in_workflow,
    log_workflows_action,
)
from inspirehep.utils.record import get_arxiv_id
from inspirehep.utils.url import is_pdf_link

from inspirehep.modules.workflows.tasks.refextract import (
    extract_references_from_pdf,
    extract_references_from_text,
)
from inspirehep.modules.workflows.utils import (
    download_file_to_workflow,
    with_debug_logging,
)


def mark(key, value):
    """Mark the workflow object by putting a value in a key in extra_data."""
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        obj.extra_data[key] = value

    _mark.__doc__ = 'Mark the workflow object with %s:%s.' % (key, value)
    return _mark


def is_marked(key):
    """Check if the workflow object has a specific mark."""
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        return key in obj.extra_data and obj.extra_data[key]

    _mark.__doc__ = 'Check if the workflow object has the mark %s.' % key
    return _mark


@with_debug_logging
def is_record_accepted(obj, *args, **kwargs):
    """Check if the record was approved."""
    return obj.extra_data.get("approved", False)


@with_debug_logging
def shall_halt_workflow(obj, *args, **kwargs):
    """Check if the workflow shall be halted."""
    return obj.extra_data.get("halt_workflow", False)


def in_production_mode(*args, **kwargs):
    """Check if we are in production mode"""
    return current_app.config.get(
        "PRODUCTION_MODE", False
    )


@with_debug_logging
def add_core(obj, eng):
    """Mark a record as CORE if it was approved as CORE."""
    if 'core' in obj.extra_data:
        obj.data['core'] = obj.extra_data['core']


def halt_record(action=None, message=None):
    """Halt the workflow for approval with optional action."""
    @with_debug_logging
    @wraps(halt_record)
    def _halt_record(obj, eng):
        eng.halt(
            action=obj.extra_data.get("halt_action") or action,
            msg=obj.extra_data.get("halt_message") or message,
        )

    _halt_record.__doc__ = (
        'Halt the workflow object, action=%s, message=%s' % (action, message)
    )
    _halt_record.description = '"%s"' % (message or 'unspecified')
    return _halt_record


def reject_record(message):
    """Reject record with message."""
    @with_debug_logging
    @wraps(reject_record)
    def _reject_record(obj, *args, **kwargs):
        relevance_prediction = obj.extra_data.get("relevance_prediction")
        log_workflows_action(
            action="reject_record",
            relevance_prediction=relevance_prediction,
            object_id=obj.id,
            user_id=None,
            source="workflow",
        )

        obj.extra_data["approved"] = False
        obj.extra_data["reason"] = message
        obj.log.info(message)

    _reject_record.__doc__ = 'Reject the record, message=%s' % message
    return _reject_record


def _is_auto_rejected(workflow_obj):
    relevance_prediction = workflow_obj.extra_data.get('relevance_prediction')
    classification_results = workflow_obj.extra_data.get('classifier_results')
    if not relevance_prediction or not classification_results:
        return False

    decision = relevance_prediction.get('decision')
    all_class_results = classification_results.get('complete_output')
    core_keywords = all_class_results.get('core_keywords')

    return decision.lower() == 'rejected' and len(core_keywords) == 0


@with_debug_logging
def is_record_relevant(obj, eng):
    """Shall we halt this workflow for potential acceptance or just reject?"""

    # We do not auto-reject any user submissions
    if is_submission(obj, eng):
        return True

    if _is_auto_rejected(workflow_obj=obj):
        return False

    return True


@with_debug_logging
def is_experimental_paper(obj, eng):
    """Check if the record is an experimental paper."""
    categories = list(
        get_value(obj.data, "arxiv_eprints.categories", [[]])[0]
    ) + list(get_value(obj.data, "inspire_categories.term", []))

    categories_to_check = [
        "hep-ex", "nucl-ex", "astro-ph", "astro-ph.IM", "astro-ph.CO",
        "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.SR",
        "physics.ins-det", "Experiment-HEP", "Experiment-Nucl",
        "Astrophysics", "Instrumentation"
    ]
    for experimental_category in categories_to_check:
        if experimental_category in categories:
            return True

    return False


@with_debug_logging
def is_arxiv_paper(obj, *args, **kwargs):
    """Check if the record is from arXiv."""
    arxiv_id = get_arxiv_id(obj.data)
    categories = get_value(obj.data, 'arxiv_eprints.categories')

    if arxiv_id or categories:
        return True
    return False


@with_debug_logging
def is_submission(obj, eng):
    """Is this a submission?"""
    source = obj.data.get('acquisition_source')
    if source:
        return source.get('method') == "submitter"
    return False


@with_debug_logging
def submission_fulltext_download(obj, eng):
    submission_pdf = obj.extra_data.get('submission_pdf')
    if submission_pdf and is_pdf_link(submission_pdf):
        filename = secure_filename('fulltext.pdf')
        pdf = download_file_to_workflow(
            workflow=obj,
            name=filename,
            url=submission_pdf,
        )

        if pdf:
            obj.data['documents'] = [
                document for document in obj.data.get('documents', ())
                if document.get('key') != filename
            ]
            lb = LiteratureBuilder(source=obj.data['acquisition_source']['source'], record=obj.data)
            lb.add_document(
                filename,
                fulltext=True,
                original_url=submission_pdf,
                url='/api/files/{bucket}/{key}'.format(bucket=obj.files[filename].bucket_id, key=filename)
            )
            obj.data = lb.record
            obj.log.info('PDF provided by user from %s', submission_pdf)
            return obj.files[filename].file.uri
        else:
            obj.log.info('Cannot fetch PDF provided by user from %s', submission_pdf)


def prepare_update_payload(extra_data_key="update_payload"):
    @with_debug_logging
    @wraps(prepare_update_payload)
    def _prepare_update_payload(obj, eng):
        # TODO: Perform auto-merge if possible and update only necessary data
        # See obj.extra_data["record_matches"] for data on matches

        # FIXME: Just update entire record for now
        obj.extra_data[extra_data_key] = obj.data

    _prepare_update_payload.__doc__ = (
        'Prepare the update payload, extra_data_key=%s.' % extra_data_key)
    return _prepare_update_payload


@with_debug_logging
def refextract(obj, eng):
    """Extract references from various sources and add them to the workflow.

    Runs ``refextract`` on both the PDF attached to the workflow and the
    references provided by the submitter, if any, then chooses the one
    that generated the most and attaches them to the workflow object.

    Note:
        We might want to compare the number of *matched* references instead.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    pdf_references, text_references = [], []
    source = get_value(obj.data, 'acquisition_source.source')

    tmp_pdf = get_pdf_in_workflow(obj)
    if tmp_pdf:
        try:
            pdf_references = extract_references_from_pdf(tmp_pdf, source)
        except TimeoutError:
            obj.log.error('Timeout when extracting references from PDF.')
        finally:
            if os.path.exists(tmp_pdf):
                os.unlink(tmp_pdf)

    text = get_value(obj.extra_data, 'formdata.references')
    if text:
        try:
            text_references = extract_references_from_text(text, source)
        except TimeoutError:
            obj.log.error('Timeout when extracting references from text.')

    if len(pdf_references) == len(text_references) == 0:
        obj.log.info('No references extracted.')
    elif len(pdf_references) >= len(text_references):
        obj.log.info('Extracted %d references from PDF.', len(pdf_references))
        obj.data['references'] = pdf_references
    elif len(text_references) > len(pdf_references):
        obj.log.info('Extracted %d references from text.', len(text_references))
        obj.data['references'] = text_references
