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

from elasticsearch_dsl import Q
from mock import patch

from inspirehep.modules.search.search_factory import select_source
from inspirehep.modules.search.api import LiteratureSearch, AuthorsSearch
import inspire_query_parser


@patch('inspirehep.modules.search.search_factory.request')
def test_select_source_function_in_literature_search(request_mocked):
    request_mocked.headers.get.return_value = 'application/vnd+inspire.record.ui+json'
    expected_source = {
        'includes': ['$schema', 'control_number', '_ui_display']
    }

    search = select_source(LiteratureSearch())
    search_source = search.to_dict()['_source']

    assert search_source == expected_source


@patch('inspirehep.modules.search.search_factory.request')
def test_select_source_function_in_search(request_mocked):
    request_mocked.headers.get.return_value = 'application/json'
    expected_source = {
        'includes': [
            '$schema', 'abstracts.value', 'arxiv_eprints.value',
            'arxiv_eprints.categories', 'authors.affiliations',
            'authors.full_name', 'authors.inspire_roles',
            'authors.control_number', 'collaborations',
            'control_number', 'citation_count',
            'dois.value', 'earliest_date', 'inspire_categories',
            'number_of_references', 'publication_info',
            'report_numbers', 'titles.title'
        ]
    }

    search = select_source(LiteratureSearch())
    search_source = search.to_dict()['_source']

    assert search_source == expected_source


def test_select_source_function_in_author_search():
    search = select_source(AuthorsSearch())
    search_source = search.to_dict().get('_source')

    assert search_source is None


def test_search_query_with_spires_syntax_in_literature_search():
    query = u"a First Middle Last"
    expected_full_statement = inspire_query_parser.parse_query(query)
    expected_must_statement = expected_full_statement['nested']['query']['bool']['filter']

    search = LiteratureSearch().query_from_iq(query)
    search_dict = search.to_dict()
    must_statement = search_dict['query']['bool']['must']

    assert len(must_statement) == 1
    must_statement = must_statement[0]['nested']
    assert must_statement['path'] == 'authors'
    assert must_statement['query']['bool']['filter'][0] == expected_must_statement


def test_search_query_with_spires_syntax_in_authors_search():
    query_string = u"a First Middle Last"
    expected_query = Q('match', _all=query_string).to_dict()

    search = AuthorsSearch().query_from_iq(query_string)
    search_dict = search.to_dict()
    query = search_dict['query']

    assert query == expected_query


def test_empty_search_query_in_authors_search():
    query_string = ""
    expected_query = Q().to_dict()

    search = AuthorsSearch().query_from_iq(query_string)
    search_dict = search.to_dict()
    query = search_dict['query']

    assert query == expected_query
