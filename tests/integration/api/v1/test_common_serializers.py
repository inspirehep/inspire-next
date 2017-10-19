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


def test_literature_recids_serializer(api_client):
    response = api_client.get(
        '/literature/?q=title collider',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json['hits']['total'] == 2

    expected_recids = {1373790, 701585}
    response_recids = set([recid for recid in response_json['hits']['recids']])

    assert response_recids == expected_recids


def test_authors_recids_serializer(api_client):
    response = api_client.get(
        '/authors/?q=arxiv_categories:"hep-ph"',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json['hits']['total'] == 4

    expected_recids = {1057204, 984519, 1073117, 1060891}
    response_recids = set([recid for recid in response_json['hits']['recids']])

    assert response_recids == expected_recids


def test_conferences_recids_serializer(api_client):
    response = api_client.get(
        '/conferences/',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json['hits']['total'] == 1

    assert response_json['hits']['recids'][0] == 972464


def test_institutions_recids_serializer(api_client):
    response = api_client.get(
        '/institutions/',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json['hits']['total'] == 1

    assert response_json['hits']['recids'][0] == 902725


def test_experiments_recids_serializer(api_client):
    response = api_client.get(
        '/experiments/',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json['hits']['total'] == 1

    assert response_json['hits']['recids'][0] == 1108642


def test_journals_recids_serializer(api_client):
    response = api_client.get(
        '/journals/',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    expected_recids = {1214516, 1213103}
    response_recids = set([recid for recid in response_json['hits']['recids']])

    assert response_recids == expected_recids


def test_jobs_recids_serializer(api_client):
    response = api_client.get(
        '/jobs/',
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200
