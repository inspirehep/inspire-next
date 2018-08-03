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

import pytest

from copy import deepcopy

from invenio_search import current_search_client as es
from invenio_workflows import (
    ObjectStatus,
    start,
    WorkflowEngine,
    WorkflowObject,
    workflow_object_class,
)

from inspirehep.modules.workflows.tasks.matching import (
    has_same_source,
    match_non_completed_wf_in_holdingpen,
    match_previously_rejected_wf_in_holdingpen,
    stop_matched_holdingpen_wfs,
)


@pytest.fixture
def simple_record(app):
    yield {
        'data': {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': ['Literature'],
            'document_type': ['article'],
            'titles': [{'title': 'Superconductivity'}],
            'acquisition_source': {'source': 'arXiv'},
            'dois': [{'value': '10.3847/2041-8213/aa9110'}],
        },
        'extra_data': {
            'source_data': {
                'data': {
                    '$schema': 'http://localhost:5000/schemas/records/hep.json',
                    '_collections': ['Literature'],
                    'document_type': ['article'],
                    'titles': [{'title': 'Superconductivity'}],
                    'acquisition_source': {'source': 'arXiv'},
                    'dois': [{'value': '10.3847/2041-8213/aa9110'}],
                },
                'extra_data': {},
            },
        },
    }

    _es = app.extensions['invenio-search']
    list(_es.client.indices.delete(index='holdingpen-hep'))
    list(_es.create(ignore=[400]))


def test_pending_holdingpen_matches_wf_if_not_completed(app, simple_record):
    obj = workflow_object_class.create(
        status=ObjectStatus.HALTED,
        data_type='hep',
        **simple_record
    )
    obj_id = obj.id
    obj.save()
    es.indices.refresh('holdingpen-hep')

    obj2 = WorkflowObject.create(data_type='hep', **simple_record)
    assert match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data['holdingpen_matches'] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.COMPLETED
    obj.save()
    es.indices.refresh('holdingpen-hep')

    # doesn't match anymore because obj is COMPLETED
    assert not match_non_completed_wf_in_holdingpen(obj2, None)


def test_match_previously_rejected_wf_in_holdingpen(app, simple_record):
    obj = workflow_object_class.create(
        status=ObjectStatus.COMPLETED,
        data_type='hep',
        **simple_record
    )
    obj_id = obj.id
    obj.extra_data['approved'] = False  # reject it
    obj.save()
    es.indices.refresh('holdingpen-hep')

    obj2 = WorkflowObject.create(data_type='hep', **simple_record)
    assert match_previously_rejected_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data['previously_rejected_matches'] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.HALTED
    obj.save()
    es.indices.refresh('holdingpen-hep')

    # doesn't match anymore because obj is COMPLETED
    assert not match_previously_rejected_wf_in_holdingpen(obj2, None)


def test_has_same_source(app, simple_record):
    obj = workflow_object_class.create(
        status=ObjectStatus.HALTED,
        data_type='hep',
        **simple_record
    )
    obj_id = obj.id
    obj.save()
    es.indices.refresh('holdingpen-hep')

    obj2 = WorkflowObject.create(data_type='hep', **simple_record)
    match_non_completed_wf_in_holdingpen(obj2, None)

    same_source_func = has_same_source('holdingpen_matches')

    assert same_source_func(obj2, None)
    assert obj2.extra_data['holdingpen_matches'] == [obj_id]

    # change source and match the wf in the holdingpen
    different_source_rec = deepcopy(simple_record)
    different_source_rec['data']['acquisition_source'] = {'source': 'different'}
    obj3 = WorkflowObject.create(data_type='hep', **different_source_rec)

    assert match_non_completed_wf_in_holdingpen(obj3, None)
    assert not same_source_func(obj3, None)


def test_stop_matched_holdingpen_wfs(app, simple_record):
    # need to run a wf in order to assign to it the wf definition and a uuid
    # for it

    obj = workflow_object_class.create(
        data_type='hep',
        **simple_record
    )
    workflow_uuid = start('article', object_id=obj.id)
    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj.status = ObjectStatus.HALTED
    obj.save()
    obj_id = obj.id
    es.indices.refresh('holdingpen-hep')

    obj2 = WorkflowObject.create(data_type='hep', **simple_record)
    obj2_id = obj2.id

    match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data['holdingpen_matches'] == [obj_id]

    stop_matched_holdingpen_wfs(obj2, None)

    stopped_wf = workflow_object_class.get(obj_id)
    assert stopped_wf.status == ObjectStatus.COMPLETED
    assert stopped_wf.extra_data['stopped-by-wf'] == obj2_id
