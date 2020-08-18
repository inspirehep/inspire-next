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

import os
import json
import shutil

import pytest

from mock import patch
from StringIO import StringIO

from invenio_accounts.models import SessionActivity
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db

from inspire_schemas.api import load_schema, validate


@pytest.fixture(scope='function')
def log_in_as_cataloger(api_client):
    """Ensure that we're logged in as a privileged user."""
    login_user_via_session(api_client, email='cataloger@inspirehep.net')

    yield

    SessionActivity.query.delete()
    db.session.commit()


@pytest.fixture(scope='function')
def log_in_as_scientist(api_client):
    """Ensure that we're logged in as an unprivileged user."""
    login_user_via_session(api_client, email='johndoe@inspirehep.net')

    yield

    SessionActivity.query.delete()
    db.session.commit()


@pytest.fixture(scope='function')
def clean_uploads_folder(app):
    yield
    uploads = app.config['RECORD_EDITOR_FILE_UPLOAD_FOLDER']
    shutil.rmtree(uploads)


def test_check_permission_success(log_in_as_cataloger, api_client):
    response = api_client.get('/editor/literature/1497201/permission')

    assert response.status_code == 200


def test_check_permission_returns_403_on_authentication_error(log_in_as_scientist, api_client):
    response = api_client.get('/editor/literature/1497201/permission')
    assert response.status_code == 403

    # Once cached, check again the permission
    response = api_client.get('/editor/literature/1497201/permission')
    assert response.status_code == 403


def test_editor_permission_is_cached(log_in_as_cataloger, api_client):
    cache_key = 'editor-permission-literature-1497201'
    with api_client.session_transaction() as sess:
        assert cache_key not in sess

    api_client.get('/editor/literature/1497201/permission')

    with api_client.session_transaction() as sess:
        assert sess[cache_key] is True

    response = api_client.get('/editor/literature/1497201/permission')

    assert response.status_code == 200


def test_authorlist_text(log_in_as_cataloger, api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    response = api_client.post(
        '/editor/authorlist/text',
        content_type='application/json',
        data=json.dumps({
            'text': (
                'F. Lastname1, F.M. Otherlastname1,2\n'
                '\n'
                '1 CERN\n'
                '2 Otheraffiliation'
            )
        })
    )

    assert response.status_code == 200

    expected = {
        'authors': [
            {
                'full_name': 'Lastname, F.',
                'raw_affiliations': [
                    {'value': 'CERN'},
                ],
            },
            {
                'full_name': 'Otherlastname, F.M.',
                'raw_affiliations': [
                    {'value': 'CERN'},
                    {'value': 'Otheraffiliation'},
                ],
            },
        ],
    }
    result = json.loads(response.data)

    assert validate(result['authors'], subschema) is None
    assert expected == result


def test_authorlist_text_exception(log_in_as_cataloger, api_client):
    response = api_client.post(
        '/editor/authorlist/text',
        content_type='application/json',
        data=json.dumps({
            'text': (
                'F. Lastname1, F.M. Otherlastname1,2\n'
                '\n'
                'CERN\n'
                '2 Otheraffiliation'
            )
        })
    )

    assert response.status_code == 500

    expected = {
        'message': "Cannot identify type of affiliations, found IDs: [u'C', u'2']",
        'status': 500
    }
    result = json.loads(response.data)

    assert expected == result


@patch('inspirehep.modules.editor.api.start_merger')
def test_manual_merge(mock_start_merger, log_in_as_cataloger, api_client):
    mock_start_merger.return_value = 100

    response = api_client.post(
        '/editor/manual_merge',
        content_type='application/json',
        data=json.dumps({
            'head_recid': 1000,
            'update_recid': 1001,
        })
    )

    assert response.status_code == 200

    expected = {'workflow_object_id': 100}
    result = json.loads(response.data)

    assert expected == result


def test_upload(app, log_in_as_cataloger, api_client, clean_uploads_folder):

    response = api_client.post(
        '/editor/upload',
        content_type='multipart/form-data',
        data={
            'file': (StringIO('my file contents'), 'attachment.pdf'),
        },
    )
    uploads_folder = app.config['RECORD_EDITOR_FILE_UPLOAD_FOLDER']
    result = json.loads(response.data)['path']
    expected = os.path.realpath(os.path.join(uploads_folder, 'attachment.pdf'))
    assert result == expected
    assert response.status_code == 200

    response = api_client.post(
        '/editor/upload',
        content_type='multipart/form-data',
        data={
            'file': (StringIO('my file contents'), 'attachment.pdf'),
        },
    )

    result = json.loads(response.data)['path']
    expected = os.path.realpath(
        os.path.join(uploads_folder, 'attachment.pdf_1'),
    )
    assert result == expected
    assert response.status_code == 200
