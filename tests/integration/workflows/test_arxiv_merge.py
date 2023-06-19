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
from factories.db.invenio_records import TestRecordMetadata
from flask import current_app
from invenio_workflows import (ObjectStatus, WorkflowEngine, start,
                               workflow_object_class)
from invenio_workflows.errors import WorkflowsError
from mock import patch
from mocks import fake_classifier_api_request, fake_magpie_api_request
from workflow_utils import build_workflow

from inspirehep.modules.workflows.tasks.actions import load_from_source_data
from inspirehep.modules.workflows.tasks.merging import merge_articles
from inspirehep.modules.workflows.utils import (
    _get_headers_for_hep_root_table_request, get_all_wf_record_sources,
    insert_wf_record_source, read_wf_record_source)

RECORD_WITHOUT_ACQUISITION_SOURCE_AND_CONFLICTS = {
    "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
    "titles": [
        {"title": "Update with conflicts title."},
    ],
    "arxiv_eprints": [{"categories": ["hep-lat", "hep-th"], "value": "1703.04802"}],
    "document_type": ["article"],
    "_collections": ["Literature"],
    "number_of_pages": 42,
}

RECORD_WITHOUT_ACQUISITION_SOURCE_AND_NO_CONFLICTS = {
    "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
    "titles": [
        {
            "source": "arXiv",
            "title": "4D $\\mathcal{N}=1$ SYM supercurrent in terms of the gradient flow",
        },
    ],
    "arxiv_eprints": [{"categories": ["hep-lat", "hep-th"], "value": "1703.04802"}],
    "document_type": ["article"],
    "_collections": ["Literature"],
}

RECORD_WITHOUT_CONFLICTS = {
    "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
    "titles": [
        {
            "source": "arXiv",
            "title": "4D $\\mathcal{N}=1$ SYM supercurrent in terms of the gradient flow",
        }
    ],
    "arxiv_eprints": [{"categories": ["hep-lat", "hep-th"], "value": "1703.04802"}],
    "document_type": ["article"],
    "_collections": ["Literature"],
    "acquisition_source": {"source": "arXiv"},
}

RECORD_WITH_CONFLICTS = {
    "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
    "titles": [
        {"title": "Update with conflicts title."},
    ],
    "arxiv_eprints": [{"categories": ["hep-lat", "hep-th"], "value": "1703.04802"}],
    "document_type": ["article"],
    "_collections": ["Literature"],
    "acquisition_source": {"source": "arXiv"},
    "number_of_pages": 42,
}

ARXIV_ROOT = RECORD_WITH_CONFLICTS


@pytest.fixture
def enable_merge_on_update(workflow_app):
    with patch.dict(workflow_app.config, {"FEATURE_FLAG_ENABLE_MERGER": True}):
        yield


