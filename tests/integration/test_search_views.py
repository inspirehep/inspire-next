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

from __future__ import absolute_import, division, print_function

import json

from mock import patch


def test_search_conferences_is_there(app_client):
    assert app_client.get('/search?cc=conferences').status_code == 200


def test_search_authors_is_there(app_client):
    assert app_client.get('/search?cc=authors').status_code == 200


def test_search_data_is_there(app_client):
    assert app_client.get('/search?cc=data').status_code == 200


def test_search_experiments_is_there(app_client):
    assert app_client.get('/search?cc=experiments').status_code == 200


def test_search_institutions_is_there(app_client):
    assert app_client.get('/search?cc=institutions').status_code == 200


def test_search_journals_is_there(app_client):
    assert app_client.get('/search?cc=journals').status_code == 200


def test_search_jobs_is_there(app_client):
    assert app_client.get('/search?cc=jobs').status_code == 200


def test_search_falls_back_to_hep(app_client):
    assert app_client.get('/search').status_code == 200


@patch('inspirehep.modules.search.search_factory.current_app')
def test_search_logs(current_app_mock, api_client):
    def _debug(log_output):
        query = {
            u'sort': [{u'earliest_date': {u'order': u'desc'}}],
            u'from': 0,
            u'_source': {u'includes': [u'$schema', u'abstracts.value',
                                       u'arxiv_eprints.value',
                                       u'authors.affiliation',
                                       u'authors.full_name',
                                       u'authors.control_number',
                                       u'collaborations',
                                       u'control_number',
                                       u'citation_count', u'dois.value',
                                       u'earliest_date',
                                       u'inspire_categories',
                                       u'publication_info',
                                       u'references.reference.title',
                                       u'report_numbers',
                                       u'titles.title']},
            u'aggs': {
                u'doc_type': {
                    u'meta': {u'order': 6, u'title': u'Document Type'},
                    u'terms': {
                        u'field': u'facet_inspire_doc_type',
                        u'size': 20}},
                u'author': {
                    u'meta': {u'order': 2, u'title': u'Author'},
                    u'terms': {u'field': u'facet_author_name',
                               u'size': 20}},
                u'arxiv_categories': {
                    u'meta': {u'order': 4, u'title': u'arXiv Category'},
                    u'terms': {u'field': u'facet_arxiv_categories',
                               u'size': 20}},
                u'experiment': {
                    u'meta': {u'order': 5, u'title': u'Experiment'},
                    u'terms': {u'field': u'facet_experiment',
                               u'size': 20}},
                u'subject': {
                    u'meta': {u'order': 3, u'title': u'Subject'},
                    u'terms': {
                        u'field': u'facet_inspire_categories',
                        u'size': 20}}, u'earliest_date': {
                    u'date_histogram': {
                        u'field': u'earliest_date',
                        u'interval': u'year',
                        u'min_doc_count': 1,
                        u'format': u'yyyy'},
                    u'meta': {u'order': 1, u'title': u'Date'}}},
            u'query': {
                u'bool': {
                    u'filter': [{u'bool': {u'must_not': [
                        {u'match': {
                            u'_collections': u'HERMES Internal Notes'}}],
                        u'must': [{u'match': {
                            u'_collections': u'Literature'}}]}}],
                    u'minimum_should_match': u'0<1',
                    u'must': [{u'match_all': {}}]}}, u'size': 10}
        assert query == json.loads(log_output)

    current_app_mock.logger.debug.side_effect = _debug
    api_client.get('/literature/')
