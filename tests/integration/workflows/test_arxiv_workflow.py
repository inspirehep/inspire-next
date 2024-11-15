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
import pkg_resources
import pytest
import requests
import requests_mock
from calls import (core_record, do_accept_core, do_resolve_matching,
                   do_robotupload_callback, do_validation_callback,
                   generate_record)
from factories.db.invenio_records import TestRecordMetadata
from flask import current_app
from inspire_schemas.utils import validate
from invenio_db import db
from invenio_search import current_search
from invenio_workflows import (ObjectStatus, WorkflowEngine, WorkflowObject,
                               start, workflow_object_class)
from invenio_workflows.errors import WorkflowsError
from jsonschema import ValidationError
from mock import patch
from mocks import (fake_classifier_api_request, fake_download_file,
                   fake_magpie_api_request)
from workflow_utils import build_workflow

from inspirehep.modules.workflows.tasks.actions import load_from_source_data
from inspirehep.modules.workflows.utils import (
    _get_headers_for_hep_root_table_request, do_not_repeat)


@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
def get_halted_workflow(mocked_is_pdf_link, app, record, extra_config=None):
    mocked_is_pdf_link.return_value = True

    extra_config = extra_config or {}
    with mock.patch.dict(app.config, extra_config):
        workflow_id = build_workflow(record).id
        workflow_uuid = start("article", object_id=workflow_id)

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    assert obj.status == ObjectStatus.HALTED
    assert obj.data_type == "hep"

    # Files should have been attached (tarball + pdf, and plots)
    assert obj.files["1407.7587.pdf"]
    assert obj.files["1407.7587.tar.gz"]

    assert len(obj.files) > 2

    # A publication note should have been extracted
    pub_info = obj.data.get("publication_info")
    assert pub_info
    assert pub_info[0]
    assert pub_info[0].get("year") == 2014
    assert pub_info[0].get("journal_title") == "J. Math. Phys."

    # A prediction should have been made
    prediction = obj.extra_data.get("relevance_prediction")
    assert prediction
    assert prediction["decision"] == "Non-CORE"
    assert prediction["scores"]["Non-CORE"] == 0.6497962474822998

    expected_experiment_prediction = {
        "experiments": [{"label": "CMS", "score": 0.75495152473449707}]
    }
    experiments_prediction = obj.extra_data.get("experiments_prediction")
    assert experiments_prediction == expected_experiment_prediction

    keywords_prediction = obj.extra_data.get("keywords_prediction")
    assert keywords_prediction
    assert {
        "label": "galaxy",
        "score": 0.29424679279327393,
        "accept": True,
    } in keywords_prediction["keywords"]

    # This record should not have been touched yet
    assert obj.extra_data["approved"] is None

    return workflow_uuid, eng, obj


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_rejected(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_classifier_api,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app, extra_config=extra_config, record=record
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


@mock.patch("inspirehep.modules.workflows.tasks.submission.send_robotupload")
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_harvesting_arxiv_workflow_core_record_auto_accepted(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    mocked_send_robotupload,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record, categories = core_record()

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "ARXIV_CATEGORIES": categories,
    }
    with workflow_app.app_context():
        workflow_id = build_workflow(record).id
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_uuid = start("article", object_id=workflow_id)

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        assert obj.extra_data["approved"] is True
        assert obj.extra_data["auto-approved"] is True
        assert obj.data["core"] is True


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.utils.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch("inspirehep.modules.workflows.tasks.matching.match", return_value=iter([]))
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_harvesting_arxiv_workflow_manual_accepted(
    mocked_refextract_extract_refs,
    mocked_matching_match,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_download_utils,
    mocked_download_arxiv,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app,
        extra_config=extra_config,
        record=record,
    )

    do_accept_core(app=workflow_app, workflow_id=obj.id)

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    assert obj.status == ObjectStatus.WAITING

    do_robotupload_callback(app=workflow_app, workflow_id=obj.id, recids=[12345])

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    # It was accepted
    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data["approved"] is True


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_stops_pending_wf(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()

    workflow_id = build_workflow(record).id
    eng_uuid = start("article", object_id=workflow_id)
    current_search.flush_and_refresh("holdingpen-hep")
    eng = WorkflowEngine.from_uuid(eng_uuid)
    old_wf = eng.objects[0]
    obj_id = old_wf.id

    assert old_wf.status == ObjectStatus.HALTED
    assert old_wf.extra_data["previously_rejected"] is False

    record2 = record
    record["titles"][0][
        "title"
    ] = "This is an update that will match the wf in the holdingpen"
    record2_workflow = build_workflow(record2).id
    start("article", object_id=record2_workflow)
    current_search.flush_and_refresh("holdingpen-hep")

    update_wf = workflow_object_class.get(record2_workflow)

    assert update_wf.status == ObjectStatus.HALTED
    #  As workflow stops (in error) before setting this
    assert update_wf.extra_data["previously_rejected"] is False
    assert update_wf.extra_data["already-in-holding-pen"] is True
    assert update_wf.extra_data["stopped-matched-holdingpen-wf"] is True
    assert update_wf.extra_data["is-update"] is False

    old_wf = workflow_object_class.get(obj_id)
    assert old_wf.extra_data["already-in-holding-pen"] is False
    assert old_wf.extra_data["previously_rejected"] is False
    assert old_wf.extra_data["stopped-by-wf"] == update_wf.id
    assert old_wf.extra_data.get("approved") is None
    assert old_wf.extra_data["is-update"] is False
    assert old_wf.status == ObjectStatus.COMPLETED


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_previously_rejected_wf_stop(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):

    record = generate_record()

    record_workflow = build_workflow(record).id
    eng_uuid = start("article", object_id=record_workflow)
    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj_id = eng.objects[0].id
    obj = workflow_object_class.get(obj_id)
    obj.extra_data["approved"] = False  # reject record
    obj.continue_workflow()
    obj = workflow_object_class.get(obj_id)
    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data.get("approved") is False

    current_search.flush_and_refresh("holdingpen-hep")

    record["titles"][0][
        "title"
    ] = "This is an update that will match the wf in the holdingpen"
    # this workflow matches in the holdingpen and stops because the
    # matched one was rejected
    workflow_id = build_workflow(record).id
    eng_uuid = start("article", object_id=workflow_id)
    eng = WorkflowEngine.from_uuid(eng_uuid)
    obj2 = eng.objects[0]

    assert obj2.extra_data["already-in-holding-pen"] is False
    assert obj2.extra_data["previously_rejected"] is True
    assert obj_id in obj2.extra_data["previously_rejected_matches"]


def test_article_workflow_stops_when_record_is_not_valid(workflow_app):
    invalid_record = {"document_type": ["article"], "titles": [{"title": "A title"}]}

    workflow_id = build_workflow(invalid_record).id

    with pytest.raises(ValidationError):
        start("article", object_id=workflow_id)

    obj = workflow_object_class.get(workflow_id)

    assert obj.status == ObjectStatus.ERROR
    assert "_error_msg" in obj.extra_data
    assert "required" in obj.extra_data["_error_msg"]

    expected_url = "http://localhost:5000/callback/workflows/resolve_validation_errors"

    assert expected_url == obj.extra_data["callback_url"]
    assert obj.extra_data["validation_errors"]
    assert "message" in obj.extra_data["validation_errors"][0]
    assert "path" in obj.extra_data["validation_errors"][0]


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
def test_article_workflow_continues_when_record_is_valid(
    mocked_api_request_magpie, mocked_api_request_classifier, workflow_app
):
    valid_record = {
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "A title"}],
    }
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(valid_record).id
        eng_uuid = start("article", object_id=workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status != ObjectStatus.ERROR
        assert "_error_msg" not in obj.extra_data


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
def test_update_exact_matched_goes_trough_the_workflow(
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_classifier,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
):
    record = record_from_db
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{}/curation/literature/assign-institutions".format(
                current_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [record["control_number"]]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        workflow_id = build_workflow(record).id
        eng_uuid = start("article", object_id=workflow_id)
        obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
        obj = workflow_object_class.get(obj_id)

        assert obj.extra_data["holdingpen_matches"] == []
        assert obj.extra_data["previously_rejected"] is False
        assert not obj.extra_data.get("stopped-matched-holdingpen-wf")
        assert obj.extra_data["is-update"]
        assert obj.extra_data["exact-matched"]
        assert obj.extra_data["matches"]["exact"] == [record.get("control_number")]
        assert obj.extra_data["matches"]["approved"] == record.get("control_number")
        assert obj.extra_data["approved"]
        assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
def test_fuzzy_matched_goes_trough_the_workflow(
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_classifier,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
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

    record = record_from_db
    del record["arxiv_eprints"]
    rec_id = record["control_number"]

    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{}/curation/literature/assign-institutions".format(
                current_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {"control_number": record["control_number"]}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(record).id
        eng_uuid = start("article", object_id=workflow_id)

        obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
        obj = workflow_object_class.get(obj_id)

        assert obj.status == ObjectStatus.HALTED  # for matching approval
        obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
        obj = workflow_object_class.get(obj_id)

        assert obj.extra_data["holdingpen_matches"] == []

        WorkflowObject.continue_workflow = continue_wf_patched_context(workflow_app)
        do_resolve_matching(workflow_app, obj.id, rec_id)

        obj = workflow_object_class.get(obj_id)
        assert obj.extra_data["matches"]["approved"] == rec_id
        assert obj.extra_data["fuzzy-matched"]
        assert obj.extra_data["is-update"]
        assert obj.extra_data["approved"]

        obj = workflow_object_class.get(obj_id)
        assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
def test_validation_error_callback_with_a_valid(
    mocked_api_request_magpie, mocked_api_request_classifier, workflow_app
):
    valid_record = {
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "A title"}],
    }
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(valid_record).id
        eng_uuid = start("article", object_id=workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status != ObjectStatus.ERROR

        response = do_validation_callback(
            workflow_app, obj.id, obj.data, obj.extra_data
        )

        expected_error_code = "WORKFLOW_NOT_IN_ERROR_STATE"
        data = json.loads(response.get_data())

        assert response.status_code == 400
        assert expected_error_code == data["error_code"]


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
def test_validation_error_callback_with_validation_error(
    mocked_api_request_magpie, mocked_api_request_classifier, workflow_app
):
    invalid_record = {
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "A title"}],
        "preprint_date": "Jessica Jones",
    }
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(invalid_record).id

        with pytest.raises(ValidationError):
            start("article", object_id=workflow_id)

        obj = workflow_object_class.get(workflow_id)

        assert obj.status == ObjectStatus.ERROR

        response = do_validation_callback(
            workflow_app, obj.id, obj.data, obj.extra_data
        )

        expected_message = "Validation error."
        expected_error_code = "VALIDATION_ERROR"
        data = json.loads(response.get_data())

        assert response.status_code == 400
        assert expected_error_code == data["error_code"]
        assert expected_message == data["message"]

        assert data["workflow"]["_extra_data"]["callback_url"]
        assert len(data["workflow"]["_extra_data"]["validation_errors"]) == 1


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
def test_validation_error_callback_with_missing_worfklow(
    mocked_api_request_magpie, mocked_api_request_classifier, workflow_app
):
    invalid_record = {
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "A title"}],
    }
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(invalid_record).id
        eng_uuid = start("article", object_id=workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        response = do_validation_callback(workflow_app, 1111, obj.data, obj.extra_data)

        data = json.loads(response.get_data())
        expected_message = 'The workflow with id "1111" was not found.'
        expected_error_code = "WORKFLOW_NOT_FOUND"

        assert response.status_code == 404
        assert expected_error_code == data["error_code"]
        assert expected_message == data["message"]


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
def test_validation_error_callback_with_malformed_with_invalid_types(
    mocked_api_request_magpie, mocked_api_request_classifier, workflow_app
):
    invalid_record = {
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "A title"}],
    }
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(invalid_record).id
        eng_uuid = start("article", object_id=workflow_id)

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        response = do_validation_callback(
            workflow_app,
            # id
            "Alias Investigations",
            obj.data,
            # extra_data
            "Jessica Jones",
        )
        data = json.loads(response.get_data())
        expected_message = "The workflow request is malformed."
        expected_error_code = "MALFORMED"

        assert response.status_code == 400
        assert expected_error_code == data["error_code"]
        assert expected_message == data["message"]
        assert "errors" in data


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_keep_previously_rejected_from_fully_harvested_category_is_auto_approved(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    record, categories = core_record()
    obj = workflow_object_class.create(
        data=record, status=ObjectStatus.COMPLETED, data_type="hep"
    )
    obj.extra_data["approved"] = False  # reject it
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "ARXIV_CATEGORIES": categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_id = build_workflow(record).id
            eng_uuid = start("article", object_id=workflow_id)
            eng = WorkflowEngine.from_uuid(eng_uuid)
            obj2 = eng.processed_objects[0]
            assert obj2.extra_data["auto-approved"]
            assert len(obj2.extra_data["previously_rejected_matches"]) > 0
            assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_previously_rejected_from_not_fully_harvested_category_is_not_auto_approved(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    record, categories = core_record()
    record["arxiv_eprints"][0]["categories"] = ["q-bio.GN"]

    obj = workflow_object_class.create(
        data=record, status=ObjectStatus.COMPLETED, data_type="hep"
    )
    obj.extra_data["approved"] = False  # reject it
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "ARXIV_CATEGORIES": categories,
    }
    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            workflow_id = build_workflow(record).id
            eng_uuid = start("article", object_id=workflow_id)
            eng = WorkflowEngine.from_uuid(eng_uuid)
            obj2 = eng.processed_objects[0]
            assert not obj2.extra_data["auto-approved"]
            assert len(obj2.extra_data["previously_rejected_matches"]) > 0
            assert obj2.status == ObjectStatus.COMPLETED


def test_match_wf_in_error_goes_in_error_state(
    workflow_app,
):
    record = generate_record()

    wf_id = build_workflow(record).id
    obj = workflow_object_class.get(wf_id)
    obj.status = ObjectStatus.ERROR
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    with pytest.raises(WorkflowsError):
        workflow_id = build_workflow(record).id
        start("article", object_id=workflow_id)


def test_match_wf_in_error_goes_in_initial_state(
    workflow_app,
):
    record = generate_record()

    wf_id = build_workflow(record).id
    obj = workflow_object_class.get(wf_id)
    obj.status = ObjectStatus.INITIAL
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    with pytest.raises(WorkflowsError):
        workflow_id = build_workflow(record).id
        start("article", object_id=workflow_id)


def test_start_wf_with_no_source_data_fails(workflow_app):
    record = generate_record()

    obj = build_workflow(record)
    del obj.extra_data["source_data"]
    obj.save()
    db.session.commit()

    with pytest.raises(ValueError):
        start("article", object_id=obj.id)


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_do_not_repeat(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    def return_value(val):
        def _return_value(obj, eng):
            obj.extra_data["id"] = val
            obj.save()
            return {"id": val}

        return _return_value

    custom_wf_steps = [
        load_from_source_data,
        do_not_repeat("one")(return_value(1)),
        do_not_repeat("two")(return_value(2)),
    ]

    custom_wf_steps_to_repeat = [
        load_from_source_data,
        do_not_repeat("one")(return_value(41)),
        do_not_repeat("two")(return_value(42)),
        do_not_repeat("three")(return_value(43)),
    ]

    expected_persistent_data_first_run = {
        "one": {"id": 1},
        "two": {"id": 2},
    }.viewitems()

    expected_persistent_data_second_run = {
        "one": {"id": 1},
        "two": {"id": 2},
        "three": {"id": 43},
    }.viewitems()

    record = generate_record()

    with workflow_app.app_context():
        wf_id = build_workflow(record).id
        workflow_uuid = start("article", object_id=wf_id)

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        eng = WorkflowEngine.from_uuid(obj.id_workflow)
        eng.callbacks.replace(custom_wf_steps)
        eng.process([obj])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        persistent_data = obj.extra_data["source_data"]["persistent_data"].viewitems()
        assert expected_persistent_data_first_run <= persistent_data
        assert obj.extra_data["id"] == 2
        assert obj.status == ObjectStatus.COMPLETED

        eng = WorkflowEngine.from_uuid(obj.id_workflow)
        eng.callbacks.replace(custom_wf_steps_to_repeat)
        obj.callback_pos = [0]
        obj.save()
        db.session.commit()
        eng.process([obj])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        persistent_data = obj.extra_data["source_data"]["persistent_data"].viewitems()
        assert expected_persistent_data_second_run <= persistent_data
        assert obj.extra_data["id"] == 43


def test_workflows_halts_on_multiple_exact_matches(workflow_app):
    # Record from arxiv with just arxiv ID in DB
    record_1 = TestRecordMetadata.create_from_file(
        __name__, "multiple_matches_arxiv.json", index_name="records-hep"
    )

    # Record from publisher with just DOI in DB
    record_2 = TestRecordMetadata.create_from_file(
        __name__, "multiple_matches_publisher.json", index_name="records-hep"
    )

    path = pkg_resources.resource_filename(
        __name__, "fixtures/multiple_matches_arxiv_update.json"
    )
    update_from_arxiv = json.load(open(path))
    with requests_mock.Mocker(real_http=True) as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={
                "matched_ids": [
                    record_1.inspire_record["control_number"],
                    record_2.inspire_record["control_number"],
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        # An update from arxiv with the same arxiv and DOI as above records
        workflow_id = build_workflow(update_from_arxiv).id
        start("article", object_id=workflow_id)

        obj = workflow_object_class.get(workflow_id)

        assert len(set(obj.extra_data["matches"]["exact"])) == 2

        assert obj.status == ObjectStatus.HALTED
        assert obj.extra_data["_action"] == "resolve_multiple_exact_matches"


def fake_validation(data, schema=None):
    return


@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch("inspirehep.modules.workflows.tasks.matching.match", return_value=iter([]))
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.validate",
    side_effect=[fake_validation, validate],
)
def test_workflow_with_validation_error(
    fake_validation,
    mocked_match,
    mocked_magpie_json_api_request,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
):
    record_with_validation_error = {
        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
        "titles": [{"title": "Update without conflicts title."}],
        "arxiv_eprints": [
            {"categories": ["WRONG_CATEGORY", "hep-th"], "value": "1703.04802"}
        ],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "acquisition_source": {"source": "arXiv"},
    }
    workflow = build_workflow(record_with_validation_error)
    with pytest.raises(ValidationError):
        start("article", object_id=workflow.id)
    assert fake_validation.call_count == 2
    assert workflow.status == ObjectStatus.ERROR


@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch("inspirehep.modules.workflows.tasks.matching.match", return_value=iter([]))
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.validate",
    side_effect=[fake_validation, validate],
)
def test_workflow_without_validation_error(
    fake_validation,
    mocked_match,
    mocked_magpie_json_api_request,
    mocked_api_request_classifier,
    workflow_app,
    mocked_external_services,
):
    record_without_validation_error = {
        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
        "titles": [{"title": "Update without conflicts title."}],
        "arxiv_eprints": [{"categories": ["hep-lat", "hep-th"], "value": "1703.04802"}],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "acquisition_source": {"source": "arXiv"},
    }
    workflow = build_workflow(record_without_validation_error)
    start("article", object_id=workflow.id)

    assert fake_validation.call_count == 2
    assert workflow.status == ObjectStatus.WAITING


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_workflow_restart_count_initialized_properly(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()

    with workflow_app.app_context():
        obj_id = build_workflow(record).id
        start("article", object_id=obj_id)

        obj = workflow_object_class.get(obj_id)

        assert (
            obj.extra_data["source_data"]["persistent_data"]["marks"]["restart-count"]
            == 0
        )
        assert obj.extra_data["restart-count"] == 0

        obj.callback_pos = [0]
        obj.save()
        db.session.commit()

        start("article", object_id=obj_id)

        assert (
            obj.extra_data["source_data"]["persistent_data"]["marks"]["restart-count"]
            == 1
        )
        assert obj.extra_data["restart-count"] == 1


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_match_in_holdingpen_different_sources_continues(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    workflow_app,
    mocked_external_services,
):
    record = generate_record()

    workflow_id = build_workflow(record).id
    eng_uuid = start("article", object_id=workflow_id)
    current_search.flush_and_refresh("holdingpen-hep")
    eng = WorkflowEngine.from_uuid(eng_uuid)
    wf_to_match = eng.objects[0].id
    obj = workflow_object_class.get(wf_to_match)
    assert obj.status == ObjectStatus.HALTED
    # generated wf pending in holdingpen

    record["titles"][0][
        "title"
    ] = "This is an update that will match the wf in the holdingpen"
    record["acquisition_source"]["source"] = "but not the source"
    # this workflow matches in the holdingpen and stops
    # because match for the workflow was found
    workflow_2_id = build_workflow(record).id
    eng_2_uuid = start("article", object_id=workflow_2_id)
    eng_2 = WorkflowEngine.from_uuid(eng_2_uuid)
    obj_2 = eng_2.objects[0]

    # the first wf from another source is still halted in HP
    assert obj.status == ObjectStatus.HALTED
    assert obj_2.status == ObjectStatus.HALTED
    assert eng.status.name == "HALTED"
    assert obj_2.extra_data["already-in-holding-pen"] is True
    assert obj_2.extra_data["holdingpen_matches"] == [wf_to_match]
    assert obj_2.extra_data["previously_rejected"] is False


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
def test_update_record_goes_through_api_version_of_store_record_without_issue(
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_classifier,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
):
    record = record_from_db
    workflow_id = build_workflow(record).id
    expected_control_number = record["control_number"]
    expected_head_uuid = str(record.id)
    with mock.patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://web:8000",
        },
    ):
        mocked_external_services.register_uri(
            "PUT",
            "{url}/literature/{cn}".format(
                url=workflow_app.config.get("INSPIREHEP_URL"),
                cn=expected_control_number,
            ),
            headers={"content-type": "application/json"},
            status_code=200,
            json={
                "metadata": {
                    "control_number": expected_control_number,
                },
                "id_": expected_head_uuid,
            },
        )
        mocked_external_services.register_uri(
            "GET",
            "{}/curation/literature/assign-institutions".format(
                current_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [record["control_number"]]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        mocked_external_services.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [],
                    [],
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        eng_uuid = start("article", object_id=workflow_id)
        url_paths = [r.path for r in mocked_external_services.request_history]
        url_hostnames = [r.hostname for r in mocked_external_services.request_history]

        assert "web" in url_hostnames
        assert "/literature/{cn}".format(cn=expected_control_number) in url_paths

        obj_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
        obj = workflow_object_class.get(obj_id)

        assert obj.data["control_number"] == expected_control_number

        assert obj.extra_data["holdingpen_matches"] == []
        assert obj.extra_data["previously_rejected"] is False
        assert not obj.extra_data.get("stopped-matched-holdingpen-wf")
        assert obj.extra_data["is-update"]
        assert obj.extra_data["exact-matched"]
        assert obj.extra_data["matches"]["exact"] == [record.get("control_number")]
        assert obj.extra_data["matches"]["approved"] == record.get("control_number")
        assert obj.extra_data["approved"]
        assert obj.status == ObjectStatus.COMPLETED


def connection_error(*args, **kwargs):
    raise requests.exceptions.ConnectionError


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.upload.requests.put",
    side_effect=connection_error,
)
def test_update_record_goes_through_api_version_of_store_record_wrong_api_address(
    mocked_request_in_upload,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_classifier,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
):
    record = record_from_db
    with mock.patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://go_to_wrong_address.bad__:98765",
        },
    ):
        mocked_external_services.register_uri(
            "GET",
            "{}/curation/literature/assign-institutions".format(
                current_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [record["control_number"]]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/curation/literature/normalize-journal-titles".format(inspirehep_url=workflow_app.config["INSPIREHEP_URL"]),
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [],
                    [],
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(record).id
        with pytest.raises(requests.exceptions.ConnectionError):
            start("article", object_id=workflow_id)
        obj = workflow_object_class.get(workflow_id)

        assert obj.status == ObjectStatus.ERROR
        assert obj.extra_data["_error_msg"].endswith("\nConnectionError\n") is True


def connection_timeout(*args, **kwargs):
    raise requests.exceptions.ConnectTimeout


@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.upload.requests.put",
    side_effect=connection_timeout,
)
def test_update_record_goes_through_api_version_of_store_record_connection_timeout(
    mocked_request_in_upload,
    mocked_is_pdf_link,
    mocked_download_arxiv,
    mocked_api_request_classifier,
    mocked_api_request_magpie,
    workflow_app,
    mocked_external_services,
    record_from_db,
):
    record = record_from_db
    with mock.patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://go_to_wrong_address.bad__:98765",
        },
    ):
        mocked_external_services.register_uri(
            "GET",
            "{}/curation/literature/assign-institutions".format(
                current_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/curation/literature/normalize-journal-titles".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": [record["control_number"]]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        mocked_external_services.register_uri(
            "GET",
            "{inspirehep_url}/curation/literature/affiliations-normalization".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={
                "normalized_affiliations": [
                    [],
                    [],
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow_id = build_workflow(record).id
        with pytest.raises(requests.exceptions.ConnectionError):
            start("article", object_id=workflow_id)
        obj = workflow_object_class.get(workflow_id)

        assert obj.status == ObjectStatus.ERROR
        assert obj.extra_data["_error_msg"].endswith("\nConnectTimeout\n") is True


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions._is_auto_rejected",
    return_value=True,
)
def test_workflow_checks_affiliations_if_record_is_not_important(
    mocked_is_auto_rejected,
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    record["authors"].append({"full_name": "Third Author"})
    record["authors"][2]["raw_affiliations"] = [
        {"value": "Fermilab"},
        {"value": "IN2P3"},
        {"value": "Cern"},
    ]
    mocked_external_services.register_uri(
        "GET",
        "{}/curation/literature/assign-institutions".format(
            current_app.config["INSPIREHEP_URL"]
        ),
        json={"authors": record["authors"]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    with patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://web:8000",
        },
    ):
        workflow_id = build_workflow(record).id
        start("article", object_id=workflow_id)
        collections_in_record = (
            filter(
                lambda x: x.path == "/literature",
                mocked_external_services.request_history,
            )
            .pop()
            .json()
            .get("_collections")
        )
        assert "CDS Hidden" in collections_in_record
        assert "HAL Hidden" in collections_in_record
        assert "Fermilab" in collections_in_record
        assert "Literature" not in collections_in_record


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_workflow_do_not_changes_to_hidden_if_record_authors_do_not_have_interesting_affiliations(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()

    workflow_id = build_workflow(record).id
    with patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://web:8000",
        },
    ):
        start("article", object_id=workflow_id)
        wf = workflow_object_class.get(workflow_id)
        wf.extra_data["approved"] = True
        wf.save()
        wf.continue_workflow(delayed=False)

    collections_in_record = (
        filter(
            lambda x: x.path == "/literature", mocked_external_services.request_history
        )
        .pop()
        .json()
        .get("_collections")
    )

    assert "CDS Hidden" not in collections_in_record
    assert "HAL Hidden" not in collections_in_record
    assert "Fermilab" not in collections_in_record
    assert ["Literature"] == collections_in_record


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions._is_auto_rejected",
    return_value=False,
)
def test_workflow_checks_affiliations_if_record_is_rejected_by_curator(
    mocked_is_auto_rejected,
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    record["authors"].append({"full_name": "Third Author"})
    record["authors"][2]["raw_affiliations"] = [
        {"value": "Fermilab?"},
        {"value": "IN2P3."},
        {"value": "Some words with CErN, inside."},
    ]
    mocked_external_services.register_uri(
        "GET",
        "{}/curation/literature/assign-institutions".format(
            current_app.config["INSPIREHEP_URL"]
        ),
        json={"authors": record["authors"]},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/exact-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_ids": []},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    mocked_external_services.register_uri(
        "GET",
        "http://web:8000/curation/literature/normalize-journal-titles",
        json={"normalized_journal_titles": {}},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )
    mocked_external_services.register_uri(
        "GET",
        "{inspirehep_url}/matcher/fuzzy-match".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
        ),
        json={"matched_data": {}},
        headers=_get_headers_for_hep_root_table_request(),
        status_code=200,
    )

    workflow_id = build_workflow(record).id
    with patch.dict(
        workflow_app.config,
        {
            "FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT": True,
            "INSPIREHEP_URL": "http://web:8000",
        },
    ):
        start("article", object_id=workflow_id)
        wf = workflow_object_class.get(workflow_id)
        wf.extra_data["approved"] = False
        wf.save()
        wf.continue_workflow(delayed=False)

    collections_in_record = (
        filter(
            lambda x: x.path == "/literature", mocked_external_services.request_history
        )
        .pop()
        .json()
        .get("_collections")
    )

    assert "CDS Hidden" in collections_in_record
    assert "HAL Hidden" in collections_in_record
    assert "Fermilab" in collections_in_record
    assert "Literature" not in collections_in_record


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link")
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.refextract.extract_references_from_file",
    return_value=[],
)
def test_grobid_extracts_authors_correctly(
    mocked_refextract_extract_refs,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_actions_download,
    mocked_is_pdf_link,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test a full harvesting workflow."""
    record = generate_record()
    record["authors"][0]["raw_affiliations"] = [
        {"value": "Concordia University, Montréal, Québec, Canada"}
    ]
    record["authors"][0]["full_name"] = "Hall, Richard Leon"

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    expected_authors_after_extraction = [
        {
            u"raw_affiliations": [
                {
                    u"value": u"Department of Mathematics and Statistics, Concordia University, 1455 de Maisonneuve Boulevard West, Montr\xe9al, Qu\xe9bec, Canada H3G 1M8"
                }
            ],
            u"emails": [u"richard.hall@concordia.ca"],
            u"full_name": u"Hall, Richard Leon",
        },
        {
            u"raw_affiliations": [
                {
                    u"value": u"Department of Mathematics and Statistics, University of Prince Edward Island, 550 University Avenue, Charlottetown, PEI, Canada C1A 4P3."
                }
            ],
            u"emails": [u"nsaad@upei.ca"],
            u"full_name": u"Saad, Nasser",
        },
    ]

    workflow_uuid, eng, obj = get_halted_workflow(
        app=workflow_app, extra_config=extra_config, record=record
    )

    obj = workflow_object_class.get(obj.id)

    assert obj.extra_data["authors_with_affiliations"]
    assert obj.data["authors"] == expected_authors_after_extraction
