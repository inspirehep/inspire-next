# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

SCHEMA_TO_QUERIES = {
    'hep': api.LiteratureSearch,
    'authors': api.AuthorsSearch,
    'data': api.DataSearch,
    'conferences': api.ConferencesSearch,
    'jobs': api.JobsSearch,
    'institutions': api.InstitutionsSearch,
    'experiments': api.ExperimentsSearch,
    'journals': api.JournalsSearch

}


def get_total_records(query, schema):
    """
    :param query: query string
    :param schema: schema of the records to be searched
    :return: returns the total records that match our query
    """
    query_result = SCHEMA_TO_QUERIES[schema]() \
        .query_from_iq(query).params(
        size=1,
        fields=[]
    ).execute()

    return query_result.hits.total


def get_record_ids_from_query(query, schema):
    """
    :param query: query string
    :param schema: schema of the records to be searched
    :return: return the uuids of the records that matched our query
    """
    query_result = SCHEMA_TO_QUERIES[schema]()\
        .query_from_iq(query).params(
        size=2000,
        fields=[]
    ).scan()

    uuids = [result.meta.id for result in query_result]
    return uuids


def get_paginated_records(number, size, uuids):
    """
    :param number: number of frontend page
    :param size:  size of the frontend page
    :param uuids: uuids that matched our query
    :return: returns the paginated uuids and db records
    """
    paginated_uuids = uuids[(number-1)*size:(number*size)]
    db_records = Record.get_records(paginated_uuids)
    records_uuids = [str(record.id) for record in db_records]
    return records_uuids, db_records,
