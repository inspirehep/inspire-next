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

"""Tests for workflow views."""

from __future__ import absolute_import, division, print_function

import json

import pytest
from invenio_workflows import ObjectStatus, WorkflowEngine, start, workflow_object_class
from invenio_accounts.testutils import login_user_via_session

from inspirehep.utils.tickets import get_rt_link_for_ticket
from inspirehep.utils.record_getter import get_db_record

from calls import do_robotupload_callback
from factories.db.invenio_records import TestRecordMetadata


@pytest.fixture(scope='function')
def edit_workflow(workflow_app):
    app_client = workflow_app.test_client()
    login_user_via_session(app_client, email='admin@inspirehep.net')

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-th'
                ],
                'value': '1802.03287'
            }
        ],
        'control_number': 123,
        'document_type': ['article'],
        'titles': [{'title': 'Resource Pooling in Large-Scale Content Delivery Systems'}],
        'self': {'$ref': 'http://localhost:5000/schemas/records/hep.json'},
        '_collections': ['Literature']
    }
    factory = TestRecordMetadata.create_from_kwargs(json=record)
    eng_uuid = start('edit_article', data=factory.record_metadata.json)
    obj = WorkflowEngine.from_uuid(eng_uuid).objects[0]

    assert obj.status == ObjectStatus.WAITING
    assert obj.extra_data['callback_url']
    return obj


def test_edit_article_view(workflow_api_client):
    login_user_via_session(workflow_api_client, email='admin@inspirehep.net')

    factory = TestRecordMetadata.create_from_kwargs(json={})
    control_number = factory.record_metadata.json['control_number']
    endpoint_url = "/workflows/edit_article/{}".format(control_number)

    response = workflow_api_client.get(endpoint_url)
    assert response.status_code == 302
    assert "/editor/holdingpen/" in response.headers['Location']


def test_edit_article_view_sets_curation_ticket_if_referrer_is_rt_ticket(workflow_api_client):
    login_user_via_session(workflow_api_client, email='admin@inspirehep.net')

    factory = TestRecordMetadata.create_from_kwargs(json={})
    control_number = factory.record_metadata.json['control_number']
    endpoint_url = "/workflows/edit_article/{}".format(control_number)

    response = workflow_api_client.get(
        endpoint_url,
        headers={'Referer': get_rt_link_for_ticket(1234)}
    )
    assert response.status_code == 302
    assert "/editor/holdingpen/" in response.headers['Location']

    wflw_id = response.headers['Location'].split('/')[-1]
    wflw = workflow_object_class.get(wflw_id)
    assert wflw.extra_data.get('curation_ticket_id') == 1234


def test_edit_article_view_wrong_recid(workflow_api_client):
    login_user_via_session(workflow_api_client, email='admin@inspirehep.net')

    response = workflow_api_client.get("/workflows/edit_article/1")
    assert response.status_code == 404


def test_edit_article_workflow(workflow_app, mocked_external_services):
    app_client = workflow_app.test_client()
    login_user_via_session(app_client, email='admin@inspirehep.net')

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-th'
                ],
                'value': '1802.03287'
            }
        ],
        'control_number': 123,
        'document_type': ['article'],
        'titles': [{'title': 'Resource Pooling in Large-Scale Content Delivery Systems'}],
        'self': {'$ref': 'http://localhost:5000/schemas/records/hep.json'},
        '_collections': ['Literature']
    }
    factory = TestRecordMetadata.create_from_kwargs(json=record)
    eng_uuid = start('edit_article', data=factory.record_metadata.json)
    obj = WorkflowEngine.from_uuid(eng_uuid).objects[0]

    assert obj.status == ObjectStatus.WAITING
    assert obj.extra_data['callback_url']

    # simulate changes in the editor and save
    new_title = 'Somebody edited this fancy title'
    obj.data['titles'][0]['title'] = new_title

    payload = {
        'id': obj.id,
        'metadata': obj.data,
        '_extra_data': obj.extra_data
    }

    app_client.put(
        obj.extra_data['callback_url'],
        data=json.dumps(payload),
        content_type='application/json'
    )

    obj = WorkflowEngine.from_uuid(eng_uuid).objects[0]
    assert obj.status == ObjectStatus.WAITING  # waiting for robot_upload
    assert obj.data['titles'][0]['title'] == new_title

    do_robotupload_callback(
        app=workflow_app,
        workflow_id=obj.id,
        recids=[obj.data['control_number']],
    )

    record = get_db_record('lit', 123)
    assert record['titles'][0]['title'] == new_title


