# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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
import mock
import uuid

import pytest
import requests_mock
from invenio_workflows.errors import WorkflowsError
from mock import MagicMock, patch
from flask import current_app

import requests
from invenio_workflows import workflow_object_class

from inspirehep.modules.records.api import InspireRecord, RecordMetadata

from factories.db.invenio_records import TestRecordMetadata

# FIXME: otherwise this task is not found by Celery.
from inspirehep.modules.orcid.tasks import orcid_push  # noqa: F401
from inspirehep.modules.workflows.tasks.upload import (
    is_stale_data,
    store_root,
    store_record,
)
from inspirehep.modules.workflows.utils import (
    insert_wf_record_source,
    read_wf_record_source,
)
from workflow_utils import build_workflow


@patch('inspirehep.modules.orcid.domain_models.OrcidPusher')
def test_store_record_does_not_raise_in_the_orcid_receiver(mock_attempt_push, app):
    config = {
        'FEATURE_FLAG_ENABLE_ORCID_PUSH': True,
        'RECORDS_SKIP_FILES': False,
    }
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))

    with patch.dict(current_app.config, config):
        obj = workflow_object_class.create({
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature',
            ],
            'authors': [
                {
                    'full_name': 'Patra, Asim',
                    'ids': [
                        {
                            'schema': 'ORCID',
                            'value': '0000-0003-1166-2790',
                        },
                    ],
                },
            ],
            'document_type': [
                'article',
            ],
            'titles': [
                {'title': 'title'},
            ],
        })

        store_record(obj, eng)  # Does not raise.


def test_store_root_new_record(workflow_app):
    config = {
        'FEATURE_FLAG_ENABLE_MERGER': True
    }
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))

    with patch.dict(current_app.config, config):
        head = TestRecordMetadata.create_from_kwargs(index=False, has_pid=False)
        head_uuid = head.record_metadata.id
        record = head.record_metadata.json

        obj = workflow_object_class.create(record)

        root = {
            'version': 'original',
            'acquisition_source': {'source': 'arXiv'}
        }

        extra_data = {
            'head_uuid': str(head_uuid),
            'merger_root': root,
        }

        obj.extra_data = extra_data

        store_root(obj, eng)

        root_entry = read_wf_record_source(head_uuid, 'arxiv')

        assert root_entry.json == root


def test_store_root_update_record(workflow_app):
    config = {
        'FEATURE_FLAG_ENABLE_MERGER': True
    }
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))

    with patch.dict(current_app.config, config):
        head = TestRecordMetadata.create_from_kwargs(index=False, has_pid=False)
        head_uuid = head.record_metadata.id
        record = head.record_metadata.json

        original_root = {
            'version': 'original',
            'acquisition_source': {'source': 'arXiv'},
        }

        update_root = {
            'version': 'updated',
            'acquisition_source': {'source': 'arXiv'},
        }

        insert_wf_record_source(json_data=original_root, record_uuid=head_uuid, source='arxiv')

        obj = workflow_object_class.create(record)

        extra_data = {
            'head_uuid': str(head_uuid),
            'merger_root': update_root,
        }

        obj.extra_data = extra_data

        store_root(obj, eng)

        root_entry = read_wf_record_source(head_uuid, 'arxiv')

        assert root_entry.json == update_root


def test_is_stale_data_is_false(workflow_app):
    head = TestRecordMetadata.create_from_kwargs(index=False, has_pid=False)
    obj = workflow_object_class.create({})
    obj.extra_data['is-update'] = True
    obj.extra_data['head_uuid'] = head.record_metadata.id
    obj.extra_data['head_version_id'] = head.record_metadata.version_id

    assert is_stale_data(obj, None) is False


def test_is_stale_data_is_true(workflow_app):
    head = TestRecordMetadata.create_from_kwargs(index=False, has_pid=False)
    obj = workflow_object_class.create({})
    obj.extra_data['is-update'] = True
    obj.extra_data['head_uuid'] = head.record_metadata.id
    obj.extra_data['head_version_id'] = head.record_metadata.version_id - 1

    assert is_stale_data(obj, None)


def test_is_stale_data_returns_false_if_is_update_is_falsy(workflow_app):
    TestRecordMetadata.create_from_kwargs(index=False, has_pid=False)
    obj = workflow_object_class.create({})
    assert is_stale_data(obj, None) is False


