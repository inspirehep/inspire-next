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

import os

import json
import pkg_resources
import urllib

from inspirehep.modules.search.facets import hep_author_publications


def test_hep_author_publications(isolated_app):
    expect = {
        'meta': {
            'order': 3,
            'title': 'Collaborators',
            'split': True
        },
        'terms': {
            'exclude': 'Jones, Jessica',
            'field': 'facet_author_name',
            'size': 20,
        },
    }
    with isolated_app.test_request_context('?exclude_author_value=Jones, Jessica'):
        result = hep_author_publications()
        assert expect == result['aggs']['author']


def test_hep_author_publications_without_exclude_parameter(isolated_app):
    expect = {
        'meta': {
            'order': 3,
            'title': 'Collaborators',
            'split': True
        },
        'terms': {
            'exclude': '',
            'field': 'facet_author_name',
            'size': 20,
        },
    }
    with isolated_app.test_request_context():
        result = hep_author_publications()
        assert expect == result['aggs']['author']


def load_json_resource(resource):
    file = pkg_resources.resource_filename(__name__, os.path.join('fixtures',
                                                                  '%s.json' % resource))
    data = json.load(open(file, 'r'))
    return data


def test_hep_facets_by_author_name(api_client):
    query = {'q': 'a Fecko'}
    expected = load_json_resource('test_hep_facets_by_author_name_expected_1')

    assert expected == json.loads(
        api_client.get('literature/facets?%s' % urllib.urlencode(query)).data)

    query = {'q': 'a Müller'}
    expected = load_json_resource('test_hep_facets_by_author_name_expected_2')

    assert expected == json.loads(
        api_client.get('literature/facets?%s' % urllib.urlencode(query)).data)

    query = {'q': 'a üź'}
    expected = load_json_resource('test_hep_facets_by_author_name_expected_3')
    assert expected == json.loads(
        api_client.get('literature/facets?%s' % urllib.urlencode(query)).data)
