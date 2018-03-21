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

from flask import json

from invenio_accounts.testutils import login_user_via_session

from invenio_workflows import workflow_object_class

from inspire_utils.record import get_value


def test_workflow_json_serializer_does_not_resolve_if_fuzzy_matches_is_missing(workflow_app):
    obj = workflow_object_class.create(
        data={},
        data_type='hep',
        id_user=1,
    )
    obj.extra_data = {
        'matches': {}
    }
    obj.save()
    with workflow_app.test_client() as client:
        login_user_via_session(client, email='cataloger@inspirehep.net')
        response = client.get('/api/holdingpen/' + str(obj.id))
        result = json.loads(response.data)
        resolved_fuzzy = get_value(result, '_extra_data.matches.fuzzy')
        assert resolved_fuzzy is None


def test_workflow_json_serializer_resolves_fuzzy_matches(workflow_app):
    matched_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1234,
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'abstracts': [
            {
                'value': 'abstract',
                'source': 'arXiv',
            }
        ],
        'titles': [
            {
                'title': 'title'
            }
        ]
    }
    from inspirehep.modules.migrator.tasks import record_insert_or_replace
    record_insert_or_replace(matched_record)

    obj = workflow_object_class.create(
        data={},
        data_type='hep',
        id_user=1,
    )
    obj.extra_data = {
        'matches': {
            'fuzzy': [
                {'$ref': 'https://localhost:5000/api/literature/1234'}
            ]
        }
    }
    obj.save()
    expected_fuzzy = [{
        'control_number': 1234,
        'abstract': 'abstract',
        'title': 'title'
    }]
    with workflow_app.test_client() as client:
        login_user_via_session(client, email='cataloger@inspirehep.net')
        response = client.get('/api/holdingpen/' + str(obj.id))
        result = json.loads(response.data)
        resolved_fuzzy = result['_extra_data']['matches']['fuzzy']
        assert resolved_fuzzy == expected_fuzzy


def test_workflow_json_serializer_resolves_fuzzy_matches_without_abstract(workflow_app):
    matched_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1234,
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {
                'title': 'title'
            }
        ]
    }
    from inspirehep.modules.migrator.tasks import record_insert_or_replace
    record_insert_or_replace(matched_record)

    obj = workflow_object_class.create(
        data={},
        data_type='hep',
        id_user=1,
    )
    obj.extra_data = {
        'matches': {
            'fuzzy': [
                {'$ref': 'https://localhost:5000/api/literature/1234'}
            ]
        }
    }
    obj.save()
    expected_fuzzy = [{
        'control_number': 1234,
        'title': 'title'
    }]
    with workflow_app.test_client() as client:
        login_user_via_session(client, email='cataloger@inspirehep.net')
        response = client.get('/api/holdingpen/' + str(obj.id))
        result = json.loads(response.data)
        resolved_fuzzy = result['_extra_data']['matches']['fuzzy']
        assert resolved_fuzzy == expected_fuzzy
