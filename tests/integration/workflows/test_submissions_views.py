# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
import json

from invenio_accounts.testutils import login_user_via_session
from invenio_workflows import workflow_object_class


def test_new_author_submit_without_authentication_post(api_client):
    response = api_client.post(
        '/submissions/authors',
        content_type='application/json',
        data=json.dumps({
            'data': {
                'given_name': 'Harun',
                'display_name': 'Harun Urhan',
                'status': 'active'
            }
        })
    )
    assert response.status_code == 401


def test_new_author_submit_without_authentication_get(api_client):
    response = api_client.get(
        '/submissions/authors',
        content_type='application/json',
    )
    assert response.status_code == 401


def test_new_author_submit_without_authentication_put(api_client):
    response = api_client.put(
        '/submissions/authors',
        content_type='application/json',
        data=json.dumps({
            'data': {
                'given_name': 'Harun',
                'display_name': 'Harun Urhan',
                'status': 'active'
            }
        })
    )
    assert response.status_code == 401


@pytest.mark.xfail(reason="Submission endpoint is no longer in use")
def test_new_author_submit_with_required_fields(api_client):
    login_user_via_session(api_client, email='johndoe@inspirehep.net')

    response = api_client.post(
        '/submissions/authors',
        content_type='application/json',
        data=json.dumps({
            'data': {
                'given_name': 'Harun',
                'display_name': 'Harun Urhan',
                'status': 'active'
            }
        })
    )
    assert response.status_code == 200

    workflow_object_id = json.loads(response.data).get('workflow_object_id')

    assert workflow_object_id is not None

    obj = workflow_object_class.get(workflow_object_id)

    expected = {
        '_collections': ['Authors'],
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        'name': {
            'preferred_name': 'Harun Urhan',
            'value': 'Harun'
        },
        'status': 'active',
        'acquisition_source': {
            'datetime': obj.data['acquisition_source']['datetime'],
            'email': 'johndoe@inspirehep.net',
            'internal_uid': 5,
            'method': 'submitter',
            'submission_number': str(obj.id)
        }
    }

    assert expected == obj.data

    assert obj.extra_data['is-update'] is False


def test_update_author_submit_with_required_fields(api_client):
    login_user_via_session(api_client, email='johndoe@inspirehep.net')

    response = api_client.put(
        '/submissions/authors/123',
        content_type='application/json',
        data=json.dumps({
            'data': {
                'given_name': 'Harun',
                'display_name': 'Harun Urhan',
                'status': 'active'
            }
        })
    )
    assert response.status_code == 200

    workflow_object_id = json.loads(response.data).get('workflow_object_id')

    assert workflow_object_id is not None

    obj = workflow_object_class.get(workflow_object_id)

    expected = {
        '_collections': ['Authors'],
        'control_number': 123,
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        'name': {
            'preferred_name': 'Harun Urhan',
            'value': 'Harun'
        },
        'status': 'active',
        'acquisition_source': {
            'datetime': obj.data['acquisition_source']['datetime'],
            'email': 'johndoe@inspirehep.net',
            'internal_uid': 5,
            'method': 'submitter',
            'submission_number': str(obj.id)
        }
    }

    assert expected == obj.data

    assert obj.extra_data['is-update'] is True
