# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2019 CERN.
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

import uuid

import time
from inspirehep.modules.workflows.utils import _get_headers_for_hep_root_table_request
import pytest
import requests_mock

from datetime import datetime, timedelta

from copy import deepcopy

from invenio_db import db
from invenio_search import current_search
from invenio_workflows import ObjectStatus, start, workflow_object_class, Workflow


def build_workflow(workflow_data, data_type='hep', extra_data=None, status=None, **kwargs):
    extra_data = extra_data or {}
    if 'source_data' not in extra_data:
        extra_data = {
            'source_data': {
                'data': deepcopy(workflow_data),
                'extra_data': extra_data,
            }
        }
    wf = Workflow(name='article', extra_data=extra_data, uuid=uuid.uuid4())
    wf.save()
    workflow_object = workflow_object_class.create(
        data=workflow_data,
        data_type=data_type,
        extra_data=extra_data,
        **kwargs
    )
    if status:
        workflow_object.status = status
    workflow_object.save(id_workflow=wf.uuid)

    return workflow_object


def check_wf_state(workflow_id, desired_status, max_time=550):  # Travis fails after 600s without output
    """Waits for the workflow to go to desired status
    Args:
        workflow: workflow to check
        desired_state: desired state
        max_time: maximum time to wait in seconds, otherwise raise exception
    Returns: None
    """
    start = datetime.now()
    end = start + timedelta(seconds=max_time)
    while True:
        db.session.close()
        if workflow_object_class.get(workflow_id).status == desired_status:
            return
        if datetime.now() > end:
            raise AssertionError(
                "Status for workflow: %s didn't changed to %s for %s seconds" % (
                    workflow_id, desired_status, max_time
                )
            )
        time.sleep(5)


@pytest.mark.xfail
def test_wf_not_stops_when_blocking_another_one_after_restarted_on_running(
    app,
    celery_app_with_context,
    celery_session_worker
):
    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    record = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
        'titles': [
            {
                "source": "arxiv",
                'title': 'Update without conflicts title.'
            },
        ],
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '9999.9999'
            }
        ],
        'document_type': ['article'],
        '_collections': ['Literature'],
        'acquisition_source': {'source': 'arXiv'},
        'keywords': [{'value': 'none'}]
    }
    with requests_mock.Mocker(real_http=True) as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": []
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow = build_workflow(record, status=ObjectStatus.RUNNING)
        workflow.save()
        record['titles'][0]['source'] = 'something_else'
        workflow2 = build_workflow(record)
        workflow2.save()
        record['titles'].append({
            "source": "arxiv",
            'title': 'Update without conflicts title.'
        },)
        workflow3 = build_workflow(record)
        workflow3.save()
        db.session.commit()

        wf1_id = workflow.id
        wf2_id = workflow2.id
        wf3_id = workflow3.id

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.RUNNING)
        check_wf_state(wf2_id, ObjectStatus.INITIAL)
        check_wf_state(wf3_id, ObjectStatus.INITIAL)

        start.delay('article', object_id=wf3_id)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.RUNNING)
        check_wf_state(wf2_id, ObjectStatus.INITIAL)
        check_wf_state(wf3_id, ObjectStatus.ERROR)

        start.delay('article', object_id=wf2_id)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.RUNNING)
        check_wf_state(wf2_id, ObjectStatus.ERROR)
        check_wf_state(wf3_id, ObjectStatus.ERROR)

        start.delay('article', object_id=wf1_id)

        current_search.flush_and_refresh('holdingpen-hep')
        check_wf_state(wf1_id, ObjectStatus.COMPLETED)
        check_wf_state(wf2_id, ObjectStatus.COMPLETED)
        check_wf_state(wf3_id, ObjectStatus.COMPLETED)

        wf1 = workflow_object_class.get(wf1_id)
        wf2 = workflow_object_class.get(wf2_id)
        wf3 = workflow_object_class.get(wf3_id)

        assert wf1.data['control_number'] == wf2.data['control_number']
        assert wf2.data['control_number'] == wf3.data['control_number']

        assert wf1.extra_data.get('restarted-by-wf') is None
        assert set(wf2.extra_data.get('restarted-by-wf')) == {1}
        assert set(wf3.extra_data.get('restarted-by-wf')) == {2}


