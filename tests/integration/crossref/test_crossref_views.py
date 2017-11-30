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
import os

import pkg_resources
import pytest
import requests_mock
from flask_security.utils import hash_password

from invenio_accounts.models import SessionActivity, User
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db


@pytest.fixture(scope='module')
def users(app):
    """Create users needed in this test module."""
    scientist = User(
        email='scientist@inspirehep.net',
        password=hash_password('scientist'),
        active=True,
    )
    db.session.add(scientist)
    db.session.commit()

    yield

    User.query.filter_by(email='scientist@inspirehep.net').delete()
    db.session.commit()


@pytest.fixture(scope='function')
def log_in_as_scientist(users, app_client):
    """Ensure that we're logged in as an unprivileged user."""
    login_user_via_session(app_client, email='scientist@inspirehep.net')

    yield

    SessionActivity.query.delete()
    db.session.commit()


def test_crossref_search_handles_the_response_when_the_request_is_valid(log_in_as_scientist, app_client):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://api.crossref.org/works/10.1086/305772',
            text=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '10.1086_305772.json')),
        )

        response = app_client.get('/doi/search?doi=10.1086/305772')

        assert response.status_code == 200

        result = json.loads(response.data)

        assert result['query'] != {}
        assert result['source'] == 'crossref'
        assert result['status'] == 'success'


def test_crossref_search_returns_an_error_when_the_doi_cant_be_normalized(log_in_as_scientist, app_client):
    with requests_mock.Mocker():
        response = app_client.get('/doi/search?doi=cant-be-normalized')

        assert response.status_code == 400

        result = json.loads(response.data)

        assert result['query'] == {}
        assert result['source'] == 'inspire'
        assert result['status'] == 'badrequest'
