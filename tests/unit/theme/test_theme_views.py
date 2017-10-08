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

from inspirehep.modules.theme.views import (
    get_institution_experiments_datatables_rows,
    get_institution_papers_datatables_rows,
    postfeedback
)


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


@mock.patch('inspirehep.modules.theme.views.get_experiment_publications')
def test_get_institution_experiments_datatables_rows_handles_unicode_title(
        mocked_get_experiment_publications
):

    mocked_hit = mock.Mock()
    mocked_hit.control_number = 1
    mocked_hit.legacy_name = u'φοο_name'
    mocked_hit.collaboration = None

    mocked_get_experiment_publications.return_value = None

    expected_result = [
        [u"<a href='/experiments/1'>φοο_name</a>", None]
    ]

    assert get_institution_experiments_datatables_rows([mocked_hit]) == expected_result


@mock.patch('inspirehep.modules.theme.views.render_macro_from_template')
@mock.patch('inspirehep.modules.theme.views.get_title')
def test_get_institution_papers_datatables_rows_handles_unicode_title(
        get_title, render_mft):

    mocked_hit = mock.Mock()
    mocked_hit.control_number = 1

    mocked_publication_info = mock.Mock()
    mocked_publication_info.journal_title = 'foo'
    mocked_hit.publication_info = [mocked_publication_info]
    mocked_hit.citation_count = 1
    mocked_hit.earliest_date = '2017-04-10'

    get_title.return_value = u'φοο_title'
    render_mft.return_value = None

    expected_result = [
        ["<a href='/literature/1'>φοο_title</a>", None, 'foo', 1, '2017']
    ]

    assert get_institution_papers_datatables_rows([mocked_hit]) \
        == expected_result


@mock.patch('inspirehep.modules.theme.views.jsonify')
@mock.patch('inspirehep.modules.theme.views.send_email')
@mock.patch('inspirehep.modules.theme.views.request')
def test_postfeedback_handles_unicode_feedback(request, send_email,
                                               jsonify):
    request.form.get.return_value = u'φοο'
    sending_mock = mock.Mock()
    sending_mock.failed.return_value = False
    send_email.delay.return_value = sending_mock

    assert postfeedback()
