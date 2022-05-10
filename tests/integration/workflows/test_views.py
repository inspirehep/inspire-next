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

import json
import mock as mock
import time
from copy import deepcopy
import requests_mock

from factories.db.invenio_records import TestRecordMetadata
from flask import current_app
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db
from invenio_workflows import workflow_object_class
from invenio_workflows.models import WorkflowObjectModel
from mock import patch
from workflow_utils import build_workflow
from invenio_workflows import ObjectStatus
from utils import override_config

from inspirehep.modules.workflows.tasks.actions import create_core_selection_wf


def test_inspect_merge_view(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={"titles": [{"title": "Curated version"}]}
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type="hep",
    )
    obj.save()
    db.session.commit()

    head = deepcopy(factory.record_metadata.json)
    factory.record_metadata.json["titles"][0]["title"] = "second curated version"
    db.session.add(factory.record_metadata)
    db.session.commit()

    obj.extra_data["merger_root"] = {
        "titles": [{"title": "Second version"}],
        "document_type": ["article"],
        "_collections": ["Literature"],
    }
    obj.extra_data["merger_original_root"] = {
        "titles": [{"title": "First version"}],
        "document_type": ["article"],
        "_collections": ["Literature"],
    }
    obj.extra_data["merger_head_revision"] = factory.inspire_record.revision_id

    expected = {
        "root": obj.extra_data["merger_original_root"],
        "head": head,
        "update": obj.extra_data["merger_root"],
        "merged": factory.record_metadata.json,
    }

    with workflow_app.test_client() as client:
        response = client.get("/workflows/inspect_merge/{}".format(obj.id))
        assert response.status_code == 200
        assert json.loads(response.data) == expected


def test_inspect_merge_view_returns_400(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={"titles": [{"title": "Curated version"}]}
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type="hep",
    )
    obj.save()
    db.session.commit()

    with workflow_app.test_client() as client:
        response = client.get("/workflows/inspect_merge/{}".format(obj.id))
        assert response.status_code == 400


def test_responses_with_etag(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={"titles": [{"title": "Etag version"}]}
    )

    workflow_id = build_workflow(factory.record_metadata.json).id
    obj = workflow_object_class.get(workflow_id)
    obj.save()
    db.session.commit()

    workflow_url = "/api/holdingpen/{}".format(obj.id)

    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        response = client.get(workflow_url)
        assert response.status_code == 200

        etag = response.headers["ETag"]
        last_modified = response.headers["Last-Modified"]

        response = client.get(
            workflow_url, headers={"If-Modified-Since": last_modified}
        )
        assert response.status_code == 304

        response = client.get(workflow_url, headers={"If-None-Match": etag})
        assert response.status_code == 304

        response = client.get(workflow_url, headers={"If-None-Match": "Jessica Jones"})
        assert response.status_code == 200


@patch("inspirehep.modules.workflows.views.start")
def test_new_author_submit_with_required_fields(
    mock_start, workflow_app, mocked_external_services
):
    data = {
        "data": {
            "$schema": "http://localhost:5000/schemas/records/authors.json",
            "_collections": ["Authors"],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": "None",
                "internal_uid": 1,
            },
            "name": {"value": "Martinez, Diegpo"},
            "status": "active",
        }
    }

    with workflow_app.test_client() as client:
        headers = {
            "Authorization": "Bearer " + current_app.config["AUTHENTICATION_TOKEN"]
        }
        response = client.post(
            "/workflows/authors",
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
        )
        assert response.status_code == 200

        workflow_object_id = json.loads(response.data).get("workflow_object_id")
        assert workflow_object_id is not None

        obj = workflow_object_class.get(workflow_object_id)

        mock_start.delay.assert_called_once_with("author", object_id=workflow_object_id)

        expected = {
            "status": "active",
            "$schema": "http://localhost:5000/schemas/records/authors.json",
            "acquisition_source": {
                "method": "submitter",
                "internal_uid": 1,
                "email": "john.doe@gmail.com",
                "submission_number": "1",
                "datetime": "2019-02-04T10:06:34.695915",
            },
            "_collections": ["Authors"],
            "name": {"value": "Martinez, Diegpo"},
        }

        assert expected == obj.data

        assert obj.extra_data["is-update"] is False


