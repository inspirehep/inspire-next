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

import mock
import pytest
import json
from inspire_schemas.readers import LiteratureReader
from invenio_workflows import ObjectStatus, workflow_object_class

from inspirehep.modules.workflows.tasks.manual_merging import save_roots
from inspirehep.modules.workflows.utils import (
    _get_headers_for_hep_root_table_request,
    insert_wf_record_source,
    read_wf_record_source,
)
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.workflows.manual_merge import start_merger
from inspirehep.utils.record_getter import RecordGetterError
from utils import override_config
import requests_mock
from calls import do_resolve_manual_merge_wf


def fake_record(title, rec_id):
    return {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles': [{'title': title}],
        '_collections': ['Literature'],
        'document_type': ['article'],
        'acquisition_source': {'source': 'arxiv'},
        'arxiv_eprints': [{'value': '1701.01431', 'categories': ['cs']}],
        'control_number': rec_id
    }


@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.store_records', side_effect=None)
@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.put_record_to_hep', side_effect=None)
def test_manual_merge_existing_records(mock_put_record_to_hep, mock_store_records, workflow_app):

    json_head = fake_record('This is the HEAD', 1)
    json_update = fake_record('While this is the update', 2)

    # this two fields will create a merging conflict
    json_head['core'] = True
    json_update['core'] = False

    head = InspireRecord.create_or_update(json_head, skip_files=False)
    head.commit()
    update = InspireRecord.create_or_update(json_update, skip_files=False)
    update.commit()
    head_id = head.id
    update_id = update.id

    obj_id = start_merger(
        head_id=1,
        update_id=2,
        current_user_id=1,
    )

    do_resolve_manual_merge_wf(workflow_app, obj_id)

    mock_put_record_to_hep.assert_called()
    assert '"1"' == mock_put_record_to_hep.call_args[1]['headers']['If-Match']

    # retrieve it again, otherwise Detached Instance Error
    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.COMPLETED
    assert 'deleted_records' in obj.data
    assert obj.extra_data['approved'] is True
    assert obj.extra_data['auto-approved'] is False
    assert 'callback_url' in obj.extra_data

    # no root present before
    last_root = read_wf_record_source(head_id, 'arxiv')
    assert last_root is None

    update_source = LiteratureReader(update).source
    root_update = read_wf_record_source(update_id, update_source)
    assert root_update is None


@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.store_records', side_effect=None)
@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.put_record_to_hep', side_effect=None)
def test_manual_merge_existing_records_with_callback_with_conflicts(mock_put_record_to_hep, mock_store_records, workflow_app):

    json_head = fake_record('This is the HEAD', 1)
    json_update = fake_record('While this is the update', 2)

    # this two fields will create a merging conflict
    json_head['core'] = True
    json_update['core'] = False

    head = InspireRecord.create_or_update(json_head, skip_files=False)
    head.commit()
    update = InspireRecord.create_or_update(json_update, skip_files=False)
    update.commit()
    head_id = head.id
    update_id = update.id

    obj_id = start_merger(
        head_id=1,
        update_id=2,
        current_user_id=1,
    )
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.HALTED

    expected_message = 'Workflow {} has been saved with conflicts.'.format(obj.id)

    with workflow_app.test_client() as client:
        response = client.put(
            '/callback/workflows/resolve_merge_conflicts',
            content_type='application/json',
            data=json.dumps({
                'id': obj_id,
                '_extra_data': obj.extra_data,
                'metadata': obj.data
            })
        )

    data = json.loads(response.get_data())
    assert 200 == response.status_code
    assert expected_message == data['message']
    # retrieve it again, otherwise Detached Instance Error
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.HALTED
    assert 'callback_url' in obj.extra_data
    assert 'conflicts' in obj.extra_data
    # no root present before
    last_root = read_wf_record_source(head_id, 'arxiv')
    assert last_root is None

    update_source = LiteratureReader(update).source
    root_update = read_wf_record_source(update_id, update_source)
    assert root_update is None


@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.store_records', side_effect=None)
@mock.patch('inspirehep.modules.workflows.tasks.manual_merging.put_record_to_hep', side_effect=None)
def xtest_manual_merge_existing_records_with_callback_without_conflicts(mock_put_record_to_hep, mock_store_records, workflow_app):

    json_head = fake_record('This is the HEAD', 1)
    json_update = fake_record('While this is the update', 2)

    # this two fields will create a merging conflict
    json_head['core'] = True
    json_update['core'] = False

    head = InspireRecord.create_or_update(json_head, skip_files=False)
    head.commit()
    update = InspireRecord.create_or_update(json_update, skip_files=False)
    update.commit()
    head_id = head.id
    update_id = update.id

    obj_id = start_merger(
        head_id=1,
        update_id=2,
        current_user_id=1,
    )
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.HALTED
    assert 'http://localhost:5000/callback/workflows/resolve_merge_conflicts' == obj.extra_data['callback_url']

    obj.extra_data['conflicts'] = []
    expected_message = 'Workflow {} is continuing.'.format(obj.id)
    metadata = obj.data

    extra_data = obj.extra_data
    with workflow_app.test_client() as client:
        response = client.put(
            '/callback/workflows/resolve_merge_conflicts',
            content_type='application/json',
            data=json.dumps({
                'id': obj_id,
                '_extra_data': extra_data,
                'metadata': metadata
            })
        )

    data = json.loads(response.get_data())
    assert 200 == response.status_code
    assert expected_message == data['message']
    # retrieve it again, otherwise Detached Instance Error
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.COMPLETED
    assert 'callback_url' not in obj.extra_data
    assert 'conflicts' not in obj.extra_data

    # no root present before
    last_root = read_wf_record_source(head_id, 'arxiv')
    assert last_root is None

    update_source = LiteratureReader(update).source
    root_update = read_wf_record_source(update_id, update_source)
    assert root_update is None


