# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from __future__ import absolute_import, division, print_function

import pytest
from flask_security.utils import encrypt_password

from invenio_access.models import ActionUsers
from invenio_accounts.models import SessionActivity, User
from invenio_accounts.testutils import login_user_via_session
from invenio_accounts.testutils import login_user_via_view
from invenio_collections.models import Collection
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_search import current_search_client as es

from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.search.api import LiteratureSearch
from inspirehep.modules.cache import current_cache


def _create_and_index_record(record):
    record = Record.create(record)
    inspire_recid_minter(record.id, record)
    # invenio-collections will populate _collections field in record upon
    # commit
    db.session.commit()

    # Record needs to be indexed since views fetch records from ES
    r = RecordIndexer()
    r.index(record)
    es.indices.refresh('records-hep')

    return record


@pytest.fixture(scope='function')
def sample_record(app):
    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": "123",
        "titles": [
            {
                "title": "Supersymmetric gauge field theory and string theory"
            }
        ],
        "collections": [
            {
                "primary": "HEP"
            },
            {
                "primary": "THESIS"
            }
        ]
    }

    record = _create_and_index_record(record)
    yield record

    pid = PersistentIdentifier.get('lit', '123')
    db.session.delete(pid)
    record.delete(force=True)
    es.delete(index='records-hep', doc_type='hep', id=pid.object_uuid)
    es.indices.refresh('records-hep')
    db.session.commit()


@pytest.fixture(scope='function')
def restricted_record(app):
    restricted_collection = Collection(
        name='Restricted Collection',
        dbquery='collections.primary:"Restricted Collection"',
    )
    another_restricted_collection = Collection(
        name='Another Restricted Collection',
        dbquery='collections.primary:"Another Restricted Collection"',
    )

    db.session.add_all([restricted_collection, another_restricted_collection])
    db.session.commit()

    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": "222",
        "titles": [
            {
                "title": "Supersymmetric gauge field theory and string theory"
            }
        ],
        "collections": [
            {
                "primary": "HEP"
            },
            {
                "primary": "THESIS"
            },
            {
                "primary": "Restricted Collection"
            },
            {
                "primary": "Another Restricted Collection"
            }
        ]
    }

    record = _create_and_index_record(record)
    yield record

    with app.app_context():
        # app context needed to avoid API app from being used after using
        # the api client. Needed for invenio-collections to be available.
        collection = Collection.query.filter_by(
            name='Restricted Collection'
        ).one()
        another_collection = Collection.query.filter_by(
            name='Another Restricted Collection'
        ).one()
        pid = PersistentIdentifier.get('lit', '222')
        es.delete(index='records-hep', doc_type='hep', id=pid.object_uuid)
        es.indices.refresh('records-hep')
        db.session.delete(collection)
        db.session.delete(another_collection)
        db.session.delete(pid)
        db.session.commit()


@pytest.fixture(scope='function')
def users(app):
    # Create test users
    encrypted_password = encrypt_password('123456')
    user = User(
        email='user@inspirehep.net',
        password=encrypted_password,
        active=True
    )
    user_partially_allowed = User(
        email='partially_allowed@inspirehep.net',
        password=encrypted_password,
        active=True,
    )
    user_allowed = User(
        email='allowed@inspirehep.net',
        password=encrypted_password,
        active=True,
    )

    db.session.add_all(
        [user, user_partially_allowed, user_allowed]
    )
    db.session.commit()

    # Create actions for the allowed user
    restricted_collection_action = ActionUsers(
        action='view-restricted-collection',
        argument='Restricted Collection',
        user_id=user_allowed.id
    )
    another_restricted_collection_action = ActionUsers(
        action='view-restricted-collection',
        argument='Another Restricted Collection',
        user_id=user_allowed.id
    )

    # Create actions for the partially allowed user
    partial_restricted_collection_action = ActionUsers(
        action='view-restricted-collection',
        argument='Restricted Collection',
        user_id=user_partially_allowed.id
    )

    db.session.add_all(
        [
            restricted_collection_action,
            another_restricted_collection_action,
            partial_restricted_collection_action
        ]
    )
    db.session.commit()

    yield

    SessionActivity.query.delete()
    ActionUsers.query.filter_by(action='view-restricted-collection').delete()
    User.query.filter_by(email='user@inspirehep.net').delete()
    User.query.filter_by(email='partially_allowed@inspirehep.net').delete()
    User.query.filter_by(email='allowed@inspirehep.net').delete()
    db.session.commit()


