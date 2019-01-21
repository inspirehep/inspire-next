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

import time

from datetime import datetime, timedelta

from copy import deepcopy

from invenio_db import db
from invenio_search import current_search_client as es
from invenio_workflows import ObjectStatus, start, workflow_object_class


def check_wf_state(workflow_id, desired_status, max_time=600):
    """Waits for the workflow to go to desired status
    Args:
        workflow: workflow to check
        desired_state: desired state
        max_time: maximum time to wait in seconds, otherwise raise exception

    Returns: None

    """
    start = datetime.now()
    end = start + timedelta(seconds=max_time)
    while (True):
        db.session.close()
        if workflow_object_class.get(workflow_id).status == desired_status:
            return
        if datetime.now() > end:
            raise AssertionError
        time.sleep(1)


def test_wf_not_stops_when_blocking_another_one_after_restarted_on_running(
    app,
    celery_app_with_context,
    celery_session_worker
):
    def build_workflow(workflow_data, data_type='hep', **kwargs):
        workflow_object = workflow_object_class.create(
            data_type=data_type,
            data=workflow_data,
            extra_data={
                'source_data': {
                    'data': deepcopy(workflow_data),
                    'extra_data': {},
                }
            },
            **kwargs
        )
        return workflow_object

    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    record = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
        'titles': [
            {
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

    workflow = build_workflow(record)
    workflow.status = ObjectStatus.RUNNING
    workflow.save()
    record['titles'][0]['title'] = 'second title?'
    workflow2 = build_workflow(record)
    workflow2.save()
    record['titles'].append({'title': 'thirtd_title'})
    workflow3 = build_workflow(record)
    workflow3.save()
    db.session.commit()

    wf1_id = workflow.id
    wf2_id = workflow2.id
    wf3_id = workflow3.id

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.RUNNING)
    check_wf_state(wf2_id, ObjectStatus.INITIAL)
    check_wf_state(wf3_id, ObjectStatus.INITIAL)

    start.delay('article', object_id=wf3_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.RUNNING)
    check_wf_state(wf2_id, ObjectStatus.INITIAL)
    check_wf_state(wf3_id, ObjectStatus.ERROR)

    start.delay('article', object_id=wf2_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.RUNNING)
    check_wf_state(wf2_id, ObjectStatus.ERROR)
    check_wf_state(wf3_id, ObjectStatus.ERROR)

    start.delay('article', object_id=wf1_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.COMPLETED)
    check_wf_state(wf2_id, ObjectStatus.COMPLETED)
    check_wf_state(wf3_id, ObjectStatus.COMPLETED)

    wf1 = workflow_object_class.get(wf1_id)
    wf2 = workflow_object_class.get(wf2_id)
    wf3 = workflow_object_class.get(wf3_id)

    assert wf1.data['control_number'] == wf2.data['control_number']
    assert wf2.data['control_number'] == wf3.data['control_number']

    assert wf1.extra_data.get('restarted-by-wf') is None
    assert wf2.extra_data.get('restarted-by-wf') == [1]
    assert wf3.extra_data.get('restarted-by-wf') == [2]


def test_wf_not_stops_when_blocking_another_one_after_restarted_on_init(
    app,
    celery_app_with_context,
    celery_session_worker
):
    def build_workflow(workflow_data, data_type='hep', **kwargs):
        workflow_object = workflow_object_class.create(
            data_type=data_type,
            data=workflow_data,
            extra_data={
                'source_data': {
                    'data': deepcopy(workflow_data),
                    'extra_data': {},
                }
            },
            **kwargs
        )
        return workflow_object

    app.config['FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY'] = False
    app.config['PRODUCTION_MODE'] = False
    record = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
        'titles': [
            {
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

    workflow = build_workflow(record)
    workflow.save()
    record['titles'][0]['title'] = 'second title?'
    workflow2 = build_workflow(record)
    workflow2.save()
    record['titles'].append({'title': 'thirtd_title'})
    workflow3 = build_workflow(record)
    workflow3.save()
    db.session.commit()

    wf1_id = workflow.id
    wf2_id = workflow2.id
    wf3_id = workflow3.id

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.INITIAL)
    check_wf_state(wf2_id, ObjectStatus.INITIAL)
    check_wf_state(wf3_id, ObjectStatus.INITIAL)

    start.delay('article', object_id=wf3_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.INITIAL)
    check_wf_state(wf2_id, ObjectStatus.INITIAL)
    check_wf_state(wf3_id, ObjectStatus.ERROR)

    start.delay('article', object_id=wf2_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.INITIAL)
    check_wf_state(wf2_id, ObjectStatus.ERROR)
    check_wf_state(wf3_id, ObjectStatus.ERROR)

    start.delay('article', object_id=wf1_id)

    es.indices.refresh('holdingpen-hep')

    check_wf_state(wf1_id, ObjectStatus.COMPLETED)
    check_wf_state(wf2_id, ObjectStatus.COMPLETED)
    check_wf_state(wf3_id, ObjectStatus.COMPLETED)

    wf1 = workflow_object_class.get(wf1_id)
    wf2 = workflow_object_class.get(wf2_id)
    wf3 = workflow_object_class.get(wf3_id)

    assert wf1.data['control_number'] == wf2.data['control_number']
    assert wf2.data['control_number'] == wf3.data['control_number']

    assert wf1.extra_data.get('restarted-by-wf') is None
    assert wf2.extra_data.get('restarted-by-wf') == [1]
    assert wf3.extra_data.get('restarted-by-wf') == [2]
