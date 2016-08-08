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


def test_api_literature_search_no_warnings_when_query_is_well_formed(app):
    with app.test_client() as client:
        response = client.get(
            '/api/literature/?cc=literature&q=author:+Panos',
            headers = {
                'Accept': 'application/vnd+inspire.brief+json',
            },
        )

        expected = []
        result = json.loads(response.data)

        assert expected == result['warnings']


def test_api_literature_search_has_warnings_when_query_is_malformed(app):
    with app.test_client() as client:
        response = client.get(
            '/api/literature/?cc=literature&q=author:+Panos+(',
            headers = {
                'Accept': 'application/vnd+inspire.brief+json',
            },
        )

        result = json.loads(response.data)

        assert {u'query_suggestion': u'MalformedQuery'} in result['warnings']


def test_api_literature_search_has_warnings_when_query_has_unssuported_keywords(app):
    with app.test_client() as client:
        response = client.get(
            '/api/literature/?cc=literature&q=refersto:+123',
            headers = {
                'Accept': 'application/vnd+inspire.brief+json',
            },
        )

        result = json.loads(response.data)

        assert {u'query_suggestion': u'keyword refersto is currently unsupported'} in result['warnings']


def test_api_literature_search_has_warnings_when_query_has_extra_keywords(app):
    with app.test_client() as client:
        response = client.get(
            '/api/literature/?cc=literature&q=author:+John+Ellis',
            headers = {
                'Accept': 'application/vnd+inspire.brief+json',
            },
        )

        result = json.loads(response.data)

        assert {u'query_suggestion': u'Extra Keyword'} in result['warnings']