def test_all_collections_are_cached(app, users, sample_record):
    """Test that collection info gets cached."""
    with app.test_client() as client:
        # Remove collection cache key
        current_cache.delete('restricted_collections')

        client.get("/literature/123")

        # Check that cache key has been correctly filled
        assert current_cache.get('restricted_collections') == \
            set([u'Another Restricted Collection', u'Restricted Collection'])


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 200),
    # Logged in user without permissions assigned
    (dict(email='user@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='allowed@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_public_detailed_read(app, sample_record, users, user_info, status):
    """Test that a record can be read by everybody through web interface."""
    with app.test_client() as client:
        if user_info:
            # Login as user
            login_user_via_session(client, email=user_info['email'])

        assert client.get("/literature/123").status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 200),
    # Logged in user without permissions assigned
    (dict(email='user@inspirehep.net'), 200),
    # Logged in user with permissions assigned
    (dict(email='allowed@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_public_api_read(app, api_client, sample_record, users, user_info, status):
    """Test that a record can be read by everybody through the API."""
    if user_info:
        # Login as user
        login_user_via_session(api_client, email=user_info['email'])

    assert api_client.get("/literature/123").status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 302),
    # Logged in user without permissions assigned
    (dict(email='user@inspirehep.net'), 403),
    # Logged in user not allowed in all collections
    (dict(email='partially_allowed@inspirehep.net'), 403),
    # Logged in user with permissions assigned
    (dict(email='allowed@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_restricted_detailed_read(app, restricted_record, users, user_info, status):
    """Test permissions of restricted record accessing detailed view."""

    with app.test_client() as client:
        if user_info:
            # Login as user
            login_user_via_session(client, email=user_info['email'])

        assert client.get("/literature/222").status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # Logged in user without permissions assigned
    (dict(email='user@inspirehep.net'), 403),
    # Logged in user not allowed in all collections
    (dict(email='partially_allowed@inspirehep.net'), 403),
    # Logged in user with permissions assigned
    (dict(email='allowed@inspirehep.net'), 200),
    # admin user
    (dict(email='admin@inspirehep.net'), 200),
])
def test_record_restricted_api_read(app, api_client, restricted_record, users, user_info, status):
    """Test permissions of a restricted record through the API."""

    if user_info:
        login_user_via_session(api_client, email=user_info['email'])
    assert api_client.get("/literature/222").status_code == status


@pytest.mark.parametrize('user_info,total_count,es_filter', [
    # anonymous user
    (None, 426, [{'bool': {'must_not': [{'match': {'_collections': u'Another Restricted Collection'}}, {'match': {'_collections': u'Restricted Collection'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    # Logged in user without permissions assigned
    (dict(email='user@inspirehep.net', password='123456'), 426, [{'bool': {'must_not': [{'match': {'_collections': u'Another Restricted Collection'}}, {'match': {'_collections': u'Restricted Collection'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    # Logged in user not allowed in all collections
    (dict(email='partially_allowed@inspirehep.net', password='123456'), 426, [{'bool': {'must_not': [{'match': {'_collections': u'Another Restricted Collection'}}], 'must': [{'match': {'_collections': 'Literature'}}]}}]),
    # Logged in user with permissions assigned
    (dict(email='allowed@inspirehep.net', password='123456'), 427, [{'match': {'_collections': 'Literature'}}]),
    # admin user
    (dict(email='admin@inspirehep.net', password='123456'), 427, [{'match': {'_collections': 'Literature'}}]),
])
def test_inspire_search_filter(app, restricted_record, users, user_info, total_count, es_filter):
    """Test default inspire search filter."""

    with app.test_client() as client:
        if user_info:
            login_user_via_view(client, email=user_info['email'], password=user_info['password'], login_url='/login/?local=1')

        # Doing a client request creates a request context that allows the
        # assert to correctly use the logged in user.
        client.get('/search')
        assert LiteratureSearch().to_dict()['query']['bool']['filter'] == es_filter
        assert LiteratureSearch().count() == total_count
