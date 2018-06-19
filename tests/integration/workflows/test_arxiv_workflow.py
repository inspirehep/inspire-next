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

"""Tests for arXiv workflows."""

from __future__ import absolute_import, division, print_function

import json
import mock
import pytest

from invenio_search import current_search_client as es
from invenio_db import db
from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    WorkflowObject,
    start,
    workflow_object_class,
)
from invenio_workflows.errors import WorkflowsError
from jsonschema import ValidationError

from calls import (
    core_record,
    do_accept_core,
    do_resolve_matching,
    do_robotupload_callback,
    do_validation_callback,
    do_webcoll_callback,
    generate_record,
)
from mocks import (
    fake_beard_api_request,
    fake_download_file,
    fake_magpie_api_request,
)
from utils import get_halted_workflow
from inspirehep.modules.workflows.tasks.matching import _get_hep_record_brief


@pytest.fixture
def enable_fuzzy_matcher(workflow_app):
    with mock.patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_FUZZY_MATCHER': True}):
        yield


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link'
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_rejected(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_beard_api,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app,
        extra_config=extra_config,
        record=record,
    )

    obj.extra_data["approved"] = False
    obj.save()
    db.session.commit()

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj_id = obj.id
    obj.continue_workflow()

    obj = workflow_object_class.get(obj_id)
    # It was rejected
    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data["approved"] is False


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_core_record_auto_accepted(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record, categories = core_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start('article', [record])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        assert obj.extra_data['approved'] is True
        assert obj.extra_data['auto-approved'] is True
        assert obj.data['core'] is True


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.utils.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.matching.match',
    return_value=iter([]),
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_accepted(
    mocked_refextract_extract_refs,
    mocked_matching_match,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download_utils,
    mocked_download_arxiv,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()
    """Test a full harvesting workflow."""

    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app,
        record=record,
    )

    do_accept_core(
        app=workflow_app,
        workflow_id=obj.id,
    )

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    assert obj.status == ObjectStatus.WAITING

    do_robotupload_callback(
        app=workflow_app,
        workflow_id=obj.id,
        recids=[12345],
    )

    obj = workflow_object_class.get(obj.id)
    assert obj.status == ObjectStatus.WAITING

    do_webcoll_callback(app=workflow_app, recids=[12345])

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    # It was accepted
    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data['approved'] is True


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_stops_pending_wf(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()

    eng_uuid = start('article', [record])
    es.indices.refresh('holdingpen-hep')
    eng = WorkflowEngine.from_uuid(eng_uuid)
    old_wf = eng.objects[0]
    obj_id = old_wf.id

    assert old_wf.status == ObjectStatus.HALTED
    assert old_wf.extra_data['previously_rejected'] is False

    record2 = record
    record['titles'][0]['title'] = 'This is an update that will match the wf in the holdingpen'
    eng_uuid2 = start('article', [record2])
    es.indices.refresh('holdingpen-hep')
    eng2 = WorkflowEngine.from_uuid(eng_uuid2)
    update_wf = eng2.objects[0]

    assert update_wf.status == ObjectStatus.HALTED
    assert update_wf.extra_data['already-in-holding-pen'] is True
    assert update_wf.extra_data['previously_rejected'] is False
    assert update_wf.extra_data['stopped-matched-holdingpen-wf'] is True
    assert update_wf.extra_data['is-update'] is False

    old_wf = workflow_object_class.get(obj_id)
    assert old_wf.extra_data['already-in-holding-pen'] is False
    assert old_wf.extra_data['previously_rejected'] is False
    assert old_wf.extra_data['stopped-by-wf'] == update_wf.id
    assert old_wf.extra_data.get('approved') is None
    assert old_wf.extra_data['is-update'] is False
    assert old_wf.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_previously_rejected_wf_stop(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()

    eng_uuid = start('article', [record])
    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj_id = eng.objects[0].id
    obj = workflow_object_class.get(obj_id)
    obj.extra_data["approved"] = False  # reject record
    obj.continue_workflow()
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data.get('approved') is False

    es.indices.refresh('holdingpen-hep')

    record['titles'][0]['title'] = 'This is an update that will match the wf in the holdingpen'
    # this workflow matches in the holdingpen and stops because the
    # matched one was rejected
    eng_uuid = start('article', [record])
    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj2 = eng.objects[0]

    assert obj2.extra_data['already-in-holding-pen'] is False
    assert obj2.extra_data['previously_rejected'] is True
    assert obj2.extra_data['previously_rejected_matches'] == [obj_id]


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_different_sources_continues(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()

    eng_uuid = start('article', [record])
    es.indices.refresh('holdingpen-hep')
    eng = WorkflowEngine.from_uuid(eng_uuid)
    wf_to_match = eng.objects[0].id
    obj = workflow_object_class.get(wf_to_match)
    assert obj.status == ObjectStatus.HALTED
    # generated wf pending in holdingpen

    record['titles'][0]['title'] = 'This is an update that will match the wf in the holdingpen'
    record['acquisition_source']['source'] = 'but not the source'
    # this workflow matches in the holdingpen but continues because has a
    # different source
    eng_uuid = start('article', [record])
    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.extra_data['already-in-holding-pen'] is True
    assert obj.extra_data['holdingpen_matches'] == [wf_to_match]
    assert obj.extra_data['previously_rejected'] is False
    assert not obj.extra_data.get('stopped-matched-holdingpen-wf')


def test_article_workflow_stops_when_record_is_not_valid(workflow_app):
    invalid_record = {
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
    }

    obj = workflow_object_class.create(
        data=invalid_record,
        data_type='hep',
        id_user=1,
    )
    obj_id = obj.id

    with pytest.raises(ValidationError):
        start('article', invalid_record, obj_id)

    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.ERROR
    assert '_error_msg' in obj.extra_data
    assert 'required' in obj.extra_data['_error_msg']

    expected_url = 'http://localhost:5000/callback/workflows/resolve_validation_errors'

    assert expected_url == obj.extra_data['callback_url']
    assert obj.extra_data['validation_errors']
    assert 'message' in obj.extra_data['validation_errors'][0]
    assert 'path' in obj.extra_data['validation_errors'][0]


def test_article_workflow_continues_when_record_is_valid(workflow_app):
    valid_record = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
    }

    eng_uuid = start('article', [valid_record])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.status != ObjectStatus.ERROR
    assert '_error_msg' not in obj.extra_data


@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
def test_update_exact_matched_goes_trough_the_workflow(
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_beard,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db
):
    record = record_from_db
    eng_uuid = start('article', [record])
    obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
    obj = workflow_object_class.get(obj_id)

    assert obj.extra_data['already-in-holding-pen'] is False
    assert obj.extra_data['holdingpen_matches'] == []
    assert obj.extra_data['previously_rejected'] is False
    assert not obj.extra_data.get('stopped-matched-holdingpen-wf')
    assert obj.extra_data['is-update']
    assert obj.extra_data['exact-matched']
    assert obj.extra_data['matches']['exact'] == [record.get('control_number')]
    assert obj.extra_data['matches']['approved'] == record.get('control_number')
    assert obj.extra_data['approved']
    assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
def test_fuzzy_matched_goes_trough_the_workflow(
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_beard,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
    enable_fuzzy_matcher,
):
    """Test update article fuzzy matched.

    In this test the `WorkflowObject.continue_workflow` is mocked because in
    the test suite celery is run in eager mode. This prevents celery to switch
    back from the api context to the app context, generating errors during
    the workflow execution. The patched version of `continue_workflow` uses
    the correct application context to run the workflow.
    """
    def continue_wf_patched_context(workflow_app):
        workflow_object_class._custom_continue = workflow_object_class.continue_workflow

        def custom_continue_workflow(self, *args, **kwargs):
            with workflow_app.app_context():
                self._custom_continue(*args, **kwargs)

        return custom_continue_workflow

    es_query = {
        'algorithm': [
            {
                'queries': [
                    {
                        'path': 'report_numbers.value',
                        'search_path': 'report_numbers.value.raw',
                        'type': 'exact',
                    },
                ],
            },
        ],
        'doc_type': 'hep',
        'index': 'records-hep',
    }

    record = record_from_db
    expected_brief = _get_hep_record_brief(record)
    del record['arxiv_eprints']
    rec_id = record['control_number']

    with mock.patch.dict(workflow_app.config['FUZZY_MATCH'], es_query):
        eng_uuid = start('article', [record])

    obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.HALTED  # for matching approval
    obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
    obj = workflow_object_class.get(obj_id)

    assert obj.extra_data['already-in-holding-pen'] is False
    assert obj.extra_data['holdingpen_matches'] == []
    assert obj.extra_data['matches']['fuzzy'][0] == expected_brief

    WorkflowObject.continue_workflow = continue_wf_patched_context(workflow_app)
    do_resolve_matching(workflow_app, obj.id, rec_id)

    obj = workflow_object_class.get(obj_id)
    assert obj.extra_data['matches']['approved'] == rec_id
    assert obj.extra_data['fuzzy-matched']
    assert obj.extra_data['is-update']
    assert obj.extra_data['approved']

    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.COMPLETED


def test_validation_error_callback_with_a_valid(workflow_app):
    valid_record = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
    }

    eng_uuid = start('article', [valid_record])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    assert obj.status != ObjectStatus.ERROR

    response = do_validation_callback(
        workflow_app,
        obj.id,
        obj.data,
        obj.extra_data
    )

    expected_error_code = 'WORKFLOW_NOT_IN_ERROR_STATE'
    data = json.loads(response.get_data())

    assert response.status_code == 400
    assert expected_error_code == data['error_code']


def test_validation_error_callback_with_validation_error(workflow_app):
    invalid_record = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
        'preprint_date': 'Jessica Jones'
    }

    obj = workflow_object_class.create(
        data=invalid_record,
        data_type='hep',
        id_user=1,
    )
    obj_id = obj.id

    with pytest.raises(ValidationError):
        start('article', invalid_record, obj_id)

    assert obj.status == ObjectStatus.ERROR

    response = do_validation_callback(
        workflow_app,
        obj.id,
        obj.data,
        obj.extra_data
    )

    expected_message = 'Validation error.'
    expected_error_code = 'VALIDATION_ERROR'
    data = json.loads(response.get_data())

    assert response.status_code == 400
    assert expected_error_code == data['error_code']
    assert expected_message == data['message']

    assert data['workflow']['_extra_data']['callback_url']
    assert len(data['workflow']['_extra_data']['validation_errors']) == 1


def test_validation_error_callback_with_missing_worfklow(workflow_app):
    invalid_record = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
    }

    eng_uuid = start('article', [invalid_record])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    response = do_validation_callback(
        workflow_app,
        1111,
        obj.data,
        obj.extra_data
    )

    data = json.loads(response.get_data())
    expected_message = 'The workflow with id "1111" was not found.'
    expected_error_code = 'WORKFLOW_NOT_FOUND'

    assert response.status_code == 404
    assert expected_error_code == data['error_code']
    assert expected_message == data['message']


