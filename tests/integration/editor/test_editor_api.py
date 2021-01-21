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

import pkg_resources
import pytest
import requests_mock

from mock import patch
from StringIO import StringIO

from invenio_accounts.models import SessionActivity
from invenio_accounts.testutils import login_user_via_session
from invenio_cache import current_cache
from invenio_db import db

from inspire_schemas.api import load_schema, validate
from inspire_utils.record import get_value
from invenio_workflows import workflow_object_class

from inspirehep.utils.errors import NoUsersFound, EmptyResponseFromRT


@pytest.fixture(autouse=True)
def clear_cache(app):
    current_cache.clear()
    yield
    current_cache.clear()


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


@patch('inspirehep.modules.editor.api.tickets')
def test_create_rt_ticket(mock_tickets, log_in_as_cataloger, api_client):
    mock_tickets.create_ticket.return_value = 1

    response = api_client.post(
        '/editor/literature/1497201/rt/tickets/create',
        content_type='application/json',
        data=json.dumps({
            'description': 'description',
            'owner': 'owner',
            'queue': 'queue',
            'recid': '4328',
            'subject': 'subject',
        }),
    )

    assert response.status_code == 200


@patch('inspirehep.modules.editor.api.tickets')
def test_create_rt_ticket_only_needs_queue_and_recid(mock_tickets, log_in_as_cataloger, api_client):
    mock_tickets.create_ticket.return_value = 1

    response = api_client.post(
        '/editor/literature/1497201/rt/tickets/create',
        content_type='application/json',
        data=json.dumps({
            'queue': 'queue',
            'recid': '4328',
        }),
    )

    assert response.status_code == 200


@patch('inspirehep.modules.editor.api.tickets')
def test_create_rt_ticket_returns_500_on_error(mock_tickets, log_in_as_cataloger, api_client):
    mock_tickets.create_ticket.return_value = -1

    response = api_client.post(
        '/editor/literature/1497201/rt/tickets/create',
        content_type='application/json',
        data=json.dumps({
            'description': 'description',
            'owner': 'owner',
            'queue': 'queue',
            'recid': '4328',
            'subject': 'subject',
        }),
    )

    assert response.status_code == 500

    expected = {'success': False}
    result = json.loads(response.data)

    assert expected == result


def test_create_rt_ticket_returns_403_on_authentication_error(api_client):
    response = api_client.post('/editor/literature/1497201/rt/tickets/create')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.api.tickets')
def test_resolve_rt_ticket(mock_tickets, log_in_as_cataloger, api_client):
    response = api_client.get('/editor/literature/1497201/rt/tickets/4328/resolve')

    assert response.status_code == 200

    expected = {'success': True}
    result = json.loads(response.data)

    assert expected == result


def test_resolve_rt_ticket_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/literature/1497201/rt/tickets/4328/resolve')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.api.tickets')
def test_get_tickets_for_record(mock_tickets, log_in_as_cataloger, api_client):
    response = api_client.get('/editor/literature/1497201/rt/tickets')

    assert response.status_code == 200


def test_get_tickets_for_record_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/literature/1497201/rt/tickets')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.api.tickets')
def test_get_rt_users(mock_tickets, log_in_as_cataloger, api_client):
    response = api_client.get('/editor/rt/users')

    assert response.status_code == 200


@patch('inspirehep.utils.tickets.query_rt')
def test_rt_users_are_cached(mock_query_rt, log_in_as_cataloger, api_client):
    mock_query_rt.return_value = [
        "10309: atkinson",
        "1125438: bhecker",
        "460354: Catherine"
    ]
    current_cache.delete('rt_users')
    response = api_client.get('/editor/rt/users')
    assert current_cache.get('rt_users') == json.loads(response.data)


def test_get_rt_users_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/rt/users')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.api.tickets')
def test_get_rt_queues(mock_tickets, log_in_as_cataloger, api_client):
    response = api_client.get('/editor/rt/queues')

    assert response.status_code == 200


@patch('inspirehep.utils.tickets.query_rt')
def test_rt_queues_are_cached(mock_query_rt, log_in_as_cataloger, api_client):
    mock_query_rt.return_value = [
        "35: Admin",
        "63: Admin-curator",
        "60: Admin-Dev"
    ]
    current_cache.delete('rt_queues')
    response = api_client.get('/editor/rt/queues')
    assert current_cache.get('rt_queues') == json.loads(response.data)


def test_get_rt_queues_returns_403_on_authentication_error(log_in_as_scientist, api_client):
    response = api_client.get('/editor/rt/queues')

    assert response.status_code == 403


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


