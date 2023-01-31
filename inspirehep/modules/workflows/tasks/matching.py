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

from flask import current_app

from inspire_schemas.readers import LiteratureReader
from inspire_utils.record import get_value
from invenio_db import db
from invenio_workflows import workflow_object_class, WorkflowEngine, \
    ObjectStatus
from invenio_workflows.errors import WorkflowsError, HaltProcessing
import re

from inspire_matcher.api import match
from inspire_utils.dedupers import dedupe_list
from inspirehep.utils.url import get_hep_url_for_recid
from inspirehep.modules.workflows.tasks.actions import mark, save_workflow
from inspirehep.modules.workflows.utils import restart_workflow
from copy import deepcopy, copy

from ..utils import with_debug_logging


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
    math_ml_latex_regex = r"(<math(.*?)<\/math>|(?<!\\)\$.*?(?<!\\)\$|(?<!\\)\\(.*?(?<!\\)\\)|(?<!\\)\\[.*?(?<!\\)\\])"
    fuzzy_match_config = current_app.config['FUZZY_MATCH']
    obj_data_without_math_ml_latex = copy(obj.data)
    if "abstracts" in obj.data:
        abstract_dup = deepcopy(obj.data["abstracts"])
        for abstract in abstract_dup:
            abstract['value'] = re.sub(math_ml_latex_regex, '', abstract['value'])
        obj_data_without_math_ml_latex["abstracts"] = abstract_dup
    matches = dedupe_list(match(obj_data_without_math_ml_latex, fuzzy_match_config))
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

    arxiv_eprint = get_value(hep_record, 'arxiv_eprints[0].value')
    if arxiv_eprint is not None:
        brief['arxiv_eprint'] = arxiv_eprint

    number_of_pages = get_value(hep_record, 'number_of_pages')
    if number_of_pages is not None:
        brief['number_of_pages'] = number_of_pages

    earliest_date = get_value(hep_record, 'earliest_date')
    if earliest_date is not None:
        brief['earliest_date'] = earliest_date

    authors = hep_record.get('authors')
    if authors is not None:
        brief['authors_count'] = len(authors)
        author_briefs = []
        for author in authors[:3]:
            author_briefs.append({'full_name': author['full_name']})
        brief['authors'] = author_briefs

    public_notes = hep_record.get('public_notes')
    if public_notes is not None:
        public_notes_value = []
        for public_note in public_notes:
            public_notes_value.append({'value': public_note['value']})
        brief['public_notes'] = public_notes_value

    publication_info = hep_record.get('publication_info')
    if publication_info is not None:
        brief['publication_info'] = publication_info

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
    return has_fully_harvested_category(obj.data) or \
        physics_data_an_is_primary_category(obj.data)


def has_fully_harvested_category(record):
    """Check if the record in `obj.data` has fully harvested categories.

    Arguments:
        record(dict): the ingested article.

    Return:
        bool: True when the record belongs to an arXiv category that is fully
        harvested, otherwise False.
    """
    record_categories = set(LiteratureReader(record).arxiv_categories)
    harvested_categories = current_app.config.get('ARXIV_CATEGORIES', {})
    return len(
        record_categories &
        set(
            harvested_categories.get('core') +
            harvested_categories.get('non-core')
        )
    ) > 0


def physics_data_an_is_primary_category(record):
    record_categories = LiteratureReader(record).arxiv_categories
    if record_categories:
        return record_categories[0] == 'physics.data-an'
    return False


def _is_first_category_core(record):
    record_core_category = LiteratureReader(record).arxiv_categories[0]
    arxiv_core_categories = set(current_app.config.get('ARXIV_CATEGORIES', {}).get('core', []))
    return record_core_category in arxiv_core_categories


def is_second_category_core(record):
    record_core_categories = LiteratureReader(record).arxiv_categories[1:]
    return set(record_core_categories) & \
        set(current_app.config.get('ARXIV_CATEGORIES', {}).get('core'))


@with_debug_logging
def set_core_in_extra_data(obj, eng):
    """Set `core=True` in `obj.extra_data` if the record belongs to a core arXiv category"""
    if _is_first_category_core(obj.data):
        obj.extra_data['core'] = True


def check_if_secondary_categories_are_core(obj, eng):
    return is_second_category_core(obj.data)


