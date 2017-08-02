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

import datetime
import json
import mock
import os
import pkg_resources
import pytest
import re
import sys
import requests_mock

from dojson.contrib.marc21.utils import create_record

from invenio_search import current_search_client as es
from invenio_db import db
from invenio_records.models import RecordMetadata
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

from inspire_dojson.hep import hep
from inspirehep.modules.converter.xslt import convert
from inspirehep.modules.pidstore.minters import inspire_recid_minter

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import (
    store_root_json,
    retrieve_root_json,
)
from inspirehep.utils.record import get_source
from utils import get_halted_workflow


def read_file(test_dir, file_name):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(base_dir, test_dir, file_name)) as f:
        return json.loads(f.read())


def create_head_record():
    head = read_file('fixtures', 'merger_head.json')
    record = InspireRecord.create(head)
    inspire_recid_minter(str(record.id), record)
    return record.id


@pytest.fixture
def record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_with_plots.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    json_data = hep.do(record_marc)

    if 'preprint_date' in json_data:
        json_data['preprint_date'] = datetime.date.today().isoformat()

    return json_data


@pytest.fixture
def to_accept_record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_to_accept.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    json_data = hep.do(record_marc)

    return json_data


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link'
)
def get_halted_workflow_merge(cls, app, record, extra_config=None):
    extra_config = extra_config or {}
    with mock.patch.dict(app.config, extra_config):
        workflow_uuid = start('article', [record])

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    return workflow_uuid, eng, obj


@mock.patch(
    'inspirehep.modules.workflows.utils.download_file_to_workflow',
    side_effect=fake_download_file,
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
    mocked_download,
    mocked_arxiv_download,
    mocked_api_request_beard,
    mocked_api_request_magpie,
    mocked_refextract_extract_refs,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""

    record = generate_record()
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid = None
    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app,
        extra_config=extra_config,
        record=record,
    )

    obj.remove_action()
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
    workflow_app,
    mocked_external_services
):
    """Test a full harvesting workflow."""
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start(
                'article',
                [
                    already_harvested_on_legacy_record()
                ]
            )

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
    'inspirehep.modules.workflows.tasks.matching.search',
    return_value=[],
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_accepted(
    mocked_refextract_extract_refs,
    mocked_matching_search,
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
    'inspirehep.modules.workflows.tasks.matching.search',
    return_value=[],
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.matching.already_harvested',
    return_value=False,
)
def test_merge_with_already_existing_article_in_the_db(
    mocked_refextract_extract_refs,
    mocked_matching_search,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download_utils,
    mocked_download_arxiv,
    mocked_already_harvested,
    workflow_app,
    mocked_external_services,
):
    """Test a full merging for an article."""
    def _setup_root_record(head_record_id):
        # store root
        original_root = read_file('fixtures', 'merger_root.json')
        store_root_json(
            record_uuid=head_record_id,
            source='arXiv',
            json=original_root,
        )
        db.session.commit()

    def _remove_uuid_authors(record):
        for author in record['authors']:
            if author.get('uuid'):
                del author['uuid']
        return record

    def _remove_buckets_version_id_files(record):
        for file in record['_files']:
            if file.get('version_id'):
                del file['version_id']
            if file.get('bucket'):
                del file['bucket']
            if file.get('checksum'):
                del file['checksum']
        return record

    def _replace_path_fft(record):
        for fft in record['_fft']:
            fft['path'] = u'generic/url/for/a/path'
        return record

    # With the functions: `_remove_uuid_authors` and `_remove_buckets_version_id_files`
    # authors.uuid, _files.version_id and _files.bucket are removed because are
    # manipulated during the workflow and are not relevant for the current test
    head_uuid = create_head_record()
    _setup_root_record(head_record_id=head_uuid)

    # refresh hep index in order to make head ready for the workflow
    es.indices.refresh('records-hep')

    update = read_file('fixtures', 'merger_update.json')

    # this function starts the workflow
    workflow_uuid, eng, obj = get_halted_workflow_merge(
        app=workflow_app,
        extra_config={
            'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [],
            # This feature is only available on latest non-legacy code
            'PRODUCTION_MODE': False,
        },
        record=update,
    )

    do_accept_core(
        app=workflow_app,
        workflow_id=obj.id,
    )

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    head = RecordMetadata.query.filter(RecordMetadata.id == head_uuid).one()
    new_root = retrieve_root_json(str(head_uuid), get_source(head.json))
    new_root = _remove_uuid_authors(new_root)
    new_root = _remove_buckets_version_id_files(new_root)

    update = _remove_buckets_version_id_files(update)

    assert new_root == update

    expected_merged = read_file('fixtures', 'merger_merged.json')
    expected_merged = _remove_uuid_authors(expected_merged)
    expected_merged = _remove_buckets_version_id_files(expected_merged)
    expected_merged = _replace_path_fft(expected_merged)

    workflow_record = _remove_uuid_authors(obj.data)
    workflow_record = _remove_buckets_version_id_files(workflow_record)
    workflow_record = _replace_path_fft(workflow_record)

    response = do_webcoll_callback(app=workflow_app, recids=[12345])
    assert response.status_code == 200

    assert obj.extra_data['match-found'] is True
    assert obj.extra_data['is-update'] is True
    assert obj.extra_data['merged'] is True

    assert expected_merged == workflow_record

    expected_conflicts = read_file('fixtures', 'merger_conflicts.json')
    assert obj.extra_data['conflicts'] == json.dumps(expected_conflicts)


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
    'inspirehep.modules.workflows.tasks.matching.search',
    return_value=[],
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    return_value=[],
)
def test_merge_without_conflicts_does_not_halt(
    mocked_refextract_extract_refs,
    mocked_matching_search,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download_utils,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):

    record_uuid = create_head_record()
    es.indices.refresh('records-hep')

    head = RecordMetadata.query.filter(RecordMetadata.id == record_uuid).one()
    update = head.json

    # this function starts the workflow
    workflow_uuid, eng, obj = get_halted_workflow_merge(
        app=workflow_app,
        extra_config={
            'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [],
            # This feature is only available on latest non-legacy code
            'PRODUCTION_MODE': False,
        },
        record=update,
    )

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    assert obj.extra_data['match-found'] is True
    assert obj.extra_data['is-update'] is True
    assert obj.extra_data['merged'] is True
    assert obj.extra_data.get('conflicts') is None
    assert obj.status == ObjectStatus.COMPLETED
