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

from copy import deepcopy
import json

from invenio_accounts.testutils import login_user_via_session
from invenio_workflows import workflow_object_class
from invenio_db import db

from factories.db.invenio_records import TestRecordMetadata
from workflow_utils import build_workflow


def test_inspect_merge_view(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={'titles': [{'title': 'Curated version'}]}
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type='hep',
    )
    obj.save()
    db.session.commit()

    head = deepcopy(factory.record_metadata.json)
    factory.record_metadata.json['titles'][0]['title'] = 'second curated version'
    db.session.add(factory.record_metadata)
    db.session.commit()

    obj.extra_data['merger_root'] = {
        'titles': [{'title': 'Second version'}],
        'document_type': ['article'],
        '_collections': ['Literature'],
    }
    obj.extra_data['merger_original_root'] = {
        'titles': [{'title': 'First version'}],
        'document_type': ['article'],
        '_collections': ['Literature'],
    }
    obj.extra_data['merger_head_revision'] = factory.inspire_record.revision_id

    expected = {
        'root': obj.extra_data['merger_original_root'],
        'head': head,
        'update': obj.extra_data['merger_root'],
        'merged': factory.record_metadata.json
    }

    with workflow_app.test_client() as client:
        response = client.get('/workflows/inspect_merge/{}'.format(obj.id))
        assert response.status_code == 200
        assert json.loads(response.data) == expected


def test_inspect_merge_view_returns_400(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={'titles': [{'title': 'Curated version'}]}
    )

    obj = workflow_object_class.create(
        data=factory.record_metadata.json,
        data_type='hep',
    )
    obj.save()
    db.session.commit()

    with workflow_app.test_client() as client:
        response = client.get('/workflows/inspect_merge/{}'.format(obj.id))
        assert response.status_code == 400


def test_responses_with_etag(workflow_app):

    factory = TestRecordMetadata.create_from_kwargs(
        json={'titles': [{'title': 'Etag version'}]}
    )

    workflow_id = build_workflow(factory.record_metadata.json).id
    obj = workflow_object_class.get(workflow_id)
    obj.save()
    db.session.commit()

    workflow_url = '/api/holdingpen/{}'.format(obj.id)

    with workflow_app.test_client() as client:
        login_user_via_session(client, email='cataloger@inspirehep.net')
        response = client.get(workflow_url)
        assert response.status_code == 200

        etag = response.headers['ETag']
        last_modified = response.headers['Last-Modified']

        response = client.get(
            workflow_url, headers={'If-Modified-Since': last_modified})
        assert response.status_code == 304

        response = client.get(workflow_url, headers={'If-None-Match': etag})
        assert response.status_code == 304

        response = client.get(workflow_url, headers={'If-None-Match': 'Jessica Jones'})
        assert response.status_code == 200


def test_new_author_submit_with_required_fields(api_client):
    data = {
        "data": {
            "_collections": [
                "Authors"
            ],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": "None",
                "internal_uid": 1,
            },
            "name": {
                "value": "Martinez, Diegpo"
            },
            "status": "active"
        }
    }
    response = api_client.post('/workflows/authors', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    workflow_object_id = json.loads(response.data).get('workflow_object_id')
    assert workflow_object_id is not None

    obj = workflow_object_class.get(workflow_object_id)

    expected = {
        "status": "active",
        "$schema": "http://localhost:5000/schemas/records/authors.json",
        "acquisition_source": {
            "method": "submitter",
            "internal_uid": 1,
            "email": "john.doe@gmail.com",
            "submission_number": "1",
            "datetime": "2019-02-04T10:06:34.695915"
        },
        "_collections": [
            "Authors"
        ],
        "name": {
            "value": "Martinez, Diegpo"
        }
    }

    assert expected == obj.data

    assert obj.extra_data['is-update'] is False


def test_update_author_submit_with_required_fields(api_client):
    data = {
        "data": {
            "_collections": [
                "Authors"
            ],
            "acquisition_source": {
                "email": "john.doe@gmail.com",
                "datetime": "2019-02-04T10:06:34.695915",
                "method": "submitter",
                "submission_number": "None",
                "internal_uid": 1,
            },
            "name": {
                "value": "Martinez, Diegpo"
            },
            "status": "active",
            "control_number": 3
        }
    }
    response = api_client.post('/workflows/authors', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    workflow_object_id = json.loads(response.data).get('workflow_object_id')
    assert workflow_object_id is not None

    obj = workflow_object_class.get(workflow_object_id)

    expected = {
        "status": "active",
        "$schema": "http://localhost:5000/schemas/records/authors.json",
        "acquisition_source": {
            "method": "submitter",
            "internal_uid": 1,
            "email": "john.doe@gmail.com",
            "submission_number": "1",
            "datetime": "2019-02-04T10:06:34.695915"
        },
        "_collections": [
            "Authors"
        ],
        "name": {
            "value": "Martinez, Diegpo"
        },
        "control_number": 3
    }

    assert expected == obj.data

    assert obj.extra_data['is-update'] is True
