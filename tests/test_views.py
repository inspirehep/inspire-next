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

import mock
import pytest


def test_postfeedback_provided_email(email_app):
    """Accepts feedback when providing en email."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(
            feedback='foo bar', replytoaddr='foo@bar.com'))

        assert response.status_code == 200


@mock.patch('inspirehep.modules.theme.views.current_user')
def test_postfeedback_logged_in_user(current_user, email_app):
    """Falls back to the email of the logged in user."""
    current_user.is_anonymous = False
    current_user.get.return_value = 'foo@bar.com'

    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback='foo bar'))

        assert response.status_code == 200


def test_postfeedback_anonymous_user(email_app):
    """Rejects feedback without an email."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback='foo bar'))

        assert response.status_code == 403


def test_postfeedback_empty_feedback(email_app):
    """Rejects empty feedback."""
    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(feedback=''))

        assert response.status_code == 400

@mock.patch('inspirehep.modules.theme.views.send_email.delay')
def test_postfeedback_send_email_failure(delay, email_app):
    """Informs the user when a server error occurred."""
    class FalseResult():
        def result(self):
            return False

    delay.return_value = FalseResult()

    with email_app.test_client() as client:
        response = client.post('/postfeedback', data=dict(
            feedback='foo bar', replytoaddr='foo@bar.com'))

        assert response.status_code == 500
