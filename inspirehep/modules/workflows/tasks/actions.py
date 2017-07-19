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

from functools import wraps

from flask import current_app
from werkzeug import secure_filename
from timeout_decorator import TimeoutError

from inspirehep.modules.workflows.utils import (
    get_pdf_in_workflow,
    log_workflows_action,
)
from inspirehep.utils.record import get_arxiv_id, get_value
from inspirehep.utils.url import is_pdf_link

from .refextract import extract_references
from ..utils import download_file_to_workflow, with_debug_logging


def mark(key, value):
    """Mark a record by putting a value in a key in extra_data."""
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        obj.extra_data[key] = value
    return _mark


def is_marked(key):
    """Mark a record by putting a value in a key in extra_data."""
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        return key in obj.extra_data and obj.extra_data[key]
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
        eng.halt(action=obj.extra_data.get("halt_action") or action,
                 msg=obj.extra_data.get("halt_message") or message)
    return _halt_record


@with_debug_logging
def update_note(metadata):
    """Check if the record was approved as CORE."""
    new_notes = []
    for note in metadata.get("public_notes", []):
        if note.get("value", "") == "*Brief entry*":
            note = {"value": "*Temporary entry*"}
        new_notes.append(note)
    if new_notes:
        metadata["public_notes"] = new_notes
    return metadata


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
    return _reject_record


def _is_auto_rejected(workflow_obj):
    relevance_prediction = workflow_obj.extra_data.get('relevance_prediction')
    classification_results = workflow_obj.extra_data.get('classifier_results')
    if not relevance_prediction or not classification_results:
        return False

    score = relevance_prediction.get('max_score')
    decision = relevance_prediction.get('decision')
    all_class_results = classification_results.get('complete_output')
    core_keywords = all_class_results.get('core_keywords')

    return (
        decision.lower() == 'rejected' and
        score > 0 and
        len(core_keywords) == 0
    )


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
    return _prepare_update_payload


@with_debug_logging
def refextract(obj, eng):
    uri = get_pdf_in_workflow(obj)
    if uri:
        try:
            journal_kb_path = current_app.config.get('REFEXTRACT_JOURNAL_KB_PATH', None)
            if journal_kb_path:
                mapped_references = extract_references(uri, {'journals': journal_kb_path})
            else:
                mapped_references = extract_references(uri)
            if mapped_references:
                obj.data['references'] = mapped_references
                obj.log.info('Extracted %d references', len(mapped_references))
            else:
                obj.log.info('No references extracted')
        except TimeoutError:
            obj.log.error('Timeout when extracting references from the PDF')
    else:
        obj.log.error('Not able to download and process the PDF')
