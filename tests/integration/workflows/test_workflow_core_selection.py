# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
from __future__ import absolute_import, division, print_function

import json
import os

import mock as mock
import pkg_resources
import requests_mock
from calls import do_accept_core
from flask import current_app
from invenio_workflows import (ObjectStatus, WorkflowObject, start,
                               workflow_object_class)
from invenio_workflows.models import WorkflowObjectModel
from mocks import fake_classifier_api_request, fake_magpie_api_request
from utils import override_config


def load_json_record(record_file):
    return json.loads(pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            record_file
        )
    ))


@mock.patch('inspirehep.modules.workflows.tasks.submission.send_robotupload')
@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_starts_after_article_wf_when_no_core(mocked_api_request_magpie, mocked_api_request_classifier, mocked_rt, mocked_send_robotupload, workflow_app, mocked_external_services):
    pid_value = 123456
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=pid_value
    )
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
        "control_number": pid_value,
    }

    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()

    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri('GET', mocked_url, json=load_json_record('hep_record_no_core.json'))
            # It's update so it should be PUT
            mock.register_uri(
                'PUT',
                "http://web:8000/literature/{control_number}".format(control_number=pid_value),
                json={
                    "metadata": {"control_number": pid_value},
                    'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
                    'revision_id': 3
                }
            )

            start("article", object_id=workflow_object.id)

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

            workflow_object.callback_pos = [34, 1, 13]
            #  Run task for creating core_selection wf
            workflow_object.extra_data['auto-approved'] = True
            workflow_object.save()
            workflow_object.continue_workflow('restart_task')

            core_selection_wf = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one()
            assert core_selection_wf.status == ObjectStatus.HALTED
            core_selection_wf_object = WorkflowObject(model=core_selection_wf)
            core_selection_wf_object_id = core_selection_wf_object.id
            # we simulate accept_core user action
            do_accept_core(app=workflow_app, workflow_id=core_selection_wf_object.id)
            core_selection_wf = workflow_object_class.get(core_selection_wf_object_id)

            assert core_selection_wf.status == ObjectStatus.COMPLETED
            assert core_selection_wf.data['control_number'] == pid_value
            assert 3 == core_selection_wf.extra_data['head_version_id']
            assert 'head_uuid' in core_selection_wf.extra_data

    expected_record_data = load_json_record('hep_record_no_core.json')['metadata']
    expected_record_data['core'] = True

    assert len(mock.request_history) == 2
    # Check is record sent to HEP is correct (only core has changed)
    assert mock.request_history[1].json() == expected_record_data


@mock.patch('inspirehep.modules.workflows.tasks.submission.send_robotupload')
@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_is_not_created_when_wf_is_record_update(mocked_api_request_magpie, mocked_api_request_classifier, mocked_rt, mocked_send_robotupload, workflow_app, mocked_external_services):
    pid_value = 123456
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=pid_value
    )
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
        "control_number": pid_value,
    }

    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()

    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri('GET', mocked_url, json=load_json_record('hep_record_no_core.json'))
            mock.register_uri(
                'PUT',
                "http://web:8000/literature/{control_number}".format(control_number=pid_value),
                json={
                    "metadata": {"control_number": pid_value},
                    'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
                    'revision_id': 3
                }
            )

            start("article", object_id=workflow_object.id)

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

            workflow_object.callback_pos = [34, 1, 13]
            #  Run task for creating core_selection wf
            workflow_object.extra_data['auto-approved'] = True
            workflow_object.extra_data['is-update'] = True
            workflow_object.save()

            workflow_object.continue_workflow('restart_task')

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0
            assert workflow_object.status == ObjectStatus.COMPLETED


@mock.patch('inspirehep.modules.workflows.tasks.submission.send_robotupload')
@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_works_when_there_is_record_redirection_on_hep(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_rt,
    mocked_send_robotupload,
    workflow_app,
    mocked_external_services,
):
    original_pid_value = 654321
    redirected_pid = 123456
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=original_pid_value
    )
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
        "control_number": original_pid_value,
    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()
    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri('GET', mocked_url, json=load_json_record('hep_record_no_core.json'))
            # It's update so it should be PUT
            mock.register_uri(
                'PUT',
                "http://web:8000/literature/{control_number}".format(control_number=redirected_pid),
                json={
                    "metadata": {"control_number": redirected_pid},
                    'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
                    'revision_id': 3
                }
            )

            start("article", object_id=workflow_object.id)

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

            workflow_object.callback_pos = [34, 1, 13]
            #  Run task for creating core_selection wf
            workflow_object.extra_data['auto-approved'] = True
            workflow_object.save()
            workflow_object.continue_workflow('restart_task')

            core_selection_wf = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one()
            assert core_selection_wf.status == ObjectStatus.HALTED
            core_selection_wf_object = WorkflowObject(model=core_selection_wf)
            core_selection_wf_object_id = core_selection_wf_object.id
            # we simulate accept_core user action
            do_accept_core(app=workflow_app, workflow_id=core_selection_wf_object.id)
            core_selection_wf = workflow_object_class.get(core_selection_wf_object_id)
            assert core_selection_wf.status == ObjectStatus.COMPLETED
            assert core_selection_wf.data['control_number'] == redirected_pid

    expected_record_data = load_json_record('hep_record_no_core.json')['metadata']
    expected_record_data['core'] = True

    assert len(mock.request_history) == 2
    # Check is record sent to HEP is correct (only core has changed)
    assert mock.request_history[1].json() == expected_record_data


