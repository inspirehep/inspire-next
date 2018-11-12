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

from factories.db.invenio_records import TestRecordMetadata


def test_get_linked_refs(isolated_api_client):
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '045',
                'journal_title': 'JHEP',
                'journal_volume': '06',
                'page_start': '045',
                'year': 2007
            }
        ],
        'titles': [
            {
                'title': 'The Strongly-Interacting Light Higgs'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    references = {
        'references': [
            {
                'reference': {
                    'publication_info': {
                        'artid': '045',
                        'journal_title': 'JHEP',
                        'journal_volume': '06',
                        'page_start': '045',
                        'year': 2007
                    }
                }
            }
        ]
    }

    response = isolated_api_client.post(
        '/editor/linked_references/',
        content_type='application/json',
        data=json.dumps(references),
    )
    assert response.status_code == 200

    linked_refs = json.loads(response.data)
    assert linked_refs['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/1'


def test_get_linked_refs_empty_list(isolated_api_client):
    response = isolated_api_client.post(
        '/editor/linked_references/',
        content_type='application/json',
        data=json.dumps({'references': []}),
    )
    assert response.status_code == 200

    linked_refs = json.loads(response.data)
    assert linked_refs['references'] == []


def test_get_linked_refs_references_are_none(isolated_api_client):
    response = isolated_api_client.post(
        '/editor/linked_references/',
        content_type='application/json',
        data=None
    )
    assert response.status_code == 400


def test_get_linked_refs_bad_request(isolated_api_client):
    response = isolated_api_client.get(
        '/editor/linked_references/',
    )
    assert response.status_code == 405
