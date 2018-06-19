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

from invenio_workflows import ObjectStatus, WorkflowEngine, start

from inspirehep.utils.record_getter import get_db_record

from calls import do_robotupload_callback
from factories.db.invenio_records import TestRecordMetadata


def test_jlab_edit_view(api_client):
    factory = TestRecordMetadata.create_from_kwargs(json={})
    control_number = factory.record_metadata.json['control_number']
    endpoint_url = "/workflows/edit_article/{}".format(control_number)

    response = api_client.get(endpoint_url)
    assert response.status_code == 302
    assert "/editor/holdingpen/" in response.data


def test_jlab_edit_view_wrong_recid(api_client):
    response = api_client.get("/workflows/edit_article/1")
    assert response.status_code == 500


def test_edit_article_workflow(workflow_app, mocked_external_services):
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
    new_title = 'JLab edited this fancy title'
    obj.data['titles'][0]['title'] = new_title

    payload = {
        'id': obj.id,
        'metadata': obj.data,
        '_extra_data': obj.extra_data
    }

    workflow_app.test_client().put(
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
