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

from __future__ import absolute_import, division, print_function

import json

from mock import patch


def test_search_conferences_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=conferences').status_code == 200


def test_search_authors_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=authors').status_code == 200


def test_search_data_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=data').status_code == 200


def test_search_experiments_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=experiments').status_code == 200


def test_search_institutions_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=institutions').status_code == 200


def test_search_journals_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=journals').status_code == 200


def test_search_jobs_is_there(app):
    with app.test_client() as client:
        assert client.get('/search?cc=jobs').status_code == 200


def test_search_falls_back_to_hep(app):
    with app.test_client() as client:
        assert client.get('/search').status_code == 200


@patch('inspirehep.modules.search.query.current_app')
def test_search_logs(current_app_mock, app):
    def _debug(log_output):
        query = {
            'query': {
                'bool': {
                    'filter': [{
                        'match': {'_collections': 'Literature'}
                    }],
                    'must': [{
                        'multi_match': {
                            'query': '',
                            'fields': [
                                'title^3',
                                'title.raw^10',
                                'abstract^2',
                                'abstract.raw^4',
                                'author^10',
                                'author.raw^15',
                                'reportnumber^10',
                                'eprint^10',
                                'doi^10'
                            ],
                            'zero_terms_query': 'all',
                        }
                    }]
                }
            },
            'from': 0,
            'size': 10
        }
        assert query == json.loads(log_output)

    current_app_mock.logger.debug.side_effect = _debug
    with app.test_client() as client:
        client.get('/api/literature/')
