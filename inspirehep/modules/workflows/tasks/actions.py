# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tasks related to user actions."""

from functools import wraps

from flask import current_app

from inspirehep.utils.arxiv import get_clean_arXiv_id
from inspirehep.utils.record import get_value


def mark(key, value):
    """Mark a record by putting a value in a key in extra_data."""
    @wraps(mark)
    def _mark(obj, eng):
        obj.extra_data[key] = value
    return _mark


def is_marked(key):
    """Mark a record by putting a value in a key in extra_data."""
    @wraps(mark)
    def _mark(obj, eng):
        return key in obj.extra_data and obj.extra_data[key]
    return _mark


def is_record_accepted(obj, *args, **kwargs):
    """Check if the record was approved."""
    return obj.extra_data.get("approved", False)


def shall_halt_workflow(obj, *args, **kwargs):
    """Check if the workflow shall be halted."""
    return obj.extra_data.get("halt_workflow", False)


def shall_push_remotely(*args, **kwargs):
    """Check if the record shall be robotuploaded."""
    # If in debug mode, we do remote uploads or
    # if LEGACY_ROBOTUPLOAD_URL is set
    return current_app.config.get(
        "LEGACY_ROBOTUPLOAD_URL", False
    )


def add_core(obj, eng):
    """Add CORE collection tag to collections, if asked for."""
    if obj.extra_data.get('core'):
        collections = obj.data.get("collections", [])
        # Do not add it again if already there
        has_core = [v for c in collections
                    for v in c.values()
                    if v and v.lower() == "core"]
        if not has_core:
            collections.append({"primary": "CORE"})
            obj.data["collections"] = collections


def halt_record(action=None, message=None):
    """Halt the workflow for approval with optional action."""
    @wraps(halt_record)
    def _halt_record(obj, eng):
        eng.halt(action=obj.extra_data.get("halt_action") or action,
                 msg=obj.extra_data.get("halt_message") or message)
    return _halt_record


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
    @wraps(reject_record)
    def _reject_record(obj, *args, **kwargs):
        from inspirehep.modules.workflows.utils import log_workflows_action

        prediction_results = obj.extra_data.get("relevance_prediction")
        log_workflows_action(
            action="reject_record",
            prediction_results=prediction_results,
            object_id=obj.id,
            user_id=0,
            source="workflow",
        )

        obj.extra_data["approved"] = False
        obj.extra_data["reason"] = message
        obj.log.info(message)
    return _reject_record


def is_record_relevant(obj, *args, **kwargs):
    """Shall we halt this workflow for potential acceptance or just reject?"""
    # We do not auto-reject any user submissions
    if is_submission(obj, *args, **kwargs):
        return True

    prediction_results = obj.extra_data.get("prediction_results")
    classification_results = obj.extra_data.get('classifier_results')

    if prediction_results and classification_results:
        score = prediction_results.get("max_score")
        decision = prediction_results.get("decision")
        classification_results = classification_results.get("complete_output")
        core_keywords = classification_results.get("Core keywords")
        if decision.lower() == "rejected" and score > 0 and \
                len(core_keywords) == 0:
            return False
    return True


def is_experimental_paper(obj, eng):
    """Check if the record is an experimental paper."""
    categories = list(get_value(obj.data, "arxiv_eprints.categories", [[]])[0]) + \
        list(get_value(obj.data, "field_categories.term", []))
    categories_to_check = [
        "hep-ex", "nucl-ex", "astro-ph", "astro-ph.IM", "astro-ph.CO",
        "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.SR",
        "physics.ins-det",
        "Experiment-HEP", "Experiment-Nucl", "Astrophysics", "Instrumentation"
    ]
    for experimental_category in categories_to_check:
        if experimental_category in categories:
            return True
    return False


def is_arxiv_paper(obj, *args, **kwargs):
    """Check if the record is from arXiv."""
    return bool(get_value(obj.data, "arxiv_eprints.categories", [[]])[0]) or \
        get_clean_arXiv_id(obj.data)


def is_submission(obj, eng):
    """Is this a submission?"""
    source = obj.data.get('acquisition_source')
    if source:
        return source.get('method') == "submission"
    return False


def emit_record_signals(obj, eng):
    """Emit record signals to update record metadata."""
    from invenio_records.signals import before_record_insert

    before_record_insert.send(obj.data)


def prepare_update_payload(extra_data_key="update_payload"):
    @wraps(prepare_update_payload)
    def _prepare_update_payload(obj, eng):
        # TODO: Perform auto-merge if possible and update only necessary data
        # See obj.extra_data["record_matches"] for data on matches

        # FIXME: Just update entire record for now
        obj.extra_data[extra_data_key] = obj.data
    return _prepare_update_payload
