# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from __future__ import absolute_import, division, print_function

from flask import request
from invenio_records_rest.facets import range_filter
from inspirehep.modules.records.facets import range_author_count_filter, must_match_all_filter


def hep_author_publications():
    exclude_value = request.values.get('exclude_author_value', '', type=str)
    return {
        "filters": {
            "author": must_match_all_filter('facet_author_name'),
            "author_count": range_author_count_filter('author_count'),
            "doc_type": must_match_all_filter('facet_inspire_doc_type'),
            "earliest_date": range_filter(
                'earliest_date',
                format='yyyy',
                end_date_math='/y')
        },
        "aggs": {
            "earliest_date": {
                "date_histogram": {
                    "field": "earliest_date",
                    "interval": "year",
                    "format": "yyyy",
                    "min_doc_count": 1,
                },
                "meta": {
                    "title": "Date",
                    "order": 1,
                },
            },
            "author_count": {
                "range": {
                    "field": "author_count",
                    "ranges": [
                        {
                            "key": "10 authors or less",
                            "from": 1,
                            "to": 11,
                        },
                    ],
                },
                "meta": {
                    "title": "Number of authors",
                    "order": 2,
                },
            },
            "author": {
                "terms": {
                    "field": "facet_author_name",
                    "size": 20,
                    "exclude": exclude_value,
                },
                "meta": {
                    "title": "Collaborators",
                    "order": 3,
                },
            },
            "doc_type": {
                "terms": {
                    "field": "facet_inspire_doc_type",
                    "size": 20
                },
                "meta": {
                    "title": "Document Type",
                    "order": 4,
                },
            },
        },
    }
