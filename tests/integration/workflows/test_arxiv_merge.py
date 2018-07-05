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

import copy
import json
import pytest

from mock import patch
from mocks import (
    fake_beard_api_request,
    fake_magpie_api_request,
)

from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
)

from inspirehep.modules.workflows.utils import (
    insert_wf_record_source,
    read_all_wf_record_sources,
    read_wf_record_source,
)

from factories.db.invenio_records import TestRecordMetadata


RECORD_SKELETON = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'A record title.'
        },
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
}

RECORD_WITHOUT_ACQUISITION_SOURCE_AND_WITH_CONFLICTS = copy.deepcopy(RECORD_SKELETON)
RECORD_WITHOUT_ACQUISITION_SOURCE_AND_WITH_CONFLICTS.update({
    'collaborations': [
        {
            'record':
                {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                },
            'value': 'ALICE'
        },
    ],
})

RECORD_WITHOUT_ACQUISITION_SOURCE_AND_NO_CONFLICTS = copy.deepcopy(RECORD_SKELETON)

ARXIV_RECORD_WITHOUT_CONFLICTS = copy.deepcopy(RECORD_SKELETON)
ARXIV_RECORD_WITHOUT_CONFLICTS.update({'acquisition_source': {'source': 'arXiv'}})

ARXIV_RECORD_WITH_CONFLICTS = copy.deepcopy(RECORD_SKELETON)
ARXIV_RECORD_WITH_CONFLICTS.update({
    'acquisition_source': {'source': 'arXiv'},
    'collaborations': [
        {
            'record':
                {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                },
            'value': 'ALICE'
        },
    ],
})


@pytest.fixture
def enable_merge_on_update(workflow_app):
    with patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_MERGER': True}):
        yield


@pytest.fixture
def disable_file_upload(workflow_app):
    with patch.dict(workflow_app.config, {'RECORDS_SKIP_FILES': True}):
        yield


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_handles_remove_list_items_conflicts(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.PublisherOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITHOUT_CONFLICTS)
        record_update.update({
            'acquisition_source': {'source': 'publisher'},
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints'),
            'book_series': [{'title': 'Lectures in Testing', 'volume': '3'}],
        })

        publisher_root = copy.deepcopy(RECORD_SKELETON)
        publisher_root.update({
            'acquisition_source': {'source': 'publisher'},
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints'),
            'book_series': [{'title': 'IEEE Nucl.Sci.Symp.Conf.Rec.', 'volume': '1'},
                            {'title': 'CMS Web-Based Monitoring', 'volume': '2'},
                            {'title': 'Lectures in Testing', 'volume': '3'}],
        })

        insert_wf_record_source(json=publisher_root, record_uuid=factory.record_metadata.id, source='publisher')

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')
        assert obj.status == ObjectStatus.HALTED
        assert conflicts == [
            {
                'path': '/book_series',
                'op': 'remove',
                'value': None,
                '$type': u'REMOVE_FIELD'
            }
        ]

        assert obj.extra_data.get('callback_url') is not None
        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_with_disabled_merge_on_update_feature_flag(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
):

    with patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_MERGER': False}):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITHOUT_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.COMPLETED

        assert obj.extra_data.get('callback_url') is None
        assert obj.extra_data.get('conflicts') is None
        assert obj.extra_data.get('merged') is True
        assert obj.extra_data.get('merger_root') is None
        assert obj.extra_data.get('is-update') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_handles_update_without_acquisition_source_and_acts_as_rootless(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.PublisherOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(RECORD_WITHOUT_ACQUISITION_SOURCE_AND_NO_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        assert obj.status == ObjectStatus.COMPLETED
        assert not conflicts

        assert obj.extra_data.get('callback_url') is None
        assert obj.extra_data.get('is-update') is True

        # source us unknown, so no new root is saved.
        roots = read_all_wf_record_sources(factory.record_metadata.id)
        assert not roots


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_handles_update_without_acquisition_source_and_acts_as_rootless(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.PublisherOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(RECORD_WITHOUT_ACQUISITION_SOURCE_AND_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        # By default the root is {}.

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')
        assert obj.status == ObjectStatus.HALTED
        assert len(conflicts) == 2

        assert obj.extra_data.get('callback_url') is not None
        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_rootful(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        # By default the root is {}.

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')
        assert obj.status == ObjectStatus.HALTED
        assert len(conflicts) == 1

        assert obj.extra_data.get('callback_url') is not None
        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_rootful(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        arxiv_root = copy.deepcopy(RECORD_SKELETON)
        arxiv_root.update({
            'acquisition_source': {'source': 'arXiv'},
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints'),
            'collaborations': [
                {
                    'record':
                        {
                            '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                        },
                    'value': 'ALICE'
                },
            ],
        })

        insert_wf_record_source(json=arxiv_root, record_uuid=factory.record_metadata.id, source='arxiv')

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        assert obj.status == ObjectStatus.COMPLETED
        assert not conflicts

        assert obj.extra_data.get('callback_url') is None
        assert obj.extra_data.get('is-update') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_callback_url(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITHOUT_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.COMPLETED
        assert conflicts is None
        assert obj.extra_data.get('is-update') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update

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


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_callback_url(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

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

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_callback_url_and_resolve(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

        # resolve conflicts
        obj.data['collaborations'] = factory.record_metadata.json.get('collaborations')
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

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update


@patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_merge_callback_url_with_malformed_workflow(
        mocked_api_request_magpie,
        mocked_beard_api,
        workflow_app,
        mocked_external_services,
        disable_file_upload,
        enable_merge_on_update,
):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json', index_name='records-hep')

        record_update = copy.deepcopy(ARXIV_RECORD_WITH_CONFLICTS)
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

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
        assert obj.extra_data['merger_root'] is not None

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None