@patch("inspirehep.modules.workflows.views.start")
def test_update_author_submit_with_required_fields(
    mock_start, workflow_app, mocked_external_services
):
    data = {
        "data": {
            "$schema": "http://localhost:5000/schemas/records/authors.json",
            "_collections": ["Authors"],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": "None",
                "internal_uid": 1,
            },
            "name": {"value": "Martinez, Diegpo"},
            "status": "active",
            "control_number": 3,
        }
    }
    with workflow_app.test_client() as client:
        headers = {
            "Authorization": "Bearer " + current_app.config["AUTHENTICATION_TOKEN"]
        }
        response = client.post(
            "/workflows/authors",
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
        )
        assert response.status_code == 200

        workflow_object_id = json.loads(response.data).get("workflow_object_id")
        assert workflow_object_id is not None

        obj = workflow_object_class.get(workflow_object_id)

        mock_start.delay.assert_called_once_with("author", object_id=workflow_object_id)

        expected = {
            "status": "active",
            "$schema": "http://localhost:5000/schemas/records/authors.json",
            "acquisition_source": {
                "method": "submitter",
                "internal_uid": 1,
                "email": "john.doe@gmail.com",
                "submission_number": "1",
                "datetime": "2019-02-04T10:06:34.695915",
            },
            "_collections": ["Authors"],
            "name": {"value": "Martinez, Diegpo"},
            "control_number": 3,
        }

        assert expected == obj.data

        assert obj.extra_data["is-update"] is True


def test_new_author_submit_requires_authentication(workflow_app):
    data = {
        "data": {
            "_collections": ["Authors"],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": "None",
                "internal_uid": 1,
            },
            "name": {"value": "Martinez, Diegpo"},
            "status": "active",
        }
    }

    headers = {"Authorization": "Bearer " + "wrong_token"}
    with workflow_app.test_client() as client:
        response = client.post(
            "/api/workflows/authors",
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
        )
    assert response.status_code == 401


def test_new_literature_submit_requires_authentication(workflow_app):
    data = {
        "data": {
            "$schema": "http://localhost:5000/schemas/records/hep.json",
            "_collections": ["Literature"],
            "document_type": ["article"],
            "titles": [{"title": "Discovery of cool stuff"}],
            "authors": [{"full_name": "Harun Urhan"}],
        },
        "form_data": {"url": "https://cern.ch/coolstuff.pdf"},
    }

    headers = {"Authorization": "Bearer " + "wrong_token"}
    with workflow_app.test_client() as client:
        response = client.post(
            "/api/workflows/authors",
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
        )
    assert response.status_code == 401


@patch("inspirehep.modules.workflows.views.start")
def test_literature_submit_workflow(mock_start, workflow_app):
    data = {
        "data": {
            "$schema": "http://localhost:5000/schemas/records/hep.json",
            "_collections": ["Literature"],
            "document_type": ["article"],
            "titles": [{"title": "Discovery of cool stuff"}],
            "authors": [{"full_name": "Harun Urhan"}],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "internal_uid": 1,
            },
        },
        "form_data": {"url": "https://cern.ch/coolstuff.pdf"},
    }

    with workflow_app.test_client() as client:
        headers = {
            "Authorization": "Bearer " + current_app.config["AUTHENTICATION_TOKEN"]
        }
        response = client.post(
            "/workflows/literature",
            data=json.dumps(data),
            content_type="application/json",
            headers=headers,
        )
        assert response.status_code == 200

        workflow_object_id = json.loads(response.data).get("workflow_object_id")
        assert workflow_object_id is not None
        mock_start.delay.assert_called_once_with(
            "article", object_id=workflow_object_id
        )

        obj = workflow_object_class.get(workflow_object_id)
        expected_data = {
            "$schema": "http://localhost:5000/schemas/records/hep.json",
            "_collections": ["Literature"],
            "document_type": ["article"],
            "titles": [{"title": "Discovery of cool stuff"}],
            "authors": [{"full_name": "Harun Urhan"}],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": str(workflow_object_id),
                "internal_uid": 1,
            },
        }

        expected_formdata = {"url": "https://cern.ch/coolstuff.pdf"}

        expected_submission_pdf = data["form_data"]["url"]

        assert expected_data == obj.data
        assert expected_formdata == obj.extra_data["formdata"]
        assert expected_submission_pdf == obj.extra_data["submission_pdf"]