def set_wf_not_completed_ids_to_wf(obj, skip_blocked=True, skip_halted=False):
    """Return list of all matched workflows ids which are not completed
    also stores this list to wf.extra_data['holdingpen_matches']
    By default it do not show workflows which are already blocked by this workflow

    Arguments:
        obj: a workflow object.
        skip_blocked: boolean, if True do not returnd workflows blocked by this one,
            if False then return all matched workflows.
        skip_halted: boolean, if True, then it skips HALTED workflows when
            looking for matched workflows
    """
    def _accept_only_article_wf(base_record, match_result):
        return get_value(match_result, '_source._workflow.workflow_class') == "article"

    def _non_completed(base_record, match_result):
        return get_value(match_result, '_source._workflow.status') != 'COMPLETED' \
            and _accept_only_article_wf(base_record, match_result)

    def _not_completed_or_halted(base_record, match_result):
        return get_value(match_result, '_source._workflow.status') not in [
            'COMPLETED', 'HALTED'] and _accept_only_article_wf(base_record, match_result)

    def is_workflow_blocked_by_another_workflow(workflow_id):
        workflow = workflow_object_class.get(workflow_id)
        return obj.id in workflow.extra_data.get('holdingpen_matches', [])

    if skip_halted:
        matched_ids = pending_in_holding_pen(obj, _not_completed_or_halted)
    else:
        matched_ids = pending_in_holding_pen(obj, _non_completed)

    if skip_blocked:
        matched_ids = [_id for _id in matched_ids if
                       not is_workflow_blocked_by_another_workflow(_id)]
    obj.extra_data['holdingpen_matches'] = matched_ids
    save_workflow(obj, None)
    return matched_ids


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
    matched_ids = set_wf_not_completed_ids_to_wf(obj)
    return bool(matched_ids)


def raise_if_match_workflow(obj, eng):
    """Raise if a matching wf is not in completed state in the HoldingPen.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    matched_ids = set_wf_not_completed_ids_to_wf(
        obj,
        skip_blocked=True,
        skip_halted=True
    )
    if bool(matched_ids):
        urls = ["<a href='{0}' target='_blank'>{1}</a>".format(get_hep_url_for_recid(id, 'holdingpen'), id) for id in matched_ids]

        raise WorkflowsError(
            'Cannot continue processing workflow {wf_id}. '
            'Found not-completed workflows in holdingpen'
            ': {blocking_ids}'.format(
                wf_id=obj.id,
                blocking_ids=urls)
        )


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
        current_source = get_value(
            obj.data,
            'acquisition_source.source'
        ).lower()

        try:
            workflows = obj.extra_data[extra_data_key]
        except KeyError:
            workflows = []

        for wf_id in workflows:
            wf = workflow_object_class.get(wf_id)
            if _has_same_source(current_source, wf):
                return True
        return False

    return _get_wfs_same_source


def _has_same_source(current_wf_source, holdingpen_match_wf):
    wf_source = get_value(holdingpen_match_wf.data, 'acquisition_source.source').lower()
    if wf_source == current_wf_source.lower():
        return True


def _halt_record_if_match_from_different_source(holdingpen_wf_eng, holdingpen_wf):
    try:
        holdingpen_wf_eng.halt(msg="Waiting for matched worfklow to finish")
    except HaltProcessing:
        holdingpen_wf.status = ObjectStatus.HALTED
        holdingpen_wf.extra_data['halted-by-match-with-different-source'] = True
        holdingpen_wf_eng.save()
        holdingpen_wf.save()


def handle_matched_holdingpen_wfs(obj, eng):
    """Stop the matched workflow objects in the holdingpen.

    Stops the matched workflows with the same source in the holdingpen by replacing their steps with
    a new one defined on the fly, containing a ``stop`` step, and executing it.
    Workflows that have different source are being halted.
    For traceability reason, stopped workflows are also marked as
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
    save_workflow(obj, eng)
    current_wf_source = get_value(obj.data, 'acquisition_source.source')
    stopping_steps = [mark('stopped-by-wf', int(obj.id)), stop_processing]
    for holdingpen_wf_id in obj.extra_data['holdingpen_matches']:
        holdingpen_wf = workflow_object_class.get(holdingpen_wf_id)
        holdingpen_wf_eng = WorkflowEngine.from_uuid(holdingpen_wf.id_workflow)

        # halt workflow
        if not _has_same_source(current_wf_source, holdingpen_wf):
            _halt_record_if_match_from_different_source(holdingpen_wf_eng, holdingpen_wf)
            continue

        # stop this holdingpen workflow by replacing its steps with a stop step
        holdingpen_wf_eng.callbacks.replace(stopping_steps)
        holdingpen_wf_eng.process([holdingpen_wf])


@with_debug_logging
def has_more_than_one_exact_match(obj, eng):
    """Does the record have more than one exact match."""
    exact_matches = obj.extra_data['matches']['exact']
    return len(set(exact_matches)) > 1


@with_debug_logging
def run_next_if_necessary(obj, eng):
    """Remove current wf id from matched workflows and run next one"""
    blocked_wfs = set_wf_not_completed_ids_to_wf(obj, skip_blocked=False)
    next_wf = None
    for wf_id in blocked_wfs:
        wf = workflow_object_class.get(wf_id)
        if obj.id in wf.extra_data.get('holdingpen_matches', []):
            wf.extra_data['holdingpen_matches'].remove(obj.id)
            save_workflow(wf, eng)
        if not wf.extra_data.get('holdingpen_matches', []) and not next_wf:
            # If workflow is not blocked by any other workflow
            # And there is no next workflow set
            # then set is as next to restart
            next_wf = wf
    if next_wf:
        restart_workflow(next_wf, obj.id)
