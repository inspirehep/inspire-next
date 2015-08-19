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

"""Contains task to check if incoming record already exist."""

import os
import requests
import traceback
import datetime

from flask import current_app

from functools import wraps

from invenio.base.globals import cfg
from invenio.modules.deposit.models import Deposition

from inspire.modules.oaiharvester.tasks.arxiv import get_arxiv_id_from_record

from inspire.utils.datefilter import date_older_than
from inspire.utils.helpers import get_record_from_model, \
    get_record_from_obj


# TODO(jacquerie): fix test for perform_request.
def search(query):
    """TODO."""
    params = dict(p=query, of='id')

    try:
        return requests.get(cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"], params=params).json()
    except requests.ConnectionError:
        current_app.logger.error("Error connecting to remote server:\n {0}".format(
            traceback.format_exc()
        ))
        raise
    except ValueError:
        current_app.logger.error("Error decoding results from remote server:\n {0}".format(
            traceback.format_exc()
        ))
        raise


def match_by_arxiv_id(record):
    """TODO."""
    arxiv_id = get_arxiv_id_from_record(record)

    if arxiv_id:
        arxiv_id = arxiv_id.lower().replace('arxiv:', '')
        query = '035:"arXiv.org:{0}"'.format(arxiv_id)
        return search(query)


def match_by_doi(record):
    """TODO."""
    # FIXME(jacquerie): handle multiple DOIs.
    doi = record.get('doi.doi', '')

    if doi:
        query = '0247:"{0}"'.format(doi)
        return search(query)


def match(obj, eng):
    """TODO."""
    model = eng.workflow_definition.model(obj)
    record = get_record_from_model(model)

    arxiv_id_response = match_by_arxiv_id(record)
    doi_response = match_by_doi(record)
    response = arxiv_id_response.extend(doi_response)

    if response:
        # FIXME(jacquerie): use more than just the first id.
        obj.extra_data['recid'] = response[0]
        obj.extra_data['url'] = os.path.join(
            cfg["CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"],
            'record',
            str(response[0])
        )

        return True

    return False


def was_already_harvested(record):
    """TODO."""
    # XXX(jacquerie): comment copied from original location.
    #                 Maybe no longer relevant?

    # FIXME: Let's filter away CORE categories for now.
    # Later all harvesting will happen here.
    categories = record.get('subject_term.value', [])
    for category in categories:
        if category.lower() in cfg.get('INSPIRE_ACCEPTED_CATEGORIES', []):
            return True


def is_too_old(record, days_ago=5):
    """TODO."""
    # XXX(jacquerie): comment copied from original location.
    #                 Maybe no longer relevant?

    # Check if this record should already have been rejected
    # (only on non-debug mode) E.g. if it is older than 2 days.
    defense_dates = record.get('defense_date.date', '')
    for defense_date in defense_dates:
        parsed_date = datetime.datetime.strptime(defense_date, "%Y-%m-%d")
        if date_older_than(parsed_date, datetime.datetime.now(), days=days_ago):
            return True


def exists_in_inspire_or_rejected(days_ago=None):
    """Check if record exist on INSPIRE or already rejected."""
    @wraps(exists_in_inspire_or_rejected)
    def _exists_in_inspire_or_rejected(obj, eng):

        if match(obj, eng):
            obj.log.info("Record already exists in INSPIRE.")
            return True

        if not cfg.get('DEBUG'):
            model = eng.workflow_definition.model(obj)
            record = get_record_from_model(model)

            if was_already_harvested(record):
                obj.log.info('Record is already being harvested on INSPIRE.')
                return True

            if days_ago is None:
                _days_ago = cfg.get('INSPIRE_ACCEPTANCE_TIMEOUT', 5)
            else:
                _days_ago = days_ago

            if is_too_old(record, days_ago=_days_ago):
                obj.log.info("Record is likely rejected previously.")
                return True

    return _exists_in_inspire_or_rejected


def save_identifiers_to_kb(kb_name,
                           identifier_key="report_number.primary"):
    """Save the record identifiers into a KB."""
    @wraps(save_identifiers_to_kb)
    def _save_identifiers_to_kb(obj, eng):
        from inspire.utils.knowledge import save_keys_to_kb
        record = get_record_from_obj(obj, eng)

        identifiers = record.get(identifier_key, [])
        save_keys_to_kb(kb_name, identifiers, obj.id)

    return _save_identifiers_to_kb


def exists_in_holding_pen(kb_name,
                          identifier_key="report_number.primary"):
    """Check if a record exists in HP by looking in given KB."""
    @wraps(exists_in_holding_pen)
    def _exists_in_holding_pen(obj, eng):
        from inspire.utils.knowledge import get_value

        record = get_record_from_obj(obj, eng)
        identifiers = record.get(identifier_key, [])
        result = get_value(kb_name, identifiers)
        if result:
            obj.log.info("Record already found in Holding Pen ({0})".format(
                result
            ))
        return result

    return _exists_in_holding_pen


def delete_self_and_stop_processing(obj, eng):
    """Delete both versions of itself and stops the workflow."""
    from invenio.modules.workflows.models import BibWorkflowObject
    # delete snapshot created with original data
    initial_obj = BibWorkflowObject.query.filter(
        BibWorkflowObject.id_parent == obj.id
    ).one()
    BibWorkflowObject.delete(initial_obj.id)
    # delete self
    BibWorkflowObject.delete(obj.id)
    eng.skipToken()


def update_old_object(kb_name):
    """Update the data of the old object with the new data."""
    @wraps(update_old_object)
    def _update_old_object(obj, eng):
        from inspire.utils.knowledge import get_value
        from invenio.modules.workflows.models import BibWorkflowObject

        identifiers = []
        report_numbers = obj.get_data().get('report_number', [])
        for number in report_numbers:
            if number.get("source", "").lower() == "arxiv":
                arxiv_id = number.get("primary")
                identifiers.append(arxiv_id)

        object_id = get_value(kb_name, identifiers)
        if object_id:
            old_object = BibWorkflowObject.query.get(object_id)
            if old_object:
                # record waiting approval
                old_object.set_data(obj.get_data())
                old_object.save()

    return _update_old_object


def arxiv_set_category_field(obj, eng):
    """Temporary measure to enable sorting by primary category."""
    record = get_record_from_obj(obj, eng)
    obj.uri = record.get("report_number.arxiv_category", [""])[0]
