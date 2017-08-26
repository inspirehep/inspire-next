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


def test_arxiv_search_handles_the_response_when_the_request_is_valid(log_in_as_scientist, app_client):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/oai2',
            text=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1305.0014.xml')),
        )

        response = app_client.get('/arxiv/search?arxiv=1305.0014')

        assert response.status_code == 200

        expected = [
            'created',
            'doi',
            'title',
            'categories',
            'abstract',
            'authors',
            'license',
            'comments',
            'journal-ref',
        ]
        result = json.loads(response.data)

        for el in expected:
            assert el in result['query'].keys()
        assert result['source'] == 'arxiv'
        assert result['status'] == 'success'


def test_arxiv_search_handles_the_response_when_the_request_asks_for_a_malformed_id(log_in_as_scientist, app_client):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/oai2',
            text=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'is-malformed.xml')),
        )

        response = app_client.get('/arxiv/search?arxiv=is-malformed')

        assert response.status_code == 422

        result = json.loads(response.data)

        assert result['query'] == {}
        assert result['source'] == 'arxiv'
        assert result['status'] == 'malformed'


def test_arxiv_search_handles_the_response_when_the_request_asks_for_a_non_existing_record(log_in_as_scientist, app_client):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/oai2',
            text=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1305.9999.xml')),
        )

        response = app_client.get('/arxiv/search?arxiv=1305.9999')

        assert response.status_code == 404

        result = json.loads(response.data)

        assert result['query'] == {}
        assert result['source'] == 'arxiv'
        assert result['status'] == 'notfound'


def test_arxiv_search_handles_the_response_when_the_request_asks_for_a_version(log_in_as_scientist, app_client):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/oai2',
            text=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1305.0014v1.xml')),
        )

        response = app_client.get('/arxiv/search?arxiv=1305.0014v1')

        assert response.status_code == 415

        result = json.loads(response.data)

        assert result['query'] == {}
        assert result['source'] == 'arxiv'
        assert result['status'] == 'unsupported_versioning'
