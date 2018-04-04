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

"""Tasks to check if the incoming record already exist."""

from __future__ import absolute_import, division, print_function

import datetime
from functools import wraps

from flask import current_app

from invenio_db import db
from invenio_workflows import workflow_object_class, WorkflowEngine

from inspire_matcher.api import match
from inspire_utils.dedupers import dedupe_list
from inspirehep.utils.datefilter import date_older_than
from inspirehep.utils.record import get_arxiv_categories, get_value
from inspirehep.modules.workflows.tasks.actions import mark

from ..utils import with_debug_logging


def is_too_old(record, days_ago=5):
    """Return True if the record is more than days_ago days old.

    If the record is older then it's probably an update of an earlier
    record, and we don't want those.
    """
    date_format = "%Y-%m-%d"
    earliest_date = record.get('earliest_date', '')
    if not earliest_date:
        earliest_date = record.get('preprint_date', '')

    if earliest_date:
        try:
            parsed_date = datetime.datetime.strptime(
                earliest_date,
                date_format,
            )

        except ValueError as err:
            raise ValueError(
                (
                    'Unrecognized earliest_date format "%s", valid formats is '
                    '%s: %s'
                ) % (earliest_date, date_format, err)
            )

        if not date_older_than(
            parsed_date,
            datetime.datetime.utcnow(),
            days=days_ago,
        ):
            return False
    return True


@with_debug_logging
def exact_match(obj, eng):
    """Return ``True`` if the record is already present in the system.

    Uses the default configuration of the ``inspire-matcher`` to find
    duplicates of the current workflow object in the system.

    Also sets the ``matches.exact`` property in ``extra_data`` to the list of
    control numbers that matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the system
        ``False`` otherwise.

    """
    exact_match_config = current_app.config['EXACT_MATCH']
    matches = dedupe_list(match(obj.data, exact_match_config))
    record_ids = [el['_source']['control_number'] for el in matches]
    obj.extra_data.setdefault('matches', {})['exact'] = record_ids
    return bool(record_ids)


@with_debug_logging
def fuzzy_match(obj, eng):
    """Return ``True`` if a similar record is found in the system.

    Uses a custom configuration for ``inspire-matcher`` to find records
    similar to the current workflow object's payload in the system.

    Also sets the ``matches.fuzzy`` property in ``extra_data`` to the list of
    the brief of first 5 record that matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the system
        ``False`` otherwise.

    """
    if not current_app.config.get('FEATURE_FLAG_ENABLE_FUZZY_MATCHER'):
        return False

    fuzzy_match_config = current_app.config['FUZZY_MATCH']
    matches = dedupe_list(match(obj.data, fuzzy_match_config))
    record_ids = [_get_hep_record_brief(el['_source']) for el in matches]
    obj.extra_data.setdefault('matches', {})['fuzzy'] = record_ids[0:5]
    return bool(record_ids)


def _get_hep_record_brief(hep_record):
    brief = {
        'control_number': hep_record['control_number'],
        'title': get_value(hep_record, 'titles[0].title'),
    }

    abstract = get_value(hep_record, 'abstracts[0].value')
    if abstract is not None:
        brief['abstract'] = abstract

    authors = hep_record.get('authors')
    if authors is not None:
        author_briefs = []
        for author in authors[:3]:
            author_briefs.append({'full_name': author['full_name']})
        brief['authors'] = author_briefs
    return brief


@with_debug_logging
def is_fuzzy_match_approved(obj, eng):
    """Check if a fuzzy match has been approved by a human."""
    return obj.extra_data.get('fuzzy_match_approved_id')


@with_debug_logging
def set_fuzzy_match_approved_in_extradata(obj, eng):
    """Set the human approved match in `matches.approved` in extra_data."""
    approved_match = obj.extra_data.get('fuzzy_match_approved_id')
    obj.extra_data.setdefault('matches', {})['approved'] = approved_match


@with_debug_logging
def set_exact_match_as_approved_in_extradata(obj, eng):
    """Set the best match in `matches.approved` in extra_data."""
    best_match = obj.extra_data['matches']['exact'][0]
    obj.extra_data.setdefault('matches', {})['approved'] = best_match


def auto_approve(obj, eng):
    """Check if auto approve the current ingested article.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Return:
        bool: True when the record belongs to an arXiv category that is fully
        harvested or if the primary category is `physics.data-an`, otherwise
        False.
    """
    return has_fully_harvested_category(obj.data) or physics_data_an_is_primary_category(obj.data)


def has_fully_harvested_category(record):
    """Check if the record in `obj.data` has fully harvested categories.

    Arguments:
        record(dict): the ingested article.

    Return:
        bool: True when the record belongs to an arXiv category that is fully
        harvested, otherwise False.
    """
    record_categories = set(get_arxiv_categories(record))
    harvested_categories = current_app.config.get('ARXIV_CATEGORIES', {})
    return len(
        record_categories &
        set(
            harvested_categories.get('core') +
            harvested_categories.get('non-core')
        )
    ) > 0


def physics_data_an_is_primary_category(record):
    record_categories = get_arxiv_categories(record)
    if record_categories:
        return record_categories[0] == 'physics.data-an'
    return False


@with_debug_logging
def set_core_in_extra_data(obj, eng):
    """Set `core=True` in `obj.extra_data` if the record belongs to a core arXiv category"""
    def _is_core(record):
        return set(get_arxiv_categories(record)) & \
            set(current_app.config.get('ARXIV_CATEGORIES', {}).get('core'))

    if _is_core(obj.data):
        obj.extra_data['core'] = True