def test_aggregations(workflow_app):
    factory = TestRecordMetadata.create_from_kwargs(
        json={
            "titles": [{"title": "Quarks and protons"}],
            "publication_info": [{"journal_title": "z.phys."}],
        }
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type="hep",
    )
    obj.save()
    db.session.commit()

    factory_2 = TestRecordMetadata.create_from_kwargs(
        json={
            "titles": [{"title": "Standard model"}],
            "dois": [{"value": "10.1007/bf01397206", "source": "publisher"}],
            "authors": [
                {"full_name": "Ambarzumian, V."},
                {"full_name": "Iwanenko, D."},
            ],
            "public_notes": [{"value": "Translation available at arXiv:2105.04360"}],
            "publication_info": [
                {
                    "artid": "104275",
                    "journal_record": {
                        "$ref": "https://inspirebeta.net/api/journals/1214078"
                    },
                    "journal_title": "J.Geom.Phys.",
                    "journal_volume": "167",
                    "material": "publication",
                    "year": 2021
                }
            ],
            "report_numbers": [{"source": "arXiv", "value": "MS-TP-21-05"}],
        }
    )

    obj_2 = workflow_object_class.create(
        data=factory_2.record_metadata.json,
        data_type="hep",
    )

    obj_2.save()
    db.session.commit()

    time.sleep(5)

    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        search_response = client.get(
            "/api/holdingpen"
        )
        result_data = json.loads(search_response.data)

    expected_aggregations = [
        "decision",
        "pending_action",
        "source",
        "status",
        "subject",
        "workflow_name",
        "journal",
    ]
    result_aggregations = result_data["aggregations"].keys()

    for aggregation in expected_aggregations:
        assert aggregation in result_aggregations

    assert len(expected_aggregations) == len(result_aggregations)
    assert len(result_data["aggregations"]['journal']['buckets']) == 2


def test_search(workflow_app):
    factory = TestRecordMetadata.create_from_kwargs(
        json={
            "titles": [{"title": "Quarks and protons"}],
            "publication_info": [{"journal_title": "z.phys."}],
        }
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type="hep",
    )
    obj.save()
    db.session.commit()

    factory_2 = TestRecordMetadata.create_from_kwargs(
        json={
            "titles": [{"title": "Standard model"}],
            "dois": [{"value": "10.1007/bf01397206", "source": "publisher"}],
            "authors": [
                {"full_name": "Ambarzumian, V."},
                {"full_name": "Iwanenko, D."},
            ],
            "public_notes": [{"value": "Translation available at arXiv:2105.04360"}],
            "_private_notes": [{"value": "Translation available at arXiv:2105.04360"}],
            "publication_info": [
                {
                    "journal_issue": "7-8",
                    "journal_record": {
                        "$ref": "https://inspirehep.net/api/journals/1214340"
                    },
                    "journal_title": "Z.Phys.",
                    "journal_volume": "64",
                }
            ],
            "report_numbers": [{"source": "arXiv", "value": "MS-TP-21-05"}],
        }
    )

    obj_2 = workflow_object_class.create(
        data=factory_2.record_metadata.json,
        data_type="hep",
    )
    expected_wf_id = str(obj_2.id)
    obj_2.save()
    db.session.commit()

    time.sleep(5)

    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        title_search_response = client.get(
            "/api/holdingpen?q=metadata.titles.title:standard model"
        )
        public_notes_search_response = client.get(
            "/api/holdingpen?q=metadata.public_notes.value:arxiv"
        )
        # should return both workflows
        journal_title_search = client.get(
            "/api/holdingpen?q=metadata.publication_info.journal_title:Z.Phys."
        )
        reports_search = client.get(
            "/api/holdingpen?q=metadata.report_numbers.value:MS-TP-21-05"
        )
        authors_search = client.get(
            "/api/holdingpen?q=metadata.authors.full_name:Ambarzumian"
        )
        private_notes_search = client.get(
            "/api/holdingpen?q=metadata._private_notes.value:arxiv"
        )

    data_titles = json.loads(title_search_response.data)
    data_public_notes = json.loads(public_notes_search_response.data)
    data_journal_title = json.loads(journal_title_search.data)
    data_reports = json.loads(reports_search.data)
    data_authors = json.loads(authors_search.data)
    data_private_notes = json.loads(private_notes_search.data)

    assert len(data_titles["hits"]["hits"]) == 1
    assert data_titles["hits"]["hits"][0]["_id"] == expected_wf_id

    assert len(data_public_notes["hits"]["hits"]) == 1
    assert data_public_notes["hits"]["hits"][0]["_id"] == expected_wf_id

    assert len(data_journal_title["hits"]["hits"]) == 2

    assert len(data_reports["hits"]["hits"]) == 1
    assert data_reports["hits"]["hits"][0]["_id"] == expected_wf_id

    assert len(data_authors["hits"]["hits"]) == 1
    assert data_authors["hits"]["hits"][0]["_id"] == expected_wf_id

    assert len(data_private_notes["hits"]["hits"]) == 1
    assert data_private_notes["hits"]["hits"][0]["_id"] == expected_wf_id


