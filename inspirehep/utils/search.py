# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Functions for searching ES and returning the results."""

from __future__ import absolute_import, division, print_function

from flask import current_app

from invenio_search.api import RecordsSearch, current_search_client

from inspirehep.modules.search import IQ


def _collection_to_index(collection_name):
    """Translates a collection name to the corresponding index."""
    try:
        mapping = current_app.config['SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING']
        index = mapping[collection_name.lower()]
    except KeyError:
        index = 'records-hep'

    return index


def get_number_of_records(collection_name):
    """Returns the number of records in a collection."""
    index = _collection_to_index(collection_name)
    result = current_search_client.count(index=index)

    return result['count']


def perform_es_search(q, index, start=0, size=10, sort=None, fields=None):
    """Helper to use elasticsearch_dsl with Spires/Invenio syntax."""
    query = IQ(q)

    search = RecordsSearch(index=index).query(query)
    if sort:
        search = search.sort(sort)
    if fields and isinstance(fields, list):
        search = search.extra(_source={'include': fields})
    return search[start:start + size].execute()
