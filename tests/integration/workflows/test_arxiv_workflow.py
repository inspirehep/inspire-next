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
import os
import pkg_resources
import pytest
import re
import requests_mock
from tempfile import mkstemp

from flask import current_app

from invenio_search import current_search_client as es
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search.api import current_search_client as es
from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
    workflow_object_class,
)
from invenio_workflows.models import WorkflowObjectModel

from inspirehep.modules.refextract.tasks import create_journal_kb_file
from inspirehep.modules.workflows.tasks.actions import normalize_journal_titles
from inspirehep.utils.record_getter import get_db_record

from calls import (
    already_harvested_on_legacy_record,
    do_accept_core,
    do_webcoll_callback,
    do_robotupload_callback,
    generate_record,
)
from mocks import (
    fake_download_file,
    fake_beard_api_request,
    fake_magpie_api_request,
)
from utils import get_halted_workflow


def _delete_record(pid_type, pid_value):
    get_db_record(pid_type, pid_value)._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, pid_value)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


@pytest.fixture(scope='function')
def workflow(workflow_app):
    workflow_object = workflow_object_class.create(
        data={},
        id_user=1,
        data_type="hep"
    )
    workflow_object.save()
    db.session.commit()
    workflow_object.continue_workflow = lambda **args: True

    yield workflow_object

    WorkflowObjectModel.query.filter_by(id=workflow_object.id).delete()
    db.session.commit()


@pytest.fixture(scope='function')
def insert_journals_in_db(workflow_app):
    """Temporarily add few journals in the DB"""
    from inspirehep.modules.migrator.tasks import record_insert_or_replace  # imported here because it is a Celery task

    journal_1 = json.loads(pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'jou_record_refereed.json')))

    journal_2 = json.loads(pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'jou_record_refereed_and_proceedings.json')))

    with db.session.begin_nested():
        record_insert_or_replace(journal_1)
        record_insert_or_replace(journal_2)

    db.session.commit()
    es.indices.refresh('records-journals')

    yield

    _delete_record('jou', 1936475)
    _delete_record('jou', 1936476)
    es.indices.refresh('records-journals')


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link'
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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
    mocked_arxiv_download,
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_beard,
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


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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
def test_harvesting_arxiv_workflow_already_on_legacy(
    mocked_download,
    mocked_is_pdf,
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    workflow_app,
    mocked_external_services
):
    """Test a full harvesting workflow."""
    record, categories = already_harvested_on_legacy_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start('article', [record])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        assert obj.status == ObjectStatus.COMPLETED
        assert 'already-ingested' in obj.extra_data
        assert obj.extra_data['already-ingested']


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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

    response = do_robotupload_callback(
        app=workflow_app,
        workflow_id=obj.id,
        recids=[12345],
    )
    assert response.status_code == 200

    obj = workflow_object_class.get(obj.id)
    assert obj.status == ObjectStatus.WAITING

    response = do_webcoll_callback(app=workflow_app, recids=[12345])
    assert response.status_code == 200

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    # It was accepted
    assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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
    mocked_download_arxiv,
    mocked_api_request_beard,
    mocked_api_request_magpie,
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
    assert update_wf.extra_data['already-ingested'] is False
    assert update_wf.extra_data['already-in-holding-pen'] is True
    assert update_wf.extra_data['previously_rejected'] is False
    assert update_wf.extra_data['stopped-matched-holdingpen-wf'] is True
    assert update_wf.extra_data['is-update'] is False

    old_wf = workflow_object_class.get(obj_id)
    assert old_wf.extra_data['already-ingested'] is False
    assert old_wf.extra_data['already-in-holding-pen'] is False
    assert old_wf.extra_data['previously_rejected'] is False
    assert old_wf.extra_data['stopped-by-wf'] == update_wf.id
    assert old_wf.extra_data.get('approved') is None
    assert old_wf.extra_data['is-update'] is False
    assert old_wf.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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
    mocked_download_arxiv,
    mocked_api_request_beard,
    mocked_api_request_magpie,
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
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
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
    mocked_download_arxiv,
    mocked_api_request_beard,
    mocked_api_request_magpie,
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
        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        # It was accepted
        assert obj.status == ObjectStatus.COMPLETED


def test_normalize_journal_titles_known_journals_with_ref(workflow_app, insert_journals_in_db, workflow):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with mock.patch.dict(current_app.config, config):
        create_journal_kb_file()

        workflow.data = json.loads(pkg_resources.resource_string(
            __name__, os.path.join('fixtures', 'lit_record_known_journals_with_refs.json')))

        normalize_journal_titles(workflow, None)

        assert workflow.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
        assert workflow.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
        assert workflow.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
        assert workflow.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}

        os.close(temporary_fd)
        os.remove(path)


def test_normalize_journal_titles_known_journals_no_ref(workflow_app, insert_journals_in_db, workflow):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with mock.patch.dict(current_app.config, config):
        create_journal_kb_file()

        workflow.data = json.loads(pkg_resources.resource_string(
            __name__, os.path.join('fixtures', 'lit_record_known_journals_with_no_refs.json')))

        normalize_journal_titles(workflow, None)

        assert workflow.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
        assert workflow.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
        assert workflow.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
        assert workflow.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}

        os.close(temporary_fd)
        os.remove(path)


def test_normalize_journal_titles_known_journals_wrong_ref(workflow_app, insert_journals_in_db, workflow):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with mock.patch.dict(current_app.config, config):
        create_journal_kb_file()

        workflow.data = json.loads(pkg_resources.resource_string(
            __name__, os.path.join('fixtures', 'lit_record_known_journals_with_wrong_refs.json')))

        normalize_journal_titles(workflow, None)

        assert workflow.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
        assert workflow.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
        assert workflow.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
        assert workflow.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}

        os.close(temporary_fd)
        os.remove(path)


def test_normalize_journal_titles_unknown_journals_with_ref(workflow_app, insert_journals_in_db, workflow):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with mock.patch.dict(current_app.config, config):
        create_journal_kb_file()

        workflow.data = json.loads(pkg_resources.resource_string(
            __name__, os.path.join('fixtures', 'lit_record_unknown_journals_with_refs.json')))

        normalize_journal_titles(workflow, None)

        assert workflow.data['publication_info'][0]['journal_title'] == 'Unknown1'
        assert workflow.data['publication_info'][2]['journal_title'] == 'Unknown2'
        assert workflow.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/0000000'}
        assert workflow.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1111111'}

        os.close(temporary_fd)
        os.remove(path)


def test_normalize_journal_titles_unknown_journals_no_ref(workflow_app, insert_journals_in_db, workflow):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with mock.patch.dict(current_app.config, config):
        create_journal_kb_file()

        workflow.data = json.loads(pkg_resources.resource_string(
            __name__, os.path.join('fixtures', 'lit_record_unknown_journals_with_no_refs.json')))

        normalize_journal_titles(workflow, None)

        assert workflow.data['publication_info'][0]['journal_title'] == 'Unknown1'
        assert workflow.data['publication_info'][2]['journal_title'] == 'Unknown2'
        assert 'journal_record' not in workflow.data['publication_info'][0]
        assert 'journal_record' not in workflow.data['publication_info'][2]

        os.close(temporary_fd)
        os.remove(path)