def test_manual_merge_with_none_record(workflow_app):

    json_head = fake_record('This is the HEAD', 1)

    head = InspireRecord.create_or_update(json_head, skip_files=False)
    head.commit()
    non_existing_id = 123456789

    with pytest.raises(RecordGetterError):
        start_merger(
            head_id=1,
            update_id=non_existing_id,
            current_user_id=1,
        )


def test_save_roots(workflow_app):

    head = InspireRecord.create_or_update(fake_record('title1', 123), skip_files=False)
    head.commit()
    update = InspireRecord.create_or_update(fake_record('title2', 456), skip_files=False)
    update.commit()

    obj = workflow_object_class.create(
        data={},
        data_type='hep'
    )
    obj.extra_data['head_uuid'] = str(head.id)
    obj.extra_data['update_uuid'] = str(update.id)
    obj.save()

    # Union: keep the most recently created/updated root from each source.
    insert_wf_record_source(json_data={'version': 'original'}, record_uuid=head.id, source='arxiv')

    insert_wf_record_source(json_data={'version': 'updated'}, record_uuid=update.id, source='arxiv')

    insert_wf_record_source(json_data={'version': 'updated'}, record_uuid=update.id, source='publisher')

    save_roots(obj, None)

    arxiv_rec = read_wf_record_source(head.id, 'arxiv')
    assert arxiv_rec.json == {'version': 'updated'}

    pub_rec = read_wf_record_source(head.id, 'publisher')
    assert pub_rec.json == {'version': 'updated'}

    assert not read_wf_record_source(update.id, 'arxiv')
    assert not read_wf_record_source(update.id, 'publisher')


def test_save_roots_using_hep_root_table_api(workflow_app):
    with override_config(
        FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP=True, INSPIREHEP_URL="http://web:8000/api"
    ):
        head = InspireRecord.create_or_update(
            fake_record("title1", 123), skip_files=False
        )
        head.commit()
        update = InspireRecord.create_or_update(
            fake_record("title2", 456), skip_files=False
        )
        update.commit()

        obj = workflow_object_class.create(data={}, data_type="hep")
        obj.extra_data["head_uuid"] = str(head.id)
        obj.extra_data["update_uuid"] = str(update.id)
        obj.save()

        original_data = dict(
            json_data={"version": "original"}, record_uuid=str(head.id), source="arxiv"
        )
        arxiv_update_data = dict(
            json_data={"version": "updated"}, record_uuid=str(update.id), source="arxiv"
        )
        publisher_update_data = dict(
            json_data={"version": "updated"},
            record_uuid=str(update.id),
            source="publisher",
        )
        workflow_sources_head = [
            {
                "created": "20-02-2012 14:35:34.2345",
                "updated": "20-02-2012 14:35:34.2345",
                "json": {"version": "original"},
                "record_uuid": str(head.id),
                "source": "arxiv",
            }
        ]
        workflow_sources_update = [
            {
                "created": "20-02-2012 14:35:34.2345",
                "updated": "20-02-2012 14:35:34.2345",
                "json": {"version": "updated"},
                "record_uuid": str(update.id),
                "source": "arxiv",
            },
            {
                "created": "20-02-2012 15:35:34.2345",
                "updated": "20-02-2012 15:35:34.2345",
                "json": {"version": "updated"},
                "record_uuid": str(update.id),
                "source": "publisher",
            },
        ]
        with requests_mock.Mocker() as request_mocker:
            request_mocker.register_uri(
                "POST",
                "http://web:8000/api/literature/workflows_record_sources",
                json={
                    "message": "workflow source for record {record_uuid} and source {source} added".format(
                        record_uuid=(head.id), source="arxiv"
                    )
                },
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            request_mocker.register_uri(
                "POST",
                "http://web:8000/api/literature/workflows_record_sources",
                json={
                    "message": "workflow source for record {record_uuid} and source {source} added".format(
                        record_uuid=(update.id), source="arxiv"
                    )
                },
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            request_mocker.register_uri(
                "POST",
                "http://web:8000/api/literature/workflows_record_sources",
                json={
                    "message": "workflow source for record {record_uuid} and source {source} added".format(
                        record_uuid=(update.id), source="publisher"
                    )
                },
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            request_mocker.register_uri(
                "GET",
                "http://web:8000/api/literature/workflows_record_sources",
                json={"workflow_sources": workflow_sources_head},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            request_mocker.register_uri(
                "GET",
                "http://web:8000/api/literature/workflows_record_sources",
                json={"workflow_sources": workflow_sources_update},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )

            request_mocker.register_uri(
                "DELETE",
                "http://web:8000/api/literature/workflows_record_sources",
                json={"message": "Record succesfully deleted"},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )

            request_mocker.register_uri(
                "POST",
                "http://web:8000/api/literature/workflows_record_sources",
                json={
                    "message": "workflow source for record {record_uuid} and source {source} added".format(
                        record_uuid=arxiv_update_data["record_uuid"],
                        source=arxiv_update_data["source"],
                    )
                },
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )

            request_mocker.register_uri(
                "POST",
                "http://web:8000/api/literature/workflows_record_sources",
                json={
                    "message": "workflow source for record {record_uuid} and source {source} added".format(
                        record_uuid=publisher_update_data["record_uuid"],
                        source=publisher_update_data["source"],
                    )
                },
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )

            # Union: keep the most recently created/updated root from each source.
            # each request should result in status code 200
            insert_wf_record_source(**original_data)

            insert_wf_record_source(**arxiv_update_data)

            insert_wf_record_source(**publisher_update_data)

            assert save_roots(obj, None) is None
