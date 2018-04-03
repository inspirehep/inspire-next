# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# Free Software Foundation, either version 3 of the License, or
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

"""Tests for merge and resolve merge conflicts."""

from __future__ import absolute_import, division, print_function

import json
import mock
import pytest

from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
)


@pytest.fixture
def enable_merge_on_update(workflow_app):
    with mock.patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_MERGER': True}):
        yield


def test_merge_with_disabled_merge_on_update_feature_flag(workflow_app, record_to_merge):
    record_update = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.extra_data.get('callback_url') is None
    assert obj.extra_data.get('conflicts') is None
    assert obj.extra_data.get('merged') is True


def test_merge_without_conflicts(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data.get('callback_url') is None
    assert obj.extra_data.get('conflicts') is None

    assert obj.extra_data.get('approved') is True
    assert obj.extra_data.get('is-update') is True
    assert obj.extra_data.get('merged') is True


def test_merge_with_conflicts(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://schemas.stark-industries.com/schemas/records/avengers.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    assert obj.status == ObjectStatus.HALTED
    assert len(conflicts) == 1
    assert obj.extra_data.get('callback_url') is not None
    assert obj.extra_data.get('is-update') is True


def test_merge_without_conflicts_callback_url(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

    assert conflicts is None
    assert obj.extra_data.get('is-update') is True

    payload = {
        'id': obj.id,
        'metadata': obj.data,
        '_extra_data': obj.extra_data
    }

    with workflow_app.test_client() as client:
        response = client.put(
            url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 400


def test_merge_with_conflicts_callback_url(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://schemas.stark-industries.com/schemas/avengers.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

    assert obj.status == ObjectStatus.HALTED
    assert expected_url == obj.extra_data.get('callback_url')
    assert len(conflicts) == 1
    assert obj.extra_data.get('is-update') is True

    payload = {
        'id': obj.id,
        'metadata': obj.data,
        '_extra_data': obj.extra_data
    }

    with workflow_app.test_client() as client:
        response = client.put(
            obj.extra_data.get('callback_url'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    data = json.loads(response.get_data())
    expected_message = 'Workflow {} has been saved with conflicts.'.format(obj.id)

    assert response.status_code == 200
    assert expected_message == data['message']

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.status == ObjectStatus.HALTED


def test_merge_with_conflicts_callback_url_and_resolve(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://schemas.stark-industries.com/schemas/avengers.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

    assert obj.status == ObjectStatus.HALTED
    assert expected_url == obj.extra_data.get('callback_url')
    assert len(conflicts) == 1
    assert obj.extra_data.get('is-update') is True

    # resolve conflicts
    obj.data['$schema'] = record_to_merge['$schema']
    del obj.extra_data['conflicts']

    payload = {
        'id': obj.id,
        'metadata': obj.data,
        '_extra_data': obj.extra_data
    }

    with workflow_app.test_client() as client:
        response = client.put(
            obj.extra_data.get('callback_url'),
            data=json.dumps(payload),
            content_type='application/json',
        )
    assert response.status_code == 200

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    assert obj.status == ObjectStatus.COMPLETED
    assert conflicts is None
    assert obj.extra_data.get('approved') is True
    assert obj.extra_data.get('is-update') is True
    assert obj.extra_data.get('merged') is True


def test_merge_callback_url_with_malformed_workflow(workflow_app, enable_merge_on_update, record_to_merge):
    record_update = {
        '$schema': 'http://schemas.stark-industries.com/schemas/avengers.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [
            {'title': 'Jessica Jones'},
            {'title': 'Luke Cage'},
            {'title': 'Frank Castle'},
        ],
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }

    eng_uuid = start('article', [record_update])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    conflicts = obj.extra_data.get('conflicts')

    expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

    assert obj.status == ObjectStatus.HALTED
    assert expected_url == obj.extra_data.get('callback_url')
    assert len(conflicts) == 1
    assert obj.extra_data.get('is-update') is True

    payload = {
        'id': obj.id,
        'metadata': 'Jessica Jones',
        '_extra_data': 'Frank Castle'
    }

    with workflow_app.test_client() as client:
        response = client.put(
            obj.extra_data.get('callback_url'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    data = json.loads(response.get_data())
    expected_message = 'The workflow request is malformed.'

    assert response.status_code == 400
    assert expected_message == data['message']

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.status == ObjectStatus.HALTED
    assert obj.extra_data.get('callback_url') is not None
    assert obj.extra_data.get('conflicts') is not None
