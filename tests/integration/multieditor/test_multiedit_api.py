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
import pytest
import os
import json
from invenio_db import db
from invenio_search import current_search_client as es
from inspirehep.modules.records.api import InspireRecord
from invenio_accounts.testutils import login_user_via_session
from invenio_records.api import Record


def test_multieditor_search_api(api_client):
    response = api_client.get('/multieditor/search?page_num=1&query_string=control_number:736770&index=hep')
    assert 736770 == json.loads(response.data)['json_records'][0]['control_number']


def test_multieditor_update_api(api_client, app_client):
    login_user_via_session(app_client, email='cataloger@inspirehep.net')
    response = api_client.get('/multieditor/search?page_num=1&query_string=control_number:736770&index=hep')

    api_client.post(
            '/multieditor/update',
            content_type='application/json',
            data=json.dumps({
                'userActions': [{'selectedAction': 'Addition', 'value': {'full_name': 'success'},
                                  'whereRegex': False, 'whereValues': [],
                                  'mainKey': 'authors',
                                  'whereKey': ''}],
                'ids': [],
                'allSelected': True
            }),
        )

    records = Record.get_records(json.loads(response.data)['uuids'])
    assert 'success' in records[0]['authors'][-1]['full_name']
    uuid_to_delete = records[0]['authors'][-1]['uuid']

    api_client.post(
        '/multieditor/update',
        content_type='application/json',
        data=json.dumps({
            'userActions': [{'selectedAction': 'Deletion', 'updateValues': ['SAC'],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': ['success'],
                              'mainKey': 'authors/signature_block',
                              'whereKey': 'authors/full_name'},
                             {'selectedAction': 'Deletion', 'updateValues': [uuid_to_delete],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': ['success'],
                              'mainKey': 'authors/uuid',
                              'whereKey': 'authors/full_name'},
                             {'selectedAction': 'Deletion', 'updateValues': ['success'],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': [],
                              'mainKey': 'authors/full_name',
                              'whereKey': ''}],
            'ids': [],
            'allSelected': True
        }),
    )
    records = Record.get_records(json.loads(response.data)['uuids'])
    if records[0].get('authors'):
        assert 'success' not in records[0]['authors'][-1]['full_name']