def previously_rejected(days_ago=None):
    """Check if record exist on INSPIRE or already rejected."""
    @with_debug_logging
    @wraps(previously_rejected)
    def _previously_rejected(obj, eng):
        if days_ago is None:
            _days_ago = current_app.config.get('INSPIRE_ACCEPTANCE_TIMEOUT', 5)
        else:
            _days_ago = days_ago

        if is_too_old(obj.data, days_ago=_days_ago):
            obj.log.info("Record is likely rejected previously.")
            return True

        return False

    return _previously_rejected


def match_non_completed_wf_in_holdingpen(obj, eng):
    """Return ``True`` if a matching wf is processing in the HoldingPen.

    Uses a custom configuration of the ``inspire-matcher`` to find duplicates
    of the current workflow object in the Holding Pen not in the
    COMPLETED state.

    Also sets ``holdingpen_matches`` in ``extra_data`` to the list of ids that
    matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the Holding
        Pen that is not COMPLETED, ``False`` otherwise.

    """
    def _non_completed(base_record, match_result):
        return not get_value(match_result, '_source._workflow.status') == 'COMPLETED'

    matched_ids = pending_in_holding_pen(obj, _non_completed)
    obj.extra_data['holdingpen_matches'] = matched_ids
    return bool(matched_ids)


def match_previously_rejected_wf_in_holdingpen(obj, eng):
    """Return ``True`` if matches a COMPLETED and rejected wf in the HoldingPen.

    Uses a custom configuration of the ``inspire-matcher`` to find duplicates
    of the current workflow object in the Holding Pen in the
    COMPLETED state, marked as ``approved = False``.

    Also sets ``holdingpen_matches`` in ``extra_data`` to the list of ids that
    matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the Holding
        Pen that is not COMPLETED, ``False`` otherwise.

    """
    def _rejected_and_completed(base_record, match_result):
        return get_value(match_result, '_source._workflow.status') == 'COMPLETED' and \
            get_value(match_result, '_source._extra_data.approved') is False

    matched_ids = pending_in_holding_pen(obj, _rejected_and_completed)
    obj.extra_data['previously_rejected_matches'] = matched_ids
    return bool(matched_ids)


@with_debug_logging
def pending_in_holding_pen(obj, validation_func):
    """Return the list of matching workflows in the holdingpen.

    Matches the holdingpen records by their ``arxiv_eprint``, their ``doi``,
    and by a custom validator function.

    Args:
        obj: a workflow object.
        validation_func: a function used to filter the matched records.

    Returns:
        (list): the ids matching the current ``obj`` that satisfy
        ``validation_func``.

    """
    config = {
        'algorithm': [
            {
                'queries': [
                    {
                        'path': 'arxiv_eprints.value',
                        'search_path': 'metadata.arxiv_eprints.value.raw',
                        'type': 'exact',
                    },
                    {
                        'path': 'dois.value',
                        'search_path': 'metadata.dois.value.raw',
                        'type': 'exact',
                    },
                ],
                'validator': validation_func,
            },
        ],
        'doc_type': 'hep',
        'index': 'holdingpen-hep',
    }
    matches = dedupe_list(match(obj.data, config))
    return [int(el['_id']) for el in matches if int(el['_id']) != obj.id]


@with_debug_logging
def delete_self_and_stop_processing(obj, eng):
    """Delete both versions of itself and stops the workflow."""
    db.session.delete(obj.model)
    eng.skip_token()


@with_debug_logging
def stop_processing(obj, eng):
    """Stop processing the given workflow.

    Stops the given workflow engine. This causes the stop of all the workflows
    related to it.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    eng.stop()


def has_same_source(extra_data_key):
    """Match a workflow in obj.extra_data[`extra_data_key`] by the source.

    Takes a list of workflows from extra_data using as key `extra_data_key`
    and goes through them checking if at least one workflow has the same source
    of the current workflow object.

    Args:
        extra_data_key: the key to retrieve a workflow list from the current
        workflow object.

    Returns:
        bool: True if a workflow, whose id is in obj.extra_data[
        `extra_data_key`], matches the current workflow by the source.
    """

    def _get_wfs_same_source(obj, eng):
        current_source = get_value(obj.data, 'acquisition_source.source').lower()

        try:
            workflows = obj.extra_data[extra_data_key]
        except KeyError:
            workflows = []

        for wf_id in workflows:
            wf = workflow_object_class.get(wf_id)
            wf_source = get_value(wf.data, 'acquisition_source.source').lower()
            if wf_source == current_source:
                return True
        return False

    return _get_wfs_same_source


def stop_matched_holdingpen_wfs(obj, eng):
    """Stop the matched workflow objects in the holdingpen.

    Stops the matched workflows in the holdingpen by replacing their steps with
    a new one defined on the fly, containing a ``stop`` step, and executing it.
    For traceability reason, these workflows are also marked as
    ``'stopped-by-wf'``, whose value is the current workflow's id.

    In the use case of harvesting twice an article, this function is involved
    to stop the first workflow and let the current one being processed,
    since it the latest metadata.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    stopping_steps = [mark('stopped-by-wf', int(obj.id)), stop_processing]

    obj.save()

    for holdingpen_wf_id in obj.extra_data['holdingpen_matches']:
        holdingpen_wf = workflow_object_class.get(holdingpen_wf_id)
        holdingpen_wf_eng = WorkflowEngine.from_uuid(holdingpen_wf.id_workflow)

        # stop this holdingpen workflow by replacing its steps with a stop step
        holdingpen_wf_eng.callbacks.replace(stopping_steps)
        holdingpen_wf_eng.process([holdingpen_wf])
