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


@pytest.fixture
def populate_db(app):
    db_records = []
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_records.json')) as data_file:
        records = json.load(data_file)
    for record in records:
        db_records.append(InspireRecord.create(record))
    db.session.commit()
    es.indices.refresh('records-hep')
    yield populate_db
    for db_record in db_records:
        db_record._delete(force=True)
    db.session.commit()


def test_multieditor_search_api(populate_db, api_client):
    response = api_client.get('/multieditor/search?page_num=1&query_string=foo&index=hep')
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_records.json')) as data_file:
        records = json.load(data_file)
    assert sorted(records) == sorted(json.loads(response.data)['json_records'])


def test_multieditor_update_api(populate_db, api_client, app_client):
    login_user_via_session(app_client, email='cataloger@inspirehep.net')
    api_client.get('/multieditor/search?page_num=1&query_string=&index=hep')

    api_client.post(
            '/multieditor/update',
            content_type='application/json',
            data=json.dumps({
                'userActions': [{'selectedAction': 'Addition', 'value': {'full_name': 'success'},
                                  'whereRegex': False, 'whereValues': [],
                                  'mainKey': 'authors',
                                  'whereKey': ''}],
                'ids': ['8569ad80-7996-43fb-a5b0-7b152a607668',
                        'f0746746-689f-4e64-b131-e23e37cc1ec7',
                        '47e8b29b-48e0-4909-8063-97d6405c6e0b'],
                'allSelected': False
            }),
        )
    records = Record.get_records(['8569ad80-7996-43fb-a5b0-7b152a607668',
                                 'f0746746-689f-4e64-b131-e23e37cc1ec7', '47e8b29b-48e0-4909-8063-97d6405c6e0b'])
    for record in records:
        assert 'success' in record.authors[-1].full_name

    api_client.post(
        '/multieditor/update',
        content_type='application/json',
        data=json.dumps({
            'userActions': [{'selectedAction': 'Deletion', 'updateValues': [],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': ['success'],
                              'mainKey': 'authors/signature_block',
                              'whereKey': 'authors/full_name'},
                             {'selectedAction': 'Deletion', 'updateValues': [],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': ['success'],
                              'mainKey': 'authors/uuid',
                              'whereKey': 'authors/full_name'},
                             {'selectedAction': 'Deletion', 'updateValues': ['success'],
                              'updateRegex': False,
                              'whereRegex': False, 'whereValues': [],
                              'mainKey': 'authors/full_name',
                              'whereKey': ''}],
            'ids': ['8569ad80-7996-43fb-a5b0-7b152a607668',
                    'f0746746-689f-4e64-b131-e23e37cc1ec7',
                    '47e8b29b-48e0-4909-8063-97d6405c6e0b'],
            'allSelected': False
        }),
    )
    records = Record.get_records(['8569ad80-7996-43fb-a5b0-7b152a607668',
                                 'f0746746-689f-4e64-b131-e23e37cc1ec7', '47e8b29b-48e0-4909-8063-97d6405c6e0b'])

    for record in records:
        if record.get('authors'):
            assert 'success' not in record.authors[-1].full_name
