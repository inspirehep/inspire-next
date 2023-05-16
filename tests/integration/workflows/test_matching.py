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

from copy import deepcopy

import pytest
import requests_mock
from invenio_search import current_search
from invenio_workflows import (ObjectStatus, WorkflowEngine, start,
                               workflow_object_class)
from mock import patch
from mocks import fake_classifier_api_request, fake_magpie_api_request
from workflow_utils import build_workflow

from inspirehep.modules.workflows.tasks.matching import (
    exact_match, fuzzy_match, handle_matched_holdingpen_wfs, has_same_source,
    match_non_completed_wf_in_holdingpen,
    match_previously_rejected_wf_in_holdingpen)
from inspirehep.modules.workflows.utils import \
    _get_headers_for_hep_root_table_request


@pytest.fixture
def simple_record(app):
    yield {
        "workflow_data": {
            "$schema": "http://localhost:5000/schemas/records/hep.json",
            "_collections": ["Literature"],
            "document_type": ["article"],
            "titles": [{"title": "Superconductivity"}],
            "acquisition_source": {"source": "arXiv"},
            "dois": [{"value": "10.3847/2041-8213/aa9110"}],
        },
        "extra_data": {
            "source_data": {
                "data": {
                    "$schema": "http://localhost:5000/schemas/records/hep.json",
                    "_collections": ["Literature"],
                    "document_type": ["article"],
                    "titles": [{"title": "Superconductivity"}],
                    "acquisition_source": {"source": "arXiv"},
                    "dois": [{"value": "10.3847/2041-8213/aa9110"}],
                },
                "extra_data": {},
            },
        },
    }

    list(current_search.delete(index_list="holdingpen-hep"))
    list(current_search.create(ignore=[400], ignore_existing=True))


def test_pending_holdingpen_matches_wf_if_not_completed(app, simple_record):

    workflow = build_workflow(status=ObjectStatus.HALTED, **simple_record)
    obj_id = workflow.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)

    assert match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.COMPLETED
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    # doesn't match anymore because obj is COMPLETED
    assert not match_non_completed_wf_in_holdingpen(obj2, None)


def test_match_previously_rejected_wf_in_holdingpen(app, simple_record):
    obj = build_workflow(status=ObjectStatus.COMPLETED, **simple_record)
    obj_id = obj.id

    obj.extra_data["approved"] = False  # reject it
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    assert match_previously_rejected_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["previously_rejected_matches"] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.HALTED
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    # doesn't match anymore because obj is COMPLETED
    assert not match_previously_rejected_wf_in_holdingpen(obj2, None)


def test_has_same_source(app, simple_record):
    obj = build_workflow(status=ObjectStatus.HALTED, data_type="hep", **simple_record)
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    match_non_completed_wf_in_holdingpen(obj2, None)

    same_source_func = has_same_source("holdingpen_matches")

    assert same_source_func(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    # change source and match the wf in the holdingpen
    different_source_rec = deepcopy(simple_record)
    different_source_rec["workflow_data"]["acquisition_source"] = {
        "source": "different"
    }
    obj3 = build_workflow(**different_source_rec)

    assert match_non_completed_wf_in_holdingpen(obj3, None)
    assert not same_source_func(obj3, None)


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_stop_matched_holdingpen_wfs(
    mocked_api_request_magpie,
    mocked_classifer_api,
    app,
    mocked_external_services,
    simple_record,
):
    # need to run a wf in order to assign to it the wf definition and a uuid
    # for it

    obj = build_workflow(data_type="hep", **simple_record)
    workflow_uuid = start("article", object_id=obj.id)
    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj.status = ObjectStatus.HALTED
    obj.save()
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    obj2_id = obj2.id

    match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    handle_matched_holdingpen_wfs(obj2, None)

    stopped_wf = workflow_object_class.get(obj_id)
    assert stopped_wf.status == ObjectStatus.COMPLETED
    assert stopped_wf.extra_data["stopped-by-wf"] == obj2_id


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_handle_matched_holdingpen_wfs(
    mocked_api_request_magpie,
    mocked_classifer_api,
    mocked_external_services,
    app,
    simple_record,
):
    # need to run a wf in order to assign to it the wf definition and a uuid
    # for it

    obj = build_workflow(data_type="hep", **simple_record)
    workflow_uuid = start("article", object_id=obj.id)
    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj.status = ObjectStatus.WAITING
    obj.save()
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    simple_record["workflow_data"]["acquisition_source"]["source"] = "elsevier"
    obj2 = build_workflow(**simple_record)
    match_non_completed_wf_in_holdingpen(obj2, None)

    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    handle_matched_holdingpen_wfs(obj2, None)

    matched_wf_with_different_source = workflow_object_class.get(obj_id)
    # matched wf with different source is not stopped
    assert matched_wf_with_different_source.status == ObjectStatus.HALTED
    assert not matched_wf_with_different_source.extra_data.get("stopped-by-wf")
    assert matched_wf_with_different_source.extra_data.get(
        "halted-by-match-with-different-source"
    )


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_handle_matched_holdingpen_wfs_with_same_source(
    mocked_api_request_magpie,
    mocked_classifer_api,
    mocked_external_services,
    app,
    simple_record,
):
    # need to run a wf in order to assign to it the wf definition and a uuid
    # for it

    obj = build_workflow(data_type="hep", **simple_record)
    workflow_uuid = start("article", object_id=obj.id)
    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj.status = ObjectStatus.HALTED
    obj.save()
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)

    match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    handle_matched_holdingpen_wfs(obj2, None)

    matched_wf_with_same_source = workflow_object_class.get(obj_id)
    # matched wf with same source is stopped
    assert matched_wf_with_same_source.status == ObjectStatus.COMPLETED
    assert matched_wf_with_same_source.extra_data.get("stopped-by-wf")


def test_exact_match(workflow_app):
    record = {
        "_collections": ["Literature"],
        "abstracts": [{"value": "An abstract", "source": "Springer"}],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["article"],
    }
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": [1, 2, 3]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        workflow_object = workflow_object_class.create(
            data=record, id_user=None, data_type="hep"
        )
        match = exact_match(workflow_object, None)
        assert workflow_object.extra_data["matches"]["exact"] == [1, 2, 3]
        assert match


def test_fuzzy_match(workflow_app):
    record = {
        "_collections": ["Literature"],
        "abstracts": [{"value": "An abstract", "source": "Springer"}],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["article"],
    }
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "abstract": "test",
                        "title": "test",
                        "number_of_pages": 12,
                        "earliest_date": 1999,
                        "authors": [{"full_name": "Jedrych, M."}],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        workflow_object = workflow_object_class.create(
            data=record, id_user=None, data_type="hep"
        )
        match = fuzzy_match(workflow_object, None)
        assert workflow_object.extra_data["matches"]["fuzzy"] == [
            {
                "abstract": "test",
                "title": "test",
                "number_of_pages": 12,
                "earliest_date": 1999,
                "authors": [{"full_name": "Jedrych, M."}],
            }
        ]
        assert match