@pytest.mark.xfail
def test_wf_not_stops_when_blocking_another_one_after_restarted_on_init(
    app,
    celery_app_with_context,
    celery_session_worker
):
    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    record = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
        'titles': [
            {
                "source": "arxiv",
                'title': 'Update without conflicts title.'
            },
        ],
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '9999.9999'
            }
        ],
        'document_type': ['article'],
        '_collections': ['Literature'],
        'acquisition_source': {'source': 'arXiv'},
        'keywords': [{'value': 'none'}]
    }
    with requests_mock.Mocker(real_http=True) as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": []
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow = build_workflow(record)
        workflow.save()
        record['titles'][0]['source'] = 'something_else'
        workflow2 = build_workflow(record)
        workflow2.save()
        record['titles'].append({
            "source": "arxiv",
            'title': 'Update without conflicts title.'
        },)
        workflow3 = build_workflow(record)
        workflow3.save()
        db.session.commit()

        wf1_id = workflow.id
        wf2_id = workflow2.id
        wf3_id = workflow3.id

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.INITIAL)
        check_wf_state(wf2_id, ObjectStatus.INITIAL)
        check_wf_state(wf3_id, ObjectStatus.INITIAL)

        start.delay('article', object_id=wf3_id)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.INITIAL)
        check_wf_state(wf2_id, ObjectStatus.INITIAL)
        check_wf_state(wf3_id, ObjectStatus.ERROR)

        start.delay('article', object_id=wf2_id)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.INITIAL)
        check_wf_state(wf2_id, ObjectStatus.ERROR)
        check_wf_state(wf3_id, ObjectStatus.ERROR)

        start.delay('article', object_id=wf1_id)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.COMPLETED)
        check_wf_state(wf2_id, ObjectStatus.COMPLETED)
        check_wf_state(wf3_id, ObjectStatus.COMPLETED)

        wf1 = workflow_object_class.get(wf1_id)
        wf2 = workflow_object_class.get(wf2_id)
        wf3 = workflow_object_class.get(wf3_id)

        assert wf1.data['control_number'] == wf2.data['control_number']
        assert wf2.data['control_number'] == wf3.data['control_number']

        assert wf1.extra_data.get('restarted-by-wf') is None
        assert set(wf2.extra_data.get('restarted-by-wf')) == {1}
        assert set(wf3.extra_data.get('restarted-by-wf')) == {2}


@pytest.mark.vcr()
def test_wf_replaces_old_workflow_which_is_in_halted_state(
    app,
    celery_app_with_context,
    celery_session_worker,
    generated_record
):
    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    app.config['USE_SIGNALS_ON_TIMEOUT'] = False
    record = generated_record
    with requests_mock.Mocker(real_http=True) as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": []
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "POST",
            "http://web:8000/matcher/linked_references/",
            json={
                "references": [
                    {
                        "record": {
                            "$ref": "http://localhost:5000/api/literature/1000",
                        },
                        "raw_refs": [
                            {
                                "source": "submitter",
                                "schema": "That's a schema",
                                "value": "That's a reference",
                            }
                        ],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow = build_workflow(record)

        workflow.save()

        db.session.commit()

        wf1_id = workflow.id

        start.delay('article', object_id=wf1_id)
        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.HALTED)

        workflow2 = build_workflow(record)
        workflow2.save()
        db.session.commit()
        wf2_id = workflow2.id

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.HALTED)
        check_wf_state(wf2_id, ObjectStatus.INITIAL)

        start.delay('article', object_id=wf2_id)

        current_search.flush_and_refresh('holdingpen-hep')
        check_wf_state(wf1_id, ObjectStatus.COMPLETED)
        check_wf_state(wf2_id, ObjectStatus.HALTED)


@pytest.mark.vcr()
def test_wf_rejects_automatically_when_previous_matched_wf_was_rejected(
    app,
    celery_app_with_context,
    celery_session_worker,
    generated_record
):
    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    app.config['USE_SIGNALS_ON_TIMEOUT'] = False
    record = generated_record
    with requests_mock.Mocker(real_http=True) as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": []
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "POST",
            "http://web:8000/matcher/linked_references/",
            json={
                "references": [
                    {
                        "record": {
                            "$ref": "http://localhost:5000/api/literature/1000",
                        },
                        "raw_refs": [
                            {
                                "source": "submitter",
                                "schema": "That's a schema",
                                "value": "That's a reference",
                            }
                        ],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow = build_workflow(record)

        workflow.save()

        db.session.commit()

        wf1_id = workflow.id

        start.delay('article', object_id=wf1_id)
        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.HALTED)
        wf1 = workflow_object_class.get(wf1_id)
        wf1.extra_data["approved"] = False
        wf1.continue_workflow(delayed=True)

        current_search.flush_and_refresh('holdingpen-hep')

        check_wf_state(wf1_id, ObjectStatus.COMPLETED)
        wf1 = workflow_object_class.get(wf1_id)
        assert wf1.extra_data.get("approved") is False

        workflow2 = build_workflow(record)
        workflow2.save()
        db.session.commit()
        wf2_id = workflow2.id
        start.delay('article', object_id=wf2_id)

        current_search.flush_and_refresh("holdingpen-hep")

        check_wf_state(wf2_id, ObjectStatus.COMPLETED)
        wf2 = workflow_object_class.get(wf2_id)

        assert wf2.extra_data["previously_rejected"] is True
        assert wf2.extra_data["previously_rejected_matches"] == [wf1_id]
