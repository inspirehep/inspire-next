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

import json

from factories.db.invenio_records import TestRecordMetadata


def test_literature_authors_serializer_record(isolated_api_client):
    record = {
        'control_number': 123,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        'authors': [
            {
                'full_name': 'Frank Castle',
            },
            {
                'full_name': 'Smith, John',
                'inspire_roles': ['supervisor'],
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
            },
        ],
        'urls': [
            {
                'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
            }
        ],
    }
    TestRecordMetadata.create_from_kwargs(json=record)
    response = isolated_api_client.get(
        '/literature/123/authors',
        headers={'Accept': 'application/json'}
    )

    expected_metadata = {
        'authors': [
            {
                'full_name': 'Frank Castle',
                'first_name': 'Frank Castle',
            }
        ],
        'collaborations': [
            {
                'value': 'LHCb'
            }
        ],
        'supervisors': [
            {
                'full_name': 'Smith, John',
                'first_name': 'John',
                'last_name': 'Smith',
                'inspire_roles': ['supervisor'],
            }
        ],
    }

    result = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert expected_metadata == result['metadata']


def test_literature_authors_serializer_search(isolated_api_client):
    record = {
        'control_number': 123,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        'authors': [
            {
                'full_name': 'Frank Castle',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
            },
        ],
        'urls': [
            {
                'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
            }
        ],
    }
    TestRecordMetadata.create_from_kwargs(json=record)
    response = isolated_api_client.get(
        '/literature/authors',
        headers={'Accept': 'application/json'}
    )
    # XXX: we don't have ES isolation, checking the results doesn't make sense.
    assert response.status_code == 200


def test_zero_citations_in_vnd_plus_inspire_record_ui_json(isolated_api_client):
    record_json = {
        'control_number': 123,
    }
    TestRecordMetadata.create_from_kwargs(json=record_json)
    url = '/literature/123'
    response = isolated_api_client.get(url,
                                       headers={'Accept': 'application/vnd+inspire.record.ui+json'})
    assert response.status_code == 200
    result = json.loads(response.get_data(as_text=True))
    assert result['metadata']['citation_count'] == 0


def test_non_zero_citation_count_in_vnd_plus_inspire_record_ui_json(isolated_api_client):
    from invenio_db import db
    with db.session.begin_nested():
        record_json = {
            'control_number': 123,
        }
        record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record
        url = '/literature/123'
        # Add citation
        ref = {'control_number': 1234, 'references': [{'record': {'$ref': record._get_ref()}}]}
        TestRecordMetadata.create_from_kwargs(json=ref)

        response = isolated_api_client.get(url,
                                           headers={'Accept': 'application/vnd+inspire.record.ui+json'})
        assert response.status_code == 200
        result = json.loads(response.get_data(as_text=True))
        assert result['metadata']['citation_count'] == 1


def test_zero_citation_count_in_es(isolated_api_client):
    cn_map = {
        1234: 1,
        12345: 0
    }
    record_json = {
        'control_number': 1234,
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record
    url = '/literature/?page=1&size=25&q=control_number%3A1234'
    # Add citation
    ref = {'control_number': 12345, 'references': [{'record': {'$ref': record._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)

    response = isolated_api_client.get(url,
                                       headers={'Accept': 'application/vnd+inspire.record.ui+json'})
    assert response.status_code == 200
    result = json.loads(response.get_data(as_text=True))
    for obj in result['hits']['hits']:
        obj_meta = obj['metadata']
        if obj_meta['control_number'] not in cn_map.keys():
            continue
        assert obj_meta['citation_count'] == cn_map[obj_meta['control_number']]
