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