def test_regression_store_record_does_not_commit_when_error(workflow_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'title'}],
    }
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))

    obj = workflow_object_class.create(data)

    record_count = RecordMetadata.query.count()
    assert record_count == 0

    with patch.object(
        InspireRecord,
        'download_documents_and_figures',
        side_effect=Exception
    ):
        # pytest.raises catches the exception and makes the test passing immediately
        try:
            store_record(obj, eng)
        except Exception:
            record_count = RecordMetadata.query.count()
            assert record_count == 0


def test_store_record_inspirehep_api_literature_new(workflow_app):
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature']
    }
    workflow = workflow_object_class.create(record_data)
    workflow.extra_data['is-update'] = False

    expected_head_uuid = str(uuid.uuid4())
    expected_control_number = 111

    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/literature'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL")),
                headers={'content-type': 'application/json'},
                status_code=201,
                json={
                    "metadata": {
                        "control_number": expected_control_number
                    },
                    'uuid': expected_head_uuid
                }
            )
            store_record(workflow, eng)  # not throwing exception
    assert workflow.data['control_number'] == expected_control_number
    assert workflow.extra_data['recid'] == expected_control_number
    assert workflow.extra_data['head_uuid'] == expected_head_uuid
    assert workflow.extra_data['url'] == "http://localhost:5000/record/111"


@mock.patch('inspirehep.modules.workflows.tasks.upload.put_record_to_hep')
def test_store_record_inspirehep_api_literature_new_has_the_if_match_headers(mock_put_record_to_hep, workflow_app):
    expected_control_number = 111
    expected_head_uuid = str(uuid.uuid4())
    expected_version = '"1"'
    mock_put_record_to_hep.return_value = {
        'metadata': {
            'control_number': expected_control_number,
        },
        id: expected_head_uuid
    }

    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature'],
        "control_number": expected_control_number
    }

    workflow = workflow_object_class.create(record_data)
    workflow.extra_data['is-update'] = True
    workflow.extra_data['head_uuid'] = expected_head_uuid
    workflow.extra_data['head_version_id'] = 2
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        store_record(workflow, eng)  # not throwing exception

    assert expected_version == mock_put_record_to_hep.call_args_list[0][1]['headers']['If-Match']
    assert workflow.data['control_number'] == expected_control_number
    assert workflow.extra_data['recid'] == expected_control_number
    assert workflow.extra_data['head_uuid'] == expected_head_uuid
    assert workflow.extra_data['url'] == "http://localhost:5000/record/111"


def test_store_record_inspirehep_api_literature_update_without_cn(workflow_app):
    expected_control_number = 111
    expected_head_uuid = str(uuid.uuid4())

    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature']
    }

    workflow = workflow_object_class.create(record_data)
    workflow.extra_data['is-update'] = True

    workflow.extra_data['head_uuid'] = expected_head_uuid
    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'PUT', '{url}/literature/{cn}'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL"),
                    cn=expected_control_number,
                ),
                headers={'content-type': 'application/json'},
                status_code=200,
                json={
                    "metadata": {
                        "control_number": expected_control_number
                    },
                    'uuid': expected_head_uuid
                }
            )
            with pytest.raises(ValueError):
                store_record(workflow, eng)


def test_store_record_inspirehep_api_author_new(workflow_app):
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        'name': {'value': 'Robert Johnson'}, '_collections': ['Authors']
    }
    expected_control_number = 2222
    expected_head_uuid = str(uuid.uuid4())

    workflow = workflow_object_class.create(record_data)
    workflow.extra_data['is-update'] = False

    eng = MagicMock(workflow_definition=MagicMock(data_type='authors'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/authors'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL")),
                headers={'content-type': 'application/json'},
                status_code=201,
                json={
                    "metadata": {
                        "control_number": expected_control_number
                    },
                    'uuid': expected_head_uuid
                }
            )
            store_record(workflow, eng)  # not throwing exception
    assert workflow.data['control_number'] == expected_control_number
    assert workflow.extra_data['recid'] == expected_control_number
    assert workflow.extra_data['head_uuid'] == expected_head_uuid
    assert workflow.extra_data['url'] == "http://localhost:5000/record/2222"


def test_store_record_inspirehep_api_author_update(workflow_app):
    expected_control_number = 2222
    expected_head_uuid = str(uuid.uuid4())
    expected_head_version_id = 1
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        'name': {'value': 'Robert Johnson'}, '_collections': ['Authors'],
        "control_number": expected_control_number
    }

    workflow = workflow_object_class.create(record_data)
    workflow.extra_data['is-update'] = True

    workflow.extra_data['head_uuid'] = expected_head_uuid
    workflow.extra_data['head_version_id'] = expected_head_version_id
    eng = MagicMock(workflow_definition=MagicMock(data_type='authors'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'PUT', '{url}/authors/{cn}'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL"),
                    cn=expected_control_number,
                ),
                headers={'content-type': 'application/json', "If-Match": '"{}"'.format(expected_head_version_id)},
                status_code=200,
                json={
                    "metadata": {
                        "control_number": expected_control_number
                    },
                    'uuid': expected_head_uuid
                }
            )
            store_record(workflow, eng)  # not throwing exception
    assert workflow.data['control_number'] == expected_control_number
    assert workflow.extra_data['recid'] == expected_control_number
    assert workflow.extra_data['head_uuid'] == expected_head_uuid
    assert workflow.extra_data['url'] == "http://localhost:5000/record/2222"