def test_validation_error_callback_with_malformed_with_invalid_types(workflow_app):
    invalid_record = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'A title'},
        ],
    }

    eng_uuid = start('article', [invalid_record])

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    response = do_validation_callback(
        workflow_app,
        # id
        'Alias Investigations',
        obj.data,
        # extra_data
        'Jessica Jones'
    )
    data = json.loads(response.get_data())
    expected_message = 'The workflow request is malformed.'
    expected_error_code = 'MALFORMED'

    assert response.status_code == 400
    assert expected_error_code == data['error_code']
    assert expected_message == data['message']
    assert 'errors' in data


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_keep_previously_rejected_from_fully_harvested_category_is_auto_approved(
        mocked_refextract_extract_refs,
        mocked_api_request_magpie,
        mocked_api_request_beard,
        mocked_is_pdf_link,
        mocked_package_download,
        mocked_arxiv_download,
        workflow_app,
        mocked_external_services,
):
    record, categories = core_record()
    obj = workflow_object_class.create(
        data=record,
        status=ObjectStatus.COMPLETED,
        data_type='hep',
    )
    obj.extra_data['approved'] = False  # reject it
    obj.save()
    es.indices.refresh('holdingpen-hep')

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start('article', [record])
            eng = WorkflowEngine.from_uuid(workflow_uuid)
            obj2 = eng.processed_objects[0]
            assert obj2.extra_data['auto-approved']
            assert len(obj2.extra_data['previously_rejected_matches']) > 0
            assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_previously_rejected_from_not_fully_harvested_category_is_not_auto_approved(
        mocked_refextract_extract_refs,
        mocked_api_request_magpie,
        mocked_api_request_beard,
        mocked_is_pdf_link,
        mocked_package_download,
        mocked_arxiv_download,
        workflow_app,
        mocked_external_services,
):
    record, categories = core_record()
    record['arxiv_eprints'][0]['categories'] = ['q-bio.GN']

    obj = workflow_object_class.create(
        data=record,
        status=ObjectStatus.COMPLETED,
        data_type='hep',
    )
    obj.extra_data['approved'] = False  # reject it
    obj.save()
    es.indices.refresh('holdingpen-hep')

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start('article', [record])
            eng = WorkflowEngine.from_uuid(workflow_uuid)
            obj2 = eng.processed_objects[0]
            assert not obj2.extra_data['auto-approved']
            assert len(obj2.extra_data['previously_rejected_matches']) > 0
            assert obj2.status == ObjectStatus.COMPLETED


def test_match_wf_in_error_goes_in_error_state(workflow_app):
    record = generate_record()

    obj = workflow_object_class.create(data=record, data_type='hep')
    obj.status = ObjectStatus.ERROR
    obj.save()
    es.indices.refresh('holdingpen-hep')

    with pytest.raises(WorkflowsError):
        start('article', record)


def test_match_wf_in_error_goes_in_initial_state(workflow_app):
    record = generate_record()

    obj = workflow_object_class.create(data=record, data_type='hep')
    obj.status = ObjectStatus.INITIAL
    obj.save()
    es.indices.refresh('holdingpen-hep')

    with pytest.raises(WorkflowsError):
        start('article', record)