@pytest.fixture
def disable_file_upload(workflow_app):
    with patch.dict(workflow_app.config, {"RECORDS_SKIP_FILES": True}):
        yield


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_handles_update_without_acquisition_source_and_acts_as_rootless(
    mocked_api_request_magpie,
    mocked_classifer_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.PublisherOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(
            RECORD_WITHOUT_ACQUISITION_SOURCE_AND_NO_CONFLICTS
        ).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        assert obj.status == ObjectStatus.COMPLETED
        assert not conflicts

        assert obj.extra_data.get("callback_url") is None
        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_head_revision"] == 0
        assert obj.extra_data["merger_original_root"] == {}

        # source us unknown, so no new root is saved.
        roots = get_all_wf_record_sources(factory.record_metadata.id)
        assert not roots


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_handles_update_without_acquisition_source_and_acts_as_rootless(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.PublisherOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(
            RECORD_WITHOUT_ACQUISITION_SOURCE_AND_CONFLICTS
        ).id

        # By default the root is {}.

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")
        assert obj.status == ObjectStatus.HALTED
        assert (
            len(conflicts) == 1
        )  # Title conflicting disabled for inspirehep/inspirehep#1918

        assert obj.extra_data.get("callback_url") is not None
        assert obj.extra_data.get("is-update") is True
        assert (
            obj.extra_data["merger_root"]
            == RECORD_WITHOUT_ACQUISITION_SOURCE_AND_CONFLICTS
        )
        assert obj.extra_data["merger_head_revision"] == 0
        assert obj.extra_data["merger_original_root"] == {}


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_rootful(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")
        assert obj.status == ObjectStatus.HALTED
        assert (
            len(conflicts) == 1
        )  # From now on titles doesn't cause conflicts (inspirehep/#1719)

        assert obj.extra_data.get("callback_url") is not None
        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_root"] == RECORD_WITH_CONFLICTS
        assert obj.extra_data["merger_head_revision"] == 0
        assert obj.extra_data["merger_original_root"] == {}


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_rootful(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        insert_wf_record_source(
            json_data=ARXIV_ROOT, record_uuid=factory.record_metadata.id, source="arxiv"
        )

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        assert obj.status == ObjectStatus.COMPLETED
        assert not conflicts

        assert obj.extra_data.get("callback_url") is None
        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_head_revision"] == 0
        assert obj.extra_data["merger_original_root"] == ARXIV_ROOT

        updated_root = read_wf_record_source(factory.record_metadata.id, "arxiv")
        assert updated_root.json == RECORD_WITH_CONFLICTS


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_without_conflicts_callback_url(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITHOUT_CONFLICTS).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        url = "http://localhost:5000/callback/workflows/resolve_merge_conflicts"

        assert obj.status == ObjectStatus.COMPLETED
        assert conflicts is None
        assert obj.extra_data.get("is-update") is True

        updated_root = read_wf_record_source(factory.record_metadata.id, "arxiv")
        assert updated_root.json == RECORD_WITHOUT_CONFLICTS

        payload = {"id": obj.id, "metadata": obj.data, "_extra_data": obj.extra_data}

        with workflow_app.test_client() as client:
            response = client.put(
                url,
                data=json.dumps(payload),
                content_type="application/json",
            )

        assert response.status_code == 400


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_callback_url(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        expected_url = (
            "http://localhost:5000/callback/workflows/resolve_merge_conflicts"
        )

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get("callback_url")
        assert (
            len(conflicts) == 1
        )  # From now on titles doesn't cause conflicts (inspirehep/#1719)

        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_root"] == RECORD_WITH_CONFLICTS

        payload = {"id": obj.id, "metadata": obj.data, "_extra_data": obj.extra_data}

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get("callback_url"),
                data=json.dumps(payload),
                content_type="application/json",
            )

        data = json.loads(response.get_data())
        expected_message = "Workflow {} has been saved with conflicts.".format(obj.id)

        assert response.status_code == 200
        assert expected_message == data["message"]

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.HALTED

        updated_root = read_wf_record_source(factory.record_metadata.id, "arxiv")
        assert updated_root is None


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_with_conflicts_callback_url_and_resolve(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        expected_url = (
            "http://localhost:5000/callback/workflows/resolve_merge_conflicts"
        )

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get("callback_url")
        assert (
            len(conflicts) == 1
        )  # From now on titles doesn't cause conflicts (inspirehep/#1719)

        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_root"] == RECORD_WITH_CONFLICTS

        # resolve conflicts
        obj.data["number_of_pages"] = factory.record_metadata.json.get(
            "number_of_pages"
        )
        del obj.extra_data["conflicts"]

        payload = {"id": obj.id, "metadata": obj.data, "_extra_data": obj.extra_data}

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get("callback_url"),
                data=json.dumps(payload),
                content_type="application/json",
            )
        assert response.status_code == 200

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        assert obj.status == ObjectStatus.COMPLETED
        assert conflicts is None

        assert obj.extra_data.get("approved") is True
        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data.get("merged") is True

        updated_root = read_wf_record_source(factory.record_metadata.id, "arxiv")
        assert updated_root.json == RECORD_WITH_CONFLICTS


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_merge_callback_url_with_malformed_workflow(
    mocked_api_request_magpie,
    mocked_classifier_api,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        factory = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = factory.inspire_record["control_number"]

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        eng_uuid = start("article", object_id=update_workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get("conflicts")

        expected_url = (
            "http://localhost:5000/callback/workflows/resolve_merge_conflicts"
        )

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get("callback_url")
        assert (
            len(conflicts) == 1
        )  # From now on titles doesn't cause conflicts (inspirehep/#1719)

        assert obj.extra_data.get("is-update") is True
        assert obj.extra_data["merger_root"] == RECORD_WITH_CONFLICTS

        payload = {
            "id": obj.id,
            "metadata": "Jessica Jones",
            "_extra_data": "Frank Castle",
        }

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get("callback_url"),
                data=json.dumps(payload),
                content_type="application/json",
            )

        data = json.loads(response.get_data())
        expected_message = "The workflow request is malformed."

        assert response.status_code == 400
        assert expected_message == data["message"]

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.HALTED
        assert obj.extra_data.get("callback_url") is not None
        assert obj.extra_data.get("conflicts") is not None
        assert obj.extra_data["merger_root"] is not None

        updated_root = read_wf_record_source(factory.record_metadata.id, "arxiv")
        assert updated_root is None


@patch(
    "inspirehep.modules.workflows.workflows.article.is_record_relevant",
)
@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_regression_non_relevant_update_is_not_rejected_and_gets_merged(
    mocked_api_request_magpie,
    mocked_classifier_api,
    mock_is_record_relevant,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    factory = TestRecordMetadata.create_from_file(
        __name__, "merge_record_arxiv.json", index_name="records-hep"
    )
    control_number = factory.inspire_record["control_number"]

    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/exact-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_ids": [control_number]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    update_workflow_id = build_workflow(factory.record_metadata.json).id
    eng_uuid = start("article", object_id=update_workflow_id)

    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj = eng.objects[0]

    mock_is_record_relevant.assert_not_called()

    assert obj.extra_data.get("is-update") is True
    assert obj.extra_data["approved"] is True
    assert obj.extra_data["auto-approved"] is True
    assert obj.extra_data["merged"] is True


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.upload._is_stale_data",
    side_effect=[True, False],
)
def test_workflow_restarts_once_if_working_with_stale_data(
    mocked__is_stale_data,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
):
    factory = TestRecordMetadata.create_from_file(
        __name__, "merge_record_arxiv.json", index_name="records-hep"
    )
    control_number = factory.inspire_record["control_number"]

    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/exact-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_ids": [control_number]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )

    obj_id = build_workflow(factory.record_metadata.json).id
    start("article", object_id=obj_id)

    obj = workflow_object_class.get(obj_id)

    assert obj.extra_data["head_version_id"] == 1
    assert obj.extra_data["is-update"]
    assert (
        obj.extra_data["source_data"]["persistent_data"]["marks"]["restart-count"] == 1
    )
    assert obj.status == ObjectStatus.COMPLETED


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.upload._is_stale_data",
    side_effect=[True, True, False],
)
def test_workflow_restarts_twice_if_working_with_stale_data(
    mocked__is_stale_data,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
):
    factory = TestRecordMetadata.create_from_file(
        __name__, "merge_record_arxiv.json", index_name="records-hep"
    )
    control_number = factory.inspire_record["control_number"]

    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/exact-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_ids": [control_number]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )

    obj_id = build_workflow(factory.record_metadata.json).id
    start("article", object_id=obj_id)

    obj = workflow_object_class.get(obj_id)

    assert obj.extra_data["head_version_id"] == 1
    assert obj.extra_data["is-update"]
    assert (
        obj.extra_data["source_data"]["persistent_data"]["marks"]["restart-count"] == 2
    )
    assert obj.status == ObjectStatus.COMPLETED


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@patch("inspirehep.modules.workflows.tasks.upload._is_stale_data", return_value=True)
def test_workflow_restarts_goes_in_error_after_three_restarts(
    mocked__is_stale_data,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
):
    factory = TestRecordMetadata.create_from_file(
        __name__, "merge_record_arxiv.json", index_name="records-hep"
    )
    control_number = factory.inspire_record["control_number"]

    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/exact-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_ids": [control_number]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    obj_id = build_workflow(factory.record_metadata.json).id

    with pytest.raises(WorkflowsError):
        start("article", object_id=obj_id)

    obj = workflow_object_class.get(obj_id)

    assert (
        obj.extra_data["source_data"]["persistent_data"]["marks"]["restart-count"] == 3
    )
    assert "Workflow restarted too many times" in obj.extra_data["_error_msg"]
    assert obj.status == ObjectStatus.ERROR


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_conflict_creates_ticket(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
    disable_file_upload,
    enable_merge_on_update,
):
    with patch(
        "inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters",
        ["acquisition_source.source"],
    ):
        record = TestRecordMetadata.create_from_file(
            __name__, "merge_record_arxiv.json", index_name="records-hep"
        )
        control_number = record.inspire_record["control_number"]
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [control_number]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        update_workflow_id = build_workflow(RECORD_WITH_CONFLICTS).id

        start("article", object_id=update_workflow_id)

        wf = workflow_object_class.get(update_workflow_id)
        expected_ticket = "content=Queue%3A+HEP_conflicts%0AText%3A+Merge+conflict+needs+to+be+resolved.%0A++%0A++https%3A%2F%2Flocalhost%3A5000%2Feditor%2Fholdingpen%2F{wf_id}%0ASubject%3A+arXiv%3A1703.04802+%28%23None%29%0Aid%3A+ticket%2Fnew%0ACF".format(
            wf_id=wf.id
        )

        assert mocked_external_services.request_history[1].text.startswith(
            expected_ticket
        )
        assert wf.extra_data["conflict-ticket-id"]

        expected_ticket_close_url = "http://rt.inspire/ticket/{ticket_id}/edit".format(
            ticket_id=wf.extra_data["conflict-ticket-id"]
        )

        wf.continue_workflow()

        assert (
            mocked_external_services.request_history[2].url == expected_ticket_close_url
        )
        assert (
            mocked_external_services.request_history[2].text
            == "content=Status%3A+resolved"
        )


@pytest.mark.vcr()
def test_merge_with_records_pulled_from_hep(workflow_app):
    config = {
        "INSPIREHEP_URL": "https://inspirebeta.net/api",
        "FEATURE_FLAG_ENABLE_HEP_REST_RECORD_PULL": True,
    }
    with mock.patch.dict(current_app.config, config):
        new_data = {
            "titles": [
                {"title": "New title"},
            ]
        }
        extra_data = {"matches": {"approved": 1401296}}
        expected_title = {"title": "New title"}
        wf = build_workflow(new_data, extra_data=extra_data)
        load_from_source_data(wf, None)
        merge_articles(wf, None)
        assert len(wf.data["titles"]) == 2
        assert expected_title in wf.data["titles"]