@mock.patch('inspirehep.modules.workflows.tasks.submission.send_robotupload')
@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
def test_core_selection_continue_when_asked(mocked_create_ticket, mocked_send_robotupload, workflow_app, mocked_external_services):
    pid_value = 123456
    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=pid_value
    )
    workflow_object.extra_data['auto-approved'] = True

    expected_hep_record = {'metadata': dict(record), 'uuid': "123e4567-e89b-12d3-a456-426614174000", 'revision_id': 0}
    expected_hep_record['metadata']['core'] = True
    TestRecordMetadata.create_from_kwargs(json=record)
    create_core_selection_wf(workflow_object, None)
    wf_id = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().id
    with workflow_app.test_client() as client:
        with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
            with requests_mock.Mocker() as mock:
                mock.register_uri('GET', mocked_url, json=expected_hep_record)
                mock.register_uri(
                    'PUT', "http://web:8000/literature/{control_number}".format(control_number=pid_value),
                    json={"metadata": {"control_number": pid_value}}
                )

                login_user_via_session(client, email="cataloger@inspirehep.net")
                result = client.post("/api/workflows/{wf_id}/core-selection/continue".format(wf_id=wf_id))
                result_json = json.loads(result.data)
    expected_response = {'message': 'Workflow {} is continuing.'.format(wf_id)}
    assert result.status_code == 200
    assert result_json == expected_response
    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().status == ObjectStatus.COMPLETED
    assert mock.request_history[1].json() == expected_hep_record['metadata']


@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
def test_core_selection_complete_when_asked(mocked_create_ticket, workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['auto-approved'] = True

    hep_record = {'metadata': dict(record)}
    hep_record['metadata']['core'] = False

    create_core_selection_wf(workflow_object, None)
    wf_id = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().id
    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        result = client.post("/workflows/{wf_id}/core-selection/complete".format(wf_id=wf_id))
        result_json = json.loads(result.data)
    expected_response = {'message': 'Workflow {} is set to completed state.'.format(wf_id)}
    assert result.status_code == 200
    assert result_json == expected_response
    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().status == ObjectStatus.COMPLETED


def test_core_selection_cannot_continue_when_wf_is_not_halted(workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['auto-approved'] = True

    hep_record = {'metadata': dict(record)}
    hep_record['metadata']['core'] = True

    create_core_selection_wf(workflow_object, None)
    wf_id = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().id
    wf = workflow_object_class.get(wf_id)
    wf.status = ObjectStatus.RUNNING
    wf.save()
    db.session.commit()
    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        result = client.post("/api/workflows/{wf_id}/core-selection/continue".format(wf_id=wf_id))
        result_json = json.loads(result.data)
    expected_response = {"message": 'Workflow {} is not in halted state.'.format(wf_id)}
    assert result.status_code == 405
    assert result_json == expected_response
    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().status == ObjectStatus.RUNNING


def test_core_selection_cannot_complete_when_wf_is_not_halted(workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['auto-approved'] = True

    hep_record = {'metadata': dict(record)}
    hep_record['metadata']['core'] = True

    create_core_selection_wf(workflow_object, None)
    wf_id = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().id
    wf = workflow_object_class.get(wf_id)
    wf.status = ObjectStatus.RUNNING
    wf.save()
    db.session.commit()
    with workflow_app.test_client() as client:
        login_user_via_session(client, email="cataloger@inspirehep.net")
        result = client.post("/api/workflows/{wf_id}/core-selection/complete".format(wf_id=wf_id))
        result_json = json.loads(result.data)
    expected_response = {"message": 'Workflow {} is not in halted state.'.format(wf_id)}
    assert result.status_code == 405
    assert result_json == expected_response
    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one().status == ObjectStatus.RUNNING