@pytest.mark.parametrize('user_info, expected_status_code', [
    (None, 403),
    ({'email': 'johndoe@inspirehep.net'}, 403),
    ({'email': 'jlabcurator@inspirehep.net'}, 302),
    ({'email': 'cataloger@inspirehep.net'}, 302),
    ({'email': 'admin@inspirehep.net'}, 302),
])
def test_edit_article_start_permission(
    app,
    app_client,
    user_info,
    expected_status_code,
    mocked_external_services,
):
    if user_info:
        login_user_via_session(app_client, email=user_info['email'])

    factory = TestRecordMetadata.create_from_kwargs(json={})
    control_number = factory.record_metadata.json['control_number']
    endpoint_url = "/workflows/edit_article/{}".format(control_number)

    response = app_client.get(endpoint_url)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize('user_info, expected_status_code', [
    (None, 403),
    ({'email': 'johndoe@inspirehep.net'}, 403),
    ({'email': 'jlabcurator@inspirehep.net'}, 200),
    ({'email': 'cataloger@inspirehep.net'}, 200),
    ({'email': 'admin@inspirehep.net'}, 200),
])
def test_edit_article_callback_permission(
    user_info,
    expected_status_code,
    edit_workflow,
    workflow_api_client,
    mocked_external_services,
):
    if user_info:
        login_user_via_session(workflow_api_client, email=user_info['email'])
    else:
        with workflow_api_client.session_transaction() as sess:
            sess['user_id'] = None

    payload = {
        "_id": edit_workflow.id,
        "_extra_data": edit_workflow.extra_data,
        "metadata": edit_workflow.data,
    }
    response = workflow_api_client.put(
        edit_workflow.extra_data['callback_url'],
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code


def test_edit_article_callback_redirects_to_rt(
    edit_workflow,
    workflow_api_client,
    mocked_external_services,
    workflow_app,
):
    user_info = {'email': 'jlabcurator@inspirehep.net'}

    login_user_via_session(workflow_api_client, email=user_info['email'])

    edit_workflow.extra_data['curation_ticket_id'] = 1234
    payload = {
        "_id": edit_workflow.id,
        "_extra_data": edit_workflow.extra_data,
        "metadata": edit_workflow.data,
    }
    response = workflow_api_client.put(
        edit_workflow.extra_data['callback_url'],
        data=json.dumps(payload),
        content_type='application/json',
    )

    expected_redirect = get_rt_link_for_ticket(1234)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'redirect_url' in data
    assert data['redirect_url'] == expected_redirect


def test_edit_article_callback_redirects_to_root_if_no_referrer(
    edit_workflow,
    workflow_api_client,
    mocked_external_services,
    workflow_app,
):
    user_info = {'email': 'jlabcurator@inspirehep.net'}

    login_user_via_session(workflow_api_client, email=user_info['email'])

    payload = {
        "_id": edit_workflow.id,
        "_extra_data": edit_workflow.extra_data,
        "metadata": edit_workflow.data,
    }
    response = workflow_api_client.put(
        edit_workflow.extra_data['callback_url'],
        data=json.dumps(payload),
        content_type='application/json',
    )

    expected_redirect = 'http://%s/' % workflow_app.config['SERVER_NAME']

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'redirect_url' in data
    assert data['redirect_url'] == expected_redirect