@mock.patch('inspirehep.modules.workflows.tasks.submission.send_robotupload')
@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_still_runs_when_there_is_core_on_hep_already(mocked_api_request_magpie, mocked_api_request_classifier, mocked_rt, mocked_send_robotupload, workflow_app, mocked_external_services):
    pid_value = 123456
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=pid_value
    )
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
        "control_number": pid_value,
    }
    expected_hep_record = {
        'metadata': dict(record),
        'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
        'revision_id': 2
    }
    expected_hep_record['metadata']['core'] = True

    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()
    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri('GET', mocked_url, json=expected_hep_record)
            mock.register_uri(
                'PUT',
                "http://web:8000/literature/{control_number}".format(control_number=pid_value),
                json={
                    "metadata": {"control_number": pid_value},
                    'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
                    'revision_id': 3
                }
            )
            start("article", object_id=workflow_object.id)

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

            workflow_object.callback_pos = [34, 1, 13]
            #  Run task for creating core_selection wf
            workflow_object.extra_data['auto-approved'] = True
            workflow_object.save()
            workflow_object.continue_workflow('restart_task')

            core_selection_wf = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one()
            assert core_selection_wf.status == ObjectStatus.HALTED
            core_selection_wf_object = WorkflowObject(model=core_selection_wf)
            core_selection_wf_object_id = core_selection_wf_object.id
            # we simulate accept_core user action
            do_accept_core(app=workflow_app, workflow_id=core_selection_wf_object.id)
            core_selection_wf = workflow_object_class.get(core_selection_wf_object_id)
            assert core_selection_wf.status == ObjectStatus.COMPLETED

    assert len(mock.request_history) == 2
    assert mock.request_history[1].json() == expected_hep_record['metadata']


@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket', return_value="1234")
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_skipped_if_record_was_manually_approved(mocked_api_request_magpie, mocked_api_request_classifier, mocked_rt, workflow_app, mocked_external_services):
    pid_value = 123456
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint='literature',
        control_number=pid_value
    )
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
        "control_number": pid_value,
    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()

    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri('GET', mocked_url, json=load_json_record('hep_record_no_core.json'))
            # It's update so it should be PUT
            mock.register_uri(
                'PUT',
                "http://web:8000/literature/{control_number}".format(control_number=pid_value),
                json={
                    "metadata": {"control_number": pid_value},
                    'uuid': "4915b428-618e-40f9-a289-b01e11a2cb87",
                    'revision_id': 3
                }
            )

            start("article", object_id=workflow_object.id)

            workflow_object.callback_pos = [34, 1, 13]
            #  Run task for creating core_selection wf
            workflow_object.extra_data['auto-approved'] = False
            workflow_object.save()
            workflow_object.continue_workflow('restart_task')

            assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0


@mock.patch("inspirehep.modules.workflows.tasks.submission.send_robotupload")
@mock.patch(
    "inspirehep.modules.workflows.tasks.submission.submit_rt_ticket",
    return_value="1234",
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_removes_arxiv_core_categories_when_marked_as_non_core(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_rt,
    mocked_send_robotupload,
    workflow_app,
    mocked_external_services,
):
    pid_value = 2130167
    mocked_url = "{inspirehep_url}/{endpoint}/{control_number}".format(
        inspirehep_url=current_app.config.get("INSPIREHEP_URL"),
        endpoint="literature",
        control_number=pid_value,
    )
    record = {
        "_collections": ["Literature"],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["report"],
        "collaborations": [{"value": "SHIP"}],
        "arxiv_eprints": [
            {
                "categories": [
                    "physics.optics",
                    "quant-ph",
                    "astro-ph.CO",
                ],
                "value": "2208.00828",
            }
        ],
        "inspire_categories": [
            {"source": "arxiv", "term": "Astrophysics"},
            {"source": "arxiv", "term": "General Physics"},
            {"source": "arxiv", "term": "Quantum Physics"},
        ],
    }
    workflow_object = workflow_object_class.create(
        data=record, id_user=None, data_type="hep"
    )
    workflow_object.extra_data["source_data"] = {
        "data": record,
        "extra_data": {"source_data": {"data": record}},
    }
    workflow_object.save()

    with override_config(FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT=True):
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "GET", mocked_url, json=load_json_record("non_core_2208_00828.json")
            )
            mock.register_uri(
                "POST",
                "http://web:8000/literature",
                json={
                    "metadata": {"control_number": pid_value},
                    "uuid": "c1b958b6-39e4-4aaf-aea1-ee676176f7fc",
                    "revision_id": 3,
                },
            )
            mock.register_uri(
                "PUT",
                "http://web:8000/literature/{control_number}".format(
                    control_number=pid_value
                ),
                json={
                    "metadata": {"control_number": pid_value},
                    "uuid": "c1b958b6-39e4-4aaf-aea1-ee676176f7fc",
                    "revision_id": 4,
                },
            )

            start("article", object_id=workflow_object.id)

            core_selection_wf = WorkflowObjectModel.query.filter(
                WorkflowObjectModel.workflow.has(name="core_selection")
            ).one()
            core_selection_wf_object = WorkflowObject(model=core_selection_wf)
            core_selection_wf_object.continue_workflow("continue_next")

            assert core_selection_wf.status == ObjectStatus.COMPLETED
            assert core_selection_wf.data["control_number"] == pid_value
            # Expect inspire_categories to contain only one non-core category
            assert len(core_selection_wf.data["inspire_categories"]) == 2
            assert {
                "source": "arxiv",
                "term": "Astrophysics",
            } in core_selection_wf.data["inspire_categories"]
            assert {
                "source": "arxiv",
                "term": "Quantum Physics",
            } in core_selection_wf.data["inspire_categories"]
