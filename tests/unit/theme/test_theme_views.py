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

import mock

from mocks import MockUser


user_with_email = MockUser('user@example.com')
user_empty_email = MockUser('')


def test_postfeedback_provided_email(app_client):
    """Accepts feedback when providing en email."""
    response = app_client.post('/postfeedback', data=dict(
        feedback='foo bar', replytoaddr='foo@bar.com'))

    assert response.status_code == 200
    assert json.loads(response.data) == {'success': True}


@mock.patch('inspirehep.modules.theme.views.current_user', user_with_email)
def test_postfeedback_logged_in_user(app_client):
    """Falls back to the email of the logged in user."""
    response = app_client.post('/postfeedback', data=dict(feedback='foo bar'))

    assert response.status_code == 200
    assert json.loads(response.data) == {'success': True}


@mock.patch('inspirehep.modules.theme.views.current_user', user_empty_email)
def test_postfeedback_empty_email(app_client):
    """Rejects feedback from user with empty email."""
    response = app_client.post('/postfeedback', data=dict(feedback='foo bar'))

    assert response.status_code == 403
    assert json.loads(response.data) == {'success': False}


def test_postfeedback_anonymous_user(app_client):
    """Rejects feedback without an email."""
    response = app_client.post('/postfeedback', data=dict(feedback='foo bar'))

    assert response.status_code == 403
    assert json.loads(response.data) == {'success': False}


def test_postfeedback_empty_feedback(app_client):
    """Rejects empty feedback."""
    response = app_client.post('/postfeedback', data=dict(feedback=''))

    assert response.status_code == 400
    assert json.loads(response.data) == {'success': False}


@mock.patch('inspirehep.modules.theme.views.send_email.delay')
def test_postfeedback_send_email_failure(delay, app_client):
    """Informs the user when a server error occurred."""
    class FailedResult():
        def failed(self):
            return True

    delay.return_value = FailedResult()

    response = app_client.post('/postfeedback', data=dict(
        feedback='foo bar', replytoaddr='user@example.com'))

    assert response.status_code == 500
    assert json.loads(response.data) == {'success': False}


def test_page_not_found_renders_template_when_in_app(app_client):
    response = app_client.get('/does-not-exist')

    assert response.status_code == 404
    assert response.mimetype == 'text/html'


def test_page_not_Found_returns_json_when_in_api(api_client):
    response = api_client.get('/does-not-exist')

    assert response.status_code == 404
    assert response.mimetype == 'application/json'

    expected = {
        'code': 404,
        'message': 'Not Found',
    }
    result = json.loads(response.data)

    assert expected == result