def test_refextract_text(log_in_as_cataloger, api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    response = api_client.post(
        '/editor/refextract/text',
        content_type='application/json',
        data=json.dumps({
            'text': (
                u'J. M. Maldacena. “The Large N Limit of Superconformal Field '
                u'Theories and Supergravity”. Adv. Theor. Math. Phys. 2 (1998), '
                u'pp. 231–252.'
            ),
        }),
    )
    references = json.loads(response.data)

    assert response.status_code == 200
    assert validate(references, subschema) is None
    assert get_value({'references': references}, 'references.reference.publication_info.journal_title')


def test_refextract_url(log_in_as_cataloger, api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'https://arxiv.org/pdf/1612.06414.pdf',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1612.06414.pdf')),
        )
        requests_mocker.register_uri(
            'GET', 'http://test-indexer:9200/records-hep/hep/_search?_source=control_number',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'es_response.json')),
        )

        response = api_client.post(
            '/editor/refextract/url',
            content_type='application/json',
            data=json.dumps({
                'url': 'https://arxiv.org/pdf/1612.06414.pdf',
            }),
        )
        references = json.loads(response.data)

    assert response.status_code == 200
    assert validate(references, subschema) is None
    assert get_value({'references': references}, 'references.reference.publication_info.journal_title')


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


def test_validate_workflow(api_client):
    login_user_via_session(api_client, email='admin@inspirehep.net')

    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "titles": [{"title": "BLABLABLABL"}],
        "document_type": ["article"],
        "_collections": ["Literature"],
    }

    workflow = workflow_object_class.create(
        data=record,
        data_type='hep'
    )
    workflow.save()
    db.session.commit()

    response = api_client.post(
        "/editor/validate_workflow",
        content_type="application/json",
        data=json.dumps({
            'id': workflow.id,
            'record': workflow.data,
        })
    )
    assert response.status_code == 200

    workflow.delete()
    db.session.commit()

    assert json.loads(response.data) == "success"


def test_validate_workflow_error(api_client):
    login_user_via_session(api_client, email='admin@inspirehep.net')

    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "titles": [{"title": "BLABLABLABL"}],
        "col": ["Literature"],
    }

    workflow = workflow_object_class.create(
        data=record,
        data_type="hep",
    )
    workflow.save()
    db.session.commit()

    response = api_client.post(
        "/editor/validate_workflow",
        content_type="application/json",
        data=json.dumps({
            'id': workflow.id,
            'record': workflow.data,
        })
    )
    assert response.status_code == 400

    workflow.delete()
    db.session.commit()

    assert json.loads(response.data) != "success"


@patch('inspirehep.utils.tickets.get_rt_user_by_email')
@patch('inspirehep.utils.tickets.resolve_ticket')
def test_close_ticket_sends_owner_to_rt(mock_resolve_ticket, mock_get_rt_user_by_email, api_client, log_in_as_cataloger):
    mock_get_rt_user_by_email.return_value = {"Name": "TEST_USER"}
    response = api_client.get('/editor/literature/1497201/rt/tickets/4328/resolve')

    assert response.status_code == 200
    mock_get_rt_user_by_email.assert_called_once_with(u'cataloger@inspirehep.net')
    mock_resolve_ticket.assert_called_once_with(u'4328', 'TEST_USER')


@patch('inspirehep.utils.tickets.get_rt_user_by_email')
@patch('inspirehep.utils.tickets.resolve_ticket')
def test_close_ticket_do_not_owner_to_rt_if_user_is_missing_in_rt(mock_resolve_ticket, mock_get_rt_user_by_email, api_client, log_in_as_cataloger):
    mock_get_rt_user_by_email.side_effect = NoUsersFound()
    response = api_client.get('/editor/literature/1497201/rt/tickets/4328/resolve')

    assert response.status_code == 200
    mock_get_rt_user_by_email.assert_called_once_with(u'cataloger@inspirehep.net')
    mock_resolve_ticket.assert_called_once_with(u'4328', None)


@patch('inspirehep.utils.tickets.get_rt_user_by_email')
@patch('inspirehep.utils.tickets.resolve_ticket')
def test_close_ticket_do_not_owner_to_rt_if_rt_do_not_return_users(
        mock_resolve_ticket,
        mock_get_rt_user_by_email,
        api_client,
        log_in_as_cataloger
):
    mock_get_rt_user_by_email.side_effect = EmptyResponseFromRT()
    response = api_client.get('/editor/literature/1497201/rt/tickets/4328/resolve')

    assert response.status_code == 200
    mock_get_rt_user_by_email.assert_called_once_with(u'cataloger@inspirehep.net')
    mock_resolve_ticket.assert_called_once_with(u'4328', None)
