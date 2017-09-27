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
from flask import current_app, session

from flask_security import current_user

from invenio_accounts.testutils import (
    login_user_via_session,
    login_user_via_view,
)
from invenio_cache import current_cache

from inspirehep.utils.record_getter import get_db_record
from inspirehep.modules.records.permissions import load_user_collections
from inspirehep.modules.search.api import LiteratureSearch


@pytest.fixture(autouse=True)
def clear_cache(app):
    current_cache.clear()
    yield
    current_cache.clear()


def test_all_collections_are_cached(app, app_client):
    """Test that collection info gets cached."""

    # Remove collection cache key
    current_cache.delete('restricted_collections')

    app_client.get("/literature/1497201")

    # Check that cache key has been correctly filled
    assert current_cache.get('restricted_collections') == set(['HERMES Internal Notes'])


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 200),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='cataloger@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_public_detailed_read(app, app_client, user_info, status):
    """Test that a record can be read by everybody through web interface."""
    if user_info:
        # Login as user
        login_user_via_session(app_client, email=user_info['email'])

    assert app_client.get('/literature/1497201').status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 200),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='cataloger@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_public_api_read(app, app_client, user_info, status):
    """Test that a record can be read by everybody through the API."""
    if user_info:
        # Login as user
        login_user_via_session(app_client, email=user_info['email'])

    assert app_client.get('/literature/1497201').status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 302),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 403),
    # Logged in user with permissions assigned
    (dict(email='hermescataloger@inspirehep.net'), 200),
    (dict(email='cataloger@inspirehep.net'), 403),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_restricted_detailed_read(app, app_client, user_info, status):
    """Test permissions of restricted record accessing detailed view."""

    if user_info:
        # Login as user
        login_user_via_session(app_client, email=user_info['email'])

    assert app_client.get('/literature/1090628').status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 403),
    # Logged in user with permissions assigned
    (dict(email='hermescataloger@inspirehep.net'), 200),
    (dict(email='cataloger@inspirehep.net'), 403),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_restricted_api_read(app, api_client, user_info, status):
    """Test permissions of a restricted record through the API."""

    if user_info:
        login_user_via_session(api_client, email=user_info['email'])

    assert api_client.get('/literature/1090628').status_code == status


@pytest.mark.parametrize('user_info,total_count,es_filter', [
    # anonymous user
    (None, 23, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    (dict(email='johndoe@inspirehep.net', password='123456'), 23, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    (dict(email='cataloger@inspirehep.net', password='123456'), 23, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    (dict(email='hermescataloger@inspirehep.net', password='123456'), 23, [{'match': {'_collections': 'Literature'}}]),
    (dict(email='admin@inspirehep.net', password='123456'), 23, [{'match': {'_collections': 'Literature'}}]),
])
def test_inspire_search_filter_public_collection(app, app_client, user_info, total_count, es_filter):
    """Test default inspire search filter."""

    if user_info:
        login_user_via_view(app_client, email=user_info['email'],
                            password=user_info['password'],
                            login_url='/login/?local=1')

    # Doing a client request creates a request context that allows the
    # assert to correctly use the logged in user.
    app_client.get('/search')
    assert LiteratureSearch().to_dict()['query']['bool'][
        'filter'] == es_filter
    assert LiteratureSearch().count() == total_count


@pytest.mark.parametrize('user_info,total_count,es_filter', [
    # anonymous user
    (None, 0, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': u'HERMES Internal Notes'}}]}}]),
    (dict(email='johndoe@inspirehep.net', password='123456'), 0, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': u'HERMES Internal Notes'}}]}}]),
    (dict(email='cataloger@inspirehep.net', password='123456'), 0, [{'bool': {'must_not': [{'match': {'_collections': u'HERMES Internal Notes'}}], 'must': [{'match': {'_collections': u'HERMES Internal Notes'}}]}}]),
    (dict(email='hermescataloger@inspirehep.net', password='123456'), 1, [{'match': {'_collections': 'HERMES Internal Notes'}}]),
    (dict(email='admin@inspirehep.net', password='123456'), 1, [{'match': {'_collections': 'HERMES Internal Notes'}}]),
])
def test_inspire_search_filter_restricted_collection(app, app_client, user_info, total_count, es_filter):
    """Test default inspire search filter."""

    if user_info:
        login_user_via_view(app_client, email=user_info['email'],
                            password=user_info['password'],
                            login_url='/login/?local=1')

    # Doing a client request creates a request context that allows the
    # assert to correctly use the logged in user.
    app_client.get('/search?cc=HERMES Internal Notes')
    assert LiteratureSearch().to_dict()['query']['bool'][
        'filter'] == es_filter
    assert LiteratureSearch().count() == total_count


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 403),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='cataloger@inspirehep.net'), 200),
    # Hermes cataloger only allowed in its collection
    (dict(email='hermescataloger@inspirehep.net'), 403)
])
def test_record_api_update(app, api_client, user_info, status):
    """Test that a record can be updated only from admin
       and cataloger users through the API."""
    if user_info:
        login_user_via_session(api_client, email=user_info['email'])

    record = get_db_record('lit', 1497201)

    resp = api_client.put('/literature/1497201/db',
                          data=json.dumps(record),
                          content_type='application/json')
    assert resp.status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # Logged in user without permissions assigned
    (dict(email='johndoe@inspirehep.net'), 403),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='cataloger@inspirehep.net'), 200),
    # Hermes cataloger only allowed in its collection
    (dict(email='hermescataloger@inspirehep.net'), 200)
])
def test_record_api_update_restricted_record(app, api_client, user_info, status):
    """Test that a restricted record can be updated only by
       users with the right permission."""
    if user_info:
        login_user_via_session(api_client, email=user_info['email'])

    record = get_db_record('lit', 1090628)

    resp = api_client.put('/literature/1090628/db',
                          data=json.dumps(record),
                          content_type='application/json')
    assert resp.status_code == status


@pytest.mark.parametrize('user_info,collections', [
    (None, set()),
    (dict(email='cataloger@inspirehep.net'), set()),
    (dict(email='hermescataloger@inspirehep.net'), set([u'HERMES Internal Notes'])),
])
def test_load_user_collections(app_client, user_info, collections):
    if user_info:
        login_user_via_session(app_client, email=user_info['email'])

    with app_client.get('/'):
        assert 'restricted_collection' not in session
        load_user_collections(current_app, current_user)
        assert session['restricted_collections'] == collections
