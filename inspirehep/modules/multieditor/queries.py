# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Module for quering in multi record editor used in http://inspirehep.net."""

from __future__ import absolute_import, print_function, division

from ..search import api
from invenio_records.api import Record

CLS_MAP = {
    'hep': api.LiteratureSearch,
    'authors': api.AuthorsSearch,
    'data': api.DataSearch,
    'conferences': api.ConferencesSearch,
    'jobs': api.JobsSearch,
    'institutions': api.InstitutionsSearch,
    'experiments': api.ExperimentsSearch,
    'journals': api.JournalsSearch

}


def get_total_records(query_string, index):
    """
    :param query_string: query string
    :param index: index of the records to be searched
    :return: returns the total records that match our query
    """
    query_result = CLS_MAP[index]().query_from_iq(query_string).params(
        size=1,
        fields=[]
    ).execute()

    return query_result.hits.total


def get_record_ids_from_query(query_string, index):
    """
    :param query_string: query string
    :param index: index of the records to be searched
    :return: return the uuids of the records that matched our query
    """
    uuids = []

    query_result = CLS_MAP[index]().query_from_iq(query_string).params(
        size=2000,
        fields=[]
    ).scan()

    for result in query_result:
        uuids.append(result.meta.id)
    return uuids


def get_paginated_records(page_number, page_size, uuids):
    """
    :param page_number: number of frontend page
    :param page_size:  size of the frontend page
    :param uuids: uuids that matched our query
    :return: returns the paginated uuids and db records
    """
    paginated_uuids = uuids[(page_number-1)*page_size:(page_number*page_size)]
    db_records = Record.get_records(paginated_uuids)
    records_uuids = [str(record.id) for record in db_records]
    return records_uuids, db_records,
