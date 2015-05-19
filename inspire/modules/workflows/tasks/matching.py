# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""Contains task to check if incoming record already exist."""

import os
import requests
import traceback

from functools import wraps

from invenio.base.globals import cfg
from invenio.modules.deposit.models import Deposition


def perform_request(obj, params):
    """Performs a matching request and if match found populates extra_data."""
    try:
        res = requests.get(cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"], params=params)
        response = res.json()
        if response:
            obj.extra_data['recid'] = response[0]
            obj.extra_data['url'] = os.path.join(
                cfg["CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"],
                'record',
                str(response[0])
            )
            return True
    except requests.ConnectionError:
        obj.log.error("Error connecting to remote server:\n {0}".format(
            traceback.format_exc()
        ))
        raise
    except ValueError:
        obj.log.error("Error decoding results from remote server:\n {0}".format(
            traceback.format_exc()
        ))
        raise

def match_record_arxiv_remote(obj, arxiv_id):
    """Look on the remote server if the record exists using arXiv id."""
    if arxiv_id:
        arxiv_id = arxiv_id.lower().replace('arxiv:', '')
        params = dict(p='035:"oai:arXiv.org:{0}"'.format(arxiv_id), of="id")
        return perform_request(obj, params)
    return {}


def match_record_arxiv_remote_oaiharvest(obj, eng):
    """Look on the remote server if the record exists using arXiv id."""
    report_numbers = obj.get_data().get('report_number', [])
    for number in report_numbers:
        if number.get("source", "").lower() == "arxiv":
            res = match_record_arxiv_remote(obj, number.get("primary"))
            if res:
                return True
    return False


def match_record_arxiv_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using arXiv id."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    return bool(match_record_arxiv_remote(obj, sip.metadata.get('arxiv_id')))


def match_record_doi_remote(obj, doi):
    """Look on the remote server if the record exists using doi."""
    if doi:
        params = dict(p='0247:"{0}"'.format(doi), of="id")
        return perform_request(obj, params)
    return False


def match_record_doi_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using doi."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    doi = sip.metadata.get('doi')
    return match_record_doi_remote(obj, doi)


def match_record_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using doi and arxiv_id."""
    return match_record_arxiv_remote_deposit(obj, eng) or\
        match_record_doi_remote_deposit(obj, eng)


def match_record_remote_oaiharvest(obj, eng):
    """Look on the remote server if the record exists using doi and arxiv_id."""
    return match_record_arxiv_remote_deposit(obj, eng) or\
        match_record_doi_remote_deposit(obj, eng)


def save_identifiers_oaiharvest(kb_name):
    """Save the record identifiers into a KB."""
    @wraps(save_identifiers_oaiharvest)
    def _save_identifiers_oaiharvest(obj, eng):
        from inspire.utils.knowledge import save_keys_to_kb

        identifiers = []
        report_numbers = obj.get_data().get('report_number', [])
        for number in report_numbers:
            if number.get("source", "").lower() == "arxiv":
                arxiv_id = number.get("primary")
                identifiers.append(arxiv_id)
        save_keys_to_kb(kb_name, identifiers, obj.id)

    return _save_identifiers_oaiharvest


def match_record_HP_oaiharvest(kb_name):
    """Check if a oaiharvest record exists in HP."""
    @wraps(match_record_HP_oaiharvest)
    def _match_record_HP_oaiharvest(obj, eng):
        from inspire.utils.knowledge import check_keys

        identifiers = []
        report_numbers = obj.get_data().get('report_number', [])
        for number in report_numbers:
            if number.get("source", "").lower() == "arxiv":
                arxiv_id = number.get("primary")
                identifiers.append(arxiv_id)
        return check_keys(kb_name, identifiers)

    return _match_record_HP_oaiharvest


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
