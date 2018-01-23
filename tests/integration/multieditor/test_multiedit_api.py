# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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
import pytest

from invenio_accounts.testutils import login_user_via_session
from invenio_records.api import Record


def test_multieditor_search_api(api_client):
    login_user_via_session(api_client, email='cataloger@inspirehep.net')
    response = api_client.get('/multieditor/search?number=1&q=control_number:736770&index=hep')
    assert 736770 == json.loads(response.data)['json_records'][0]['control_number']


def test_multieditor_preview_api(api_client):
    login_user_via_session(api_client, email='cataloger@inspirehep.net')
    api_client.get('/multieditor/search?number=1&q=control_number:736770&index=hep')
    response = api_client.post(
        '/multieditor/preview',
        content_type='application/json',
        data=json.dumps({
            'userActions': {
                'actions': [{
                    'actionName': 'Addition', 'value': {'full_name': 'James Bond'},
                    'matchType': 'is equal to',
                    'mainKey': 'authors'
                }],
                'conditions': [],
            },
            'queryString': 'control_number:736770',
            'pageNum': 1,
            'pageSize': 10,
            'allSelected': True,
        }),
    )

    expected_patch = [{u'path': [u'authors', 1], u'value': {u'full_name': u'James Bond'}, u'op': u'add'}]
    gotten_patches = json.loads(response.data)['json_patches']
    assert len(gotten_patches) == 1
    assert expected_patch == gotten_patches[0]


def test_multieditor_update_api(api_client):
    login_user_via_session(api_client, email='cataloger@inspirehep.net')
    response = api_client.get('/multieditor/search?number=1&q=control_number:736770&index=hep')

    api_client.post(
        '/multieditor/update',
        content_type='application/json',
        data=json.dumps({
            'userActions': {
                'actions': [{
                    'actionName': 'Addition', 'value': {'full_name': 'James Bond'},
                    'matchType': 'is equal to',
                    'mainKey': 'authors'
                }],
                'conditions': [],
            },
            'ids': [],
            'allSelected': True,
        }),
    )

    records = Record.get_records(json.loads(response.data)['uuids'])
    assert 'James Bond' in records[0]['authors'][-1]['full_name']
    uuid_to_delete = records[0]['authors'][-1]['uuid']
    signature_block_to_delete = records[0]['authors'][-1]['signature_block']
    api_client.post(
        '/multieditor/update',
        content_type='application/json',
        data=json.dumps({
            'userActions': {
                'actions': [
                    {
                        'actionName': 'Deletion',
                        'updateValue': signature_block_to_delete,
                        'matchType': 'is equal to',
                        'mainKey': 'authors.signature_block',
                    },
                    {
                        'actionName': 'Deletion',
                        'updateValue': uuid_to_delete,
                        'matchType': 'is equal to',
                        'mainKey': 'authors.uuid',
                    },
                    {
                        'actionName': 'Deletion',
                        'updateValue': 'James Bond',
                        'matchType': 'is equal to',
                        'mainKey': 'authors.full_name',
                    }
                ],
                'conditions': [
                    {
                        'key': 'authors.full_name',
                        'matchType': 'is equal to',
                        'value': 'James Bond'
                    }
                ]
            },
            'ids': [],
            'allSelected': True
        }),
    )
    records = Record.get_records(json.loads(response.data)['uuids'])
    if records[0].get('authors'):
        assert 'James Bond' not in records[0]['authors'][-1]['full_name']


@pytest.mark.parametrize('user_info,status', [
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 403),
    # Logged in user with permissions assigned
    (dict(email='cataloger@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_api_permision_search(api_client, user_info, status):
    login_user_via_session(api_client, email=user_info['email'])
    response = api_client.get('/multieditor/search?number=1&q=control_number:736770&index=hep')
    assert response.status_code == status


@pytest.mark.parametrize('user_info,endpoint', [
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 'update'),
    (dict(email='johndoe@inspirehep.net'), 'preview'),
    # No user logged in
    (None, 'update'),
    (None, 'preview')
])
def test_api_permission(api_client, user_info, endpoint):
    if user_info:
        login_user_via_session(api_client, email=user_info['email'])
    response = api_client.post(
        '/multieditor/'+endpoint,
        content_type='application/json'
    )
    assert response.status_code == 403


def test_multieditor_update_api_faulty_actions(api_client):
    login_user_via_session(api_client, email='cataloger@inspirehep.net')
    api_client.get('/multieditor/search?number=1&q=control_number:736770&index=hep')

    response = api_client.post(
        '/multieditor/preview',
        content_type='application/json',
        data=json.dumps({
            'userActions': {
                'actions': [{
                    'actionName': 'Addition', 'value': {'full_name': 'James Bond'},
                    'matchType': 'is equal to',
                    'mainKey': 'not_in_schema'
                }],
                'conditions': [],
            },
            'ids': [],
            'allSelected': True,
        }),
    )
    assert 'The actions that were provided are invalid' in json.loads(response.data)['message']
    assert response.status_code == 400
