# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
from __future__ import absolute_import, division, print_function

import mock as mock
from invenio_workflows import ObjectStatus, start, workflow_object_class
from invenio_workflows.models import WorkflowObjectModel
from mocks import (fake_classifier_api_request, fake_download_file,
                   fake_magpie_api_request)
from workflow_utils import build_workflow
from utils import override_config


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_workflow_non_core_selection_is_created_when_secondary_arxiv_category(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):
    record = {
        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
        "titles": [
            {"title": "Update without conflicts title."},
        ],
        "arxiv_eprints": [
            {"categories": ["nucl-ex", "hep-lat", "hep-th"], "value": "1703.04802"}
        ],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "acquisition_source": {
            "datetime": "2020-11-12T04:49:13.369515",
            "method": "hepcrawl",
            "submission_number": "978",
            "source": "Elsevier",
        },
    }
    workflow_id = build_workflow(record).id
    with override_config(FEATURE_FLAG_ENABLE_SEND_TO_LEGACY=False):
        start("article", object_id=workflow_id)

    assert (
        WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="non_core_selection")
        ).count()
        == 1
    )
    non_core_selection_wf = WorkflowObjectModel.query.filter(
        WorkflowObjectModel.workflow.has(name="non_core_selection")
    ).one()
    assert non_core_selection_wf.status == ObjectStatus.COMPLETED


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_workflow_non_core_selection_is_not_created_for_updates(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):
    record = {
        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
        "titles": [
            {"title": "Update without conflicts title."},
        ],
        "arxiv_eprints": [
            {"categories": ["nucl-ex", "hep-lat", "hep-th"], "value": "1703.04802"}
        ],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "acquisition_source": {
            "datetime": "2020-11-12T04:49:13.369515",
            "method": "hepcrawl",
            "submission_number": "978",
            "source": "Elsevier",
        },
    }
    with override_config(FEATURE_FLAG_ENABLE_SEND_TO_LEGACY=False):
        workflow_id = build_workflow(record).id
        start("article", object_id=workflow_id)
        wf = workflow_object_class.get(workflow_id)
        assert (
            WorkflowObjectModel.query.filter(
                WorkflowObjectModel.workflow.has(name="non_core_selection")
            ).count()
            == 1
        )
        non_core_selection_wf = WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="non_core_selection")
        ).one()

        wf.callback_pos = [34, 1, 13]
        wf.extra_data['auto-approved'] = True
        wf.extra_data['is-update'] = True
        wf.save()

        wf.continue_workflow('restart_task')

        non_core_wfs = WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="non_core_selection")
        ).all()

        assert len(non_core_wfs) == 1
        assert non_core_wfs[0].id == non_core_selection_wf.id


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.classifier.json_api_request',
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_workflow_non_core_selection_is_not_created_when_secondary_category_arent_core(
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):
    record = {
        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
        "titles": [
            {"title": "Update without conflicts title."},
        ],
        "arxiv_eprints": [
            {"categories": ["hep-th", "astro-ph"], "value": "1703.04802"}
        ],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "acquisition_source": {
            "datetime": "2020-11-12T04:49:13.369515",
            "method": "hepcrawl",
            "submission_number": "978",
            "source": "Elsevier",
        },
    }
    with override_config(FEATURE_FLAG_ENABLE_SEND_TO_LEGACY=False):
        workflow_id = build_workflow(record).id
        start("article", object_id=workflow_id)

        assert (
            WorkflowObjectModel.query.filter(
                WorkflowObjectModel.workflow.has(name="non_core_selection")
            ).count()
            == 0
        )
