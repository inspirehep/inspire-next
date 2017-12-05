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
from invenio_workflows import workflow_object_class

from inspire_matcher.api import match
from inspire_utils.dedupers import dedupe_list
from inspirehep.utils.datefilter import date_older_than
from inspirehep.utils.record import get_arxiv_categories, get_arxiv_id

from ..utils import with_debug_logging


@with_debug_logging
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
def article_exists(obj, eng):
    """Return ``True`` if the record is already present in the system.

    Uses the default configuration of the ``inspire-matcher`` to find
    duplicates of the current workflow object in the system.

    Also sets the ``record_matches`` property in ``extra_data`` to the list of
    control numbers that matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the system
        ``False`` otherwise.

    """
    matches = dedupe_list(match(obj.data))
    record_ids = [el['_source']['control_number'] for el in matches]
    if record_ids:
        obj.extra_data['record_matches'] = record_ids
        return True

    obj.extra_data['record_matches'] = []
    return False


@with_debug_logging
def is_being_harvested_on_legacy(record):
    """Return True if the record is being harvested on Legacy.

    If the record belongs to one of the CORE arXiv categories then it
    is already being harvested on Legacy.
    """
    arxiv_categories = get_arxiv_categories(record)
    legacy_categories = current_app.config.get(
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY', [])

    return len(set(arxiv_categories) & set(legacy_categories)) > 0


@with_debug_logging
def already_harvested(obj, eng):
    """Check if record is already harvested."""
    if is_being_harvested_on_legacy(obj.data):
        obj.log.info((
            'Record with arXiv id {arxiv_id} is'
            ' already being harvested on Legacy.'
        ).format(arxiv_id=get_arxiv_id(obj.data)))
        return True

    return False


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


@with_debug_logging
def pending_in_holding_pen(obj, eng):
    """Return ``True`` if the record is already present in the Holding Pen.

    Uses a custom configuration of the ``inspire-matcher`` to find duplicates
    of the current workflow object in the Holding Pen.

    Also sets ``holdingpen_matches`` in ``extra_data`` to the list of ids that
    matched.

    Arguments:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: ``True`` if the workflow object has a duplicate in the Holding
        Pen, ``False`` otherwise.

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
            },
        ],
        'doc_type': 'hep',
        'index': 'holdingpen-hep',
    }

    matches = dedupe_list(match(obj.data, config))
    holdingpen_ids = [int(el['_id']) for el in matches if int(el['_id']) != obj.id]
    if holdingpen_ids:
        obj.extra_data['holdingpen_matches'] = holdingpen_ids
        return True

    obj.extra_data['holdingpen_matches'] = []
    return False


@with_debug_logging
def delete_self_and_stop_processing(obj, eng):
    """Delete both versions of itself and stops the workflow."""
    db.session.delete(obj.model)
    eng.skip_token()


@with_debug_logging
def stop_processing(obj, eng):
    """Stop processing for object and return as completed."""
    eng.stopProcessing()


@with_debug_logging
def update_existing_workflow_object(obj, eng):
    """Update the data of the old object with the new data."""
    holdingpen_ids = obj.extra_data.get('holdingpen_matches', [])

    if not holdingpen_ids:
        return

    for matched_id in holdingpen_ids:
        existing_obj = workflow_object_class.get(matched_id)
        if (
                obj.data.get('acquisition_source') and
                existing_obj.data.get('acquisition_source')
        ):
            if (
                    obj.data['acquisition_source'].get('method') ==
                    existing_obj.data['acquisition_source'].get('method')
            ):
                # Method is the same, update obj
                existing_obj.data.update(obj.data)
                existing_obj.save()
                break
    else:
        msg = "Cannot update old object, non valid ids: %s"
        obj.log.error(msg, holdingpen_ids)
        raise Exception(msg % holdingpen_ids)
