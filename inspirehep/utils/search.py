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

"""Functions for searching ES and returning the results."""

from invenio_search import current_search_client
from inspirehep.modules.search.query import perform_query


def perform_es_search(query_string, page, size, collection, sort=''):
    query, qs_kwargs = perform_query(query_string, page, size)
    search_result = current_search_client.search(
            index='records-{0}'.format(collection),
            doc_type=collection,
            sort=sort,
            body=query.body,
            version=True,
    )

    results = [hit['_source'] for hit in search_result['hits']['hits']]
    return results
