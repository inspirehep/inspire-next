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

import requests
import traceback

from invenio.base.globals import cfg
from invenio.modules.deposit.models import Deposition


def match_record_arxiv_remote(arxiv_id):
    """Look on the remote server if the record exists using arXiv id."""
    if arxiv_id:
        arxiv_id = arxiv_id.lower().replace('arxiv:', '')
        params = dict(p="035:oai:arXiv.org:%s" % arxiv_id, of="id")
        r = requests.get(cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"], params=params)
        response = r.json()
        if response:
            return True
    return False


def match_record_arxiv_remote_oaiharvest(obj, eng):
    """Look on the remote server if the record exists using arXiv id."""
    report_numbers = obj.get_data().get('report_number', {})
    if isinstance(report_numbers, dict):
        arxiv_id = report_numbers.get('value')
    else:
        arxiv_id = None
        for number in report_numbers:
            if number.get("source", "").lower() == "arxiv":
                arxiv_id = number.get("value")
                break
    try:
        return match_record_arxiv_remote(arxiv_id)
    except requests.ConnectionError:
        obj.log.error("Error connecting to remote server:\n {0}".format(
            traceback.format_exc()
        ))
        return False


def match_record_arxiv_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using arXiv id."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    arxiv_id = sip.metadata.get('arxiv_id')
    try:
        return match_record_arxiv_remote(arxiv_id)
    except requests.ConnectionError:
        obj.log.error("Error connecting to remote server:\n {0}".format(
            traceback.format_exc()
        ))
        return False


def match_record_doi_remote(doi):
    """Look on the remote server if the record exists using doi."""
    if doi:
        params = dict(p="0247:%s" % doi, of="id")
        r = requests.get(cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"], params=params)
        response = r.json()
        if response:
            return True
    return False


def match_record_doi_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using doi."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    doi = sip.metadata.get('doi')
    return match_record_doi_remote(doi)


def match_record_remote_deposit(obj, eng):
    """Look on the remote server if the record exists using doi and arxiv_id."""
    return match_record_arxiv_remote_deposit(obj, eng) or\
        match_record_doi_remote_deposit(obj, eng)


def match_record_remote_oaiharvest(obj, eng):
    """Look on the remote server if the record exists using doi and arxiv_id."""
    return match_record_arxiv_remote_deposit(obj, eng) or\
        match_record_doi_remote_deposit(obj, eng)
