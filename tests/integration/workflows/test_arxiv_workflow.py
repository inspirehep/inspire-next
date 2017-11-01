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

import mock
import re
import requests_mock

from invenio_db import db
from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
    workflow_object_class,
)

from calls import (
    already_harvested_on_legacy_record,
    do_accept_core,
    do_webcoll_callback,
    do_robotupload_callback,
    generate_record
)
from mocks import (
    fake_download_file,
    fake_beard_api_request,
    fake_magpie_api_request,
)
from utils import get_halted_workflow


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
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_rejected(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download,
    small_app,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid = None
    with small_app.app_context():
        workflow_uuid, eng, obj = get_halted_workflow(
            app=small_app,
            extra_config=extra_config,
            record=record,
        )

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = False
        # obj.extra_data["core"] = True
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
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_already_on_legacy(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download,
    small_app
):
    """Test a full harvesting workflow."""
    record, categories = already_harvested_on_legacy_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': categories,
    }
    with small_app.app_context():
        with mock.patch.dict(small_app.config, extra_config):
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
):
    record = generate_record()
    """Test a full harvesting workflow."""
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer|localhost).*'),
            real_http=True,
        )
        requests_mocker.register_uri(
            'POST',
            re.compile(
                'https?://localhost:1234.*',
            ),
            text=u'[INFO]',
            status_code=200,
        )

        workflow_uuid, eng, obj = get_halted_workflow(
            app=workflow_app,
            extra_config={'PRODUCTION_MODE': False},
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