def test_store_record_inspirehep_api_retries_on_bad_gateway(workflow_app):
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature']
    }
    workflow = workflow_object_class.create({})
    workflow.extra_data['is-update'] = False
    workflow.data = record_data

    expected_head_uuid = str(uuid.uuid4())
    expected_control_number = 222

    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/literature'.format(url=workflow_app.config.get("INSPIREHEP_URL")),
                [
                    {'status_code': 502},
                    {'status_code': 502},
                    {'status_code': 201, 'json': {
                        "metadata": {
                            "control_number": expected_control_number
                        },
                        'uuid': expected_head_uuid
                    }}
                ],
            )
            store_record(workflow, eng)

    assert workflow.data['control_number'] == expected_control_number
    assert workflow.extra_data['recid'] == expected_control_number
    assert workflow.extra_data['head_uuid'] == expected_head_uuid
    assert workflow.extra_data['url'] == "http://localhost:5000/record/222"


def side_effect_requests_post(url, params=None, **kwargs):
    raise requests.exceptions.ConnectionError()


@patch("inspirehep.modules.workflows.tasks.upload.requests.post")
def test_store_record_inspirehep_api_retries_on_connection_error(mock_requests_post, workflow_app):
    mock_requests_post.side_effect = side_effect_requests_post

    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature']
    }
    workflow = workflow_object_class.create({})
    workflow.extra_data['is-update'] = False
    workflow.data = record_data

    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with pytest.raises(requests.exceptions.ConnectionError):
            store_record(workflow, eng)

    assert mock_requests_post.call_count == 5


def test_store_record_inspirehep_api_literature_new_wrong_response_code(workflow_app):
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': 'Follow hour including staff wrong.'}],
        'document_type': ['article'], '_collections': ['Literature']
    }
    workflow = workflow_object_class.create({})
    workflow.extra_data['is-update'] = False
    workflow.data = record_data

    eng = MagicMock(workflow_definition=MagicMock(data_type='hep'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/literature'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL")),
                headers={'content-type': 'application/json'},
                status_code=401,
                json={
                    "message": "Something"
                }
            )
            with pytest.raises(WorkflowsError):
                store_record(workflow, eng)


def test_store_record_inspirehep_api_author_new_wrong_response_code(workflow_app):
    record_data = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        'name': {'value': 'Robert Johnson'}, '_collections': ['Authors']
    }
    workflow = workflow_object_class.create({})
    workflow.extra_data['is-update'] = False
    workflow.data = record_data

    eng = MagicMock(workflow_definition=MagicMock(data_type='authors'))
    with patch.dict(workflow_app.config, {
        'FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT': True,
        'INSPIREHEP_URL': "http://web:8000"
    }):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/authors'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL")),
                headers={'content-type': 'application/json'},
                status_code=401,
                json={
                    "message": "Something"
                }
            )
            with pytest.raises(WorkflowsError):
                store_record(workflow, eng)


@pytest.mark.vcr()
def test_is_stale_data_record_from_hep(workflow_app):
    config = {
        'INSPIREHEP_URL': 'https://inspirebeta.net/api',
        'FEATURE_FLAG_ENABLE_HEP_REST_RECORD_PULL': True,
    }
    with mock.patch.dict(current_app.config, config):
        extra_data = {
            "is-update": True,
            "head_version_id": 1,
        }

        data = {
            "control_number": 1401296,
            "$schema": "https://inspirebeta.net/schemas/records/hep.json"
        }
        wf = build_workflow(data, extra_data=extra_data)
        assert is_stale_data(wf, None) is False
