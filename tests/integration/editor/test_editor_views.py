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

import json

import pytest
from flask_security.utils import encrypt_password
from mock import patch

from invenio_access.models import ActionUsers
from invenio_accounts.models import SessionActivity, User
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db


@pytest.fixture(scope='module')
def users():
    """Create users needed in this test module."""
    curator = User(
        email='curator@inspirehep.net',
        password=encrypt_password('curator'),
        active=True,
    )
    scientist = User(
        email='scientist@inspirehep.net',
        password=encrypt_password('scientist'),
        active=True,
    )
    db.session.add_all([curator, scientist])
    db.session.commit()

    curator_action = ActionUsers(
        action='editor_manage_tickets',
        argument=None,
        user_id=curator.id,
    )
    db.session.add(curator_action)
    db.session.commit()

    yield

    ActionUsers.query.filter_by(action='editor_manage_tickets').delete()
    User.query.filter_by(email='curator@inspirehep.net').delete()
    User.query.filter_by(email='scientist@inspirehep.net').delete()
    db.session.commit()


@pytest.fixture(scope='function')
def log_in_as_curator(users, api_client):
    """Ensure that we're logged in as a privileged user."""
    login_user_via_session(api_client, email='curator@inspirehep.net')

    yield

    SessionActivity.query.delete()
    db.session.commit()


@pytest.fixture(scope='function')
def log_in_as_scientist(users, api_client):
    """Ensure that we're logged in as an unprivileged user."""
    login_user_via_session(api_client, email='scientist@inspirehep.net')

    yield

    SessionActivity.query.delete()
    db.session.commit()


@patch('inspirehep.modules.editor.views.tickets')
def test_create_rt_ticket(mock_tickets, log_in_as_curator, api_client):
    mock_tickets.create_ticket.return_value = 1

    response = api_client.post(
        '/editor/rt/tickets/create',
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


@patch('inspirehep.modules.editor.views.tickets')
def test_create_rt_ticket_returns_500_on_error(mock_tickets, log_in_as_curator, api_client):
    mock_tickets.create_ticket.return_value = -1

    response = api_client.post(
        '/editor/rt/tickets/create',
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
    response = api_client.post('/editor/rt/tickets/create')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.views.tickets')
def test_resolve_rt_ticket(mock_tickets, log_in_as_curator, api_client):
    response = api_client.get('/editor/rt/tickets/4328/resolve')

    assert response.status_code == 200

    expected = {'success': True}
    result = json.loads(response.data)

    assert expected == result


def test_resolve_rt_ticket_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/rt/tickets/4328/resolve')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.views.tickets')
def test_get_tickets_for_record(mock_tickets, log_in_as_curator, api_client):
    response = api_client.get('/editor/rt/tickets/4328')

    assert response.status_code == 200


def test_get_tickets_for_record_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/rt/tickets/4328')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.views.tickets')
def test_get_rt_users(mock_tickets, log_in_as_curator, api_client):
    response = api_client.get('/editor/rt/users')

    assert response.status_code == 200


def test_get_rt_users_returns_403_on_authentication_error(api_client):
    response = api_client.get('/editor/rt/users')

    assert response.status_code == 403


@patch('inspirehep.modules.editor.views.tickets')
def test_get_rt_queues(mock_tickets, log_in_as_curator, api_client):
    response = api_client.get('/editor/rt/queues')

    assert response.status_code == 200


def test_get_rt_queues_returns_403_on_authentication_error(log_in_as_scientist, api_client):
    response = api_client.get('/editor/rt/queues')

    assert response.status_code == 403
