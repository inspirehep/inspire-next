# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import json
import mock


class MockUser(object):
    def __init__(self, email):
        self.email = email

    def get(self, key):
        if key == 'email':
            return self.email

    @property
    def is_anonymous(self):
        return False


user_with_email = MockUser('foo@bar.com')
user_empty_email = MockUser('')


def test_postfeedback_provided_email(email_app):
    """Accepts feedback when providing en email."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(
            feedback='foo bar', replytoaddr='foo@bar.com'))

        assert response.status_code == 200
        assert json.loads(response.data) == {'success': True}


@mock.patch('inspirehep.modules.theme.views.current_user', user_with_email)
def test_postfeedback_logged_in_user(email_app):
    """Falls back to the email of the logged in user."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback='foo bar'))

        assert response.status_code == 200
        assert json.loads(response.data) == {'success': True}


@mock.patch('inspirehep.modules.theme.views.current_user', user_empty_email)
def test_postfeedback_empty_email(email_app):
    """Rejects feedback from user with empty email."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback='foo bar'))

        assert response.status_code == 403
        assert json.loads(response.data) == {'success': False}


def test_postfeedback_anonymous_user(email_app):
    """Rejects feedback without an email."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback='foo bar'))

        assert response.status_code == 403
        assert json.loads(response.data) == {'success': False}


def test_postfeedback_empty_feedback(email_app):
    """Rejects empty feedback."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback=''))

        assert response.status_code == 400
        assert json.loads(response.data) == {'success': False}


@mock.patch('inspirehep.modules.theme.views.send_email.delay')
def test_postfeedback_send_email_failure(delay, email_app):
    """Informs the user when a server error occurred."""
    class FailedResult():
        def failed(self):
            return True

    delay.return_value = FailedResult()

    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(
            feedback='foo bar', replytoaddr='foo@bar.com'))

        assert response.status_code == 500
        assert json.loads(response.data) == {'success': False}
