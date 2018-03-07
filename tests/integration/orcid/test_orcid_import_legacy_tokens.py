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

from flask import current_app
from redis import StrictRedis
from pytest import fixture, mark
from mock import patch
from simplejson import dumps

from inspirehep.modules.orcid.tasks import (
    import_legacy_orcid_tokens,
    legacy_orcid_arrays,
    _find_user_matching,
    _register_user,
)
from invenio_oauthclient.models import User, RemoteToken, RemoteAccount, UserIdentity
from invenio_db import db


SAMPLE_USER = {
    'orcid': '0000-0002-1825-0097',
    'token': '3d25a708-dae9-48eb-b676-80a2bfb9d35c',
    'email': 'j.carberry@orcid.org',
    'name': 'Josiah Carberry',
}
SAMPLE_USER_2 = {
    'orcid': '0000-0001-1234-1234',
    'token': '12345678-9abc-def1-2345-6789abcdef12',
    'email': 'j.doe@orcid.org',
    'name': 'John Doe',
}
SAMPLE_USER_EDITED = {
    'orcid': '0000-0002-1825-0097',
    'token': '00000000-0000-0000-0000-000000000000',
    'email': 'j.carberry@orcid.org',
    'name': 'Josiah Carberry',
}


def record_dict_to_array(user_record):
    """Convert user record to an array, like ones received through redis."""
    key_ordering = ['orcid', 'token', 'email', 'name']
    return list(user_record[key] for key in key_ordering)


def push_to_redis(user_record):
    """Push a user record to redis."""
    user_record_json = dumps(record_dict_to_array(user_record))
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.lpush('legacy_orcid_tokens', user_record_json)


def assert_db_has_n_legacy_records(n, record):
    assert n == User.query.filter_by(email=record['email']).count()
    assert n == RemoteAccount.query.join(User).join(UserIdentity).filter(UserIdentity.id == record['orcid']).count()
    assert n == RemoteToken.query.filter_by(access_token=record['token']).count()
    assert n == UserIdentity.query.filter_by(id=record['orcid']).count()


def cleanup_record(record):
    RemoteToken.query.filter_by(access_token=record['token']).delete()
    user_id = db.session.query(UserIdentity.id_user).filter(UserIdentity.id == record['orcid']).subquery()
    RemoteAccount.query.filter(RemoteAccount.user_id.in_(user_id)).delete(synchronize_session='fetch')
    UserIdentity.query.filter_by(id=record['orcid']).delete()
    User.query.filter_by(email=record['email']).delete()


@fixture(scope='function')
def teardown_sample_user(app):
    yield

    cleanup_record(SAMPLE_USER)
    assert_db_has_n_legacy_records(0, SAMPLE_USER)


@fixture(scope='function')
def teardown_sample_user_2(app):
    yield

    cleanup_record(SAMPLE_USER_2)
    assert_db_has_n_legacy_records(0, SAMPLE_USER_2)


@fixture(scope='function')
def teardown_sample_user_edited(app):
    yield

    cleanup_record(SAMPLE_USER_EDITED)
    assert_db_has_n_legacy_records(0, SAMPLE_USER_EDITED)


@fixture(scope='function')
def redis_setup(app):
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)

    yield r

    r.delete('legacy_orcid_tokens')


@fixture(scope='function')
def app_with_config(app):
    config = {
        'ORCID_APP_CREDENTIALS': {
            'consumer_key': '0000-0000-0000-0000'
        }
    }

    with patch.dict(current_app.config, config):
        yield app


@fixture(scope='function')
def app_without_config(app):
    config = {
        'ORCID_APP_CREDENTIALS': {
            'consumer_key': None
        }
    }

    with patch.dict(current_app.config, config):
        yield app


def test_legacy_orcid_arrays(app, redis_setup):
    """Test the generator functionality."""
    push_to_redis(SAMPLE_USER_2)
    push_to_redis(SAMPLE_USER)

    # Check initial state of queue
    assert redis_setup.llen('legacy_orcid_tokens') == 2

    # Take all the records from the queue
    json_list = list(legacy_orcid_arrays())

    # Check if results are expected, and that redis is empty
    assert json_list == [record_dict_to_array(x) for x in [SAMPLE_USER, SAMPLE_USER_2]]
    assert redis_setup.llen('legacy_orcid_tokens') == 0


def test_import_multiple_orcid_tokens_no_user_exists(
        app_with_config, redis_setup, teardown_sample_user, teardown_sample_user_2):
    """Create two users and all the associate entries."""
    push_to_redis(SAMPLE_USER_2)
    push_to_redis(SAMPLE_USER)

    # Check initial state
    assert redis_setup.llen('legacy_orcid_tokens') == 2
    assert_db_has_n_legacy_records(0, SAMPLE_USER)
    assert_db_has_n_legacy_records(0, SAMPLE_USER_2)

    # Migrate
    import_legacy_orcid_tokens()

    # Check state after migration
    assert not redis_setup.llen('legacy_orcid_tokens')
    assert_db_has_n_legacy_records(1, SAMPLE_USER)
    assert_db_has_n_legacy_records(1, SAMPLE_USER_2)


def test_import_multiple_orcid_tokens_no_configuration(
        app_without_config, redis_setup, teardown_sample_user, teardown_sample_user_2):
    """Attempt and fail to create new users when configuration missing."""
    push_to_redis(SAMPLE_USER_2)
    push_to_redis(SAMPLE_USER)

    # Check initial state
    assert redis_setup.llen('legacy_orcid_tokens') == 2
    assert_db_has_n_legacy_records(0, SAMPLE_USER)
    assert_db_has_n_legacy_records(0, SAMPLE_USER_2)

    # Migrate
    import_legacy_orcid_tokens()

    # Assert state unchanged after migration
    assert redis_setup.llen('legacy_orcid_tokens') == 2
    assert_db_has_n_legacy_records(0, SAMPLE_USER)
    assert_db_has_n_legacy_records(0, SAMPLE_USER_2)


def test_linked_user_with_token_exists(app_with_config, teardown_sample_user):
    """Ignore token, if already has one."""
    assert_db_has_n_legacy_records(0, SAMPLE_USER)

    # Register sample user
    _register_user(**SAMPLE_USER)

    # Check state after migration
    assert_db_has_n_legacy_records(1, SAMPLE_USER)

    # Register the same user with another token
    _register_user(**SAMPLE_USER_EDITED)

    # Assert token unchanged
    assert_db_has_n_legacy_records(1, SAMPLE_USER)
    assert 0 == RemoteToken.query.filter_by(token=SAMPLE_USER_EDITED).count()


def test_linked_user_without_token_exists(app_with_config, teardown_sample_user_edited):
    """Add a token to an existing user with an ORCID paired."""
    assert_db_has_n_legacy_records(0, SAMPLE_USER)

    # Register sample user
    _register_user(**SAMPLE_USER)

    # Check state after migration
    assert_db_has_n_legacy_records(1, SAMPLE_USER)

    # Remove token and remote account
    RemoteToken.query.filter_by(access_token=SAMPLE_USER['token']).delete()
    user_id = db.session.query(UserIdentity.id_user).filter(UserIdentity.id == SAMPLE_USER['orcid']).subquery()
    RemoteAccount.query.filter(RemoteAccount.user_id.in_(user_id)).delete(synchronize_session='fetch')

    # Register the same user with another token
    _register_user(**SAMPLE_USER_EDITED)

    # Assert new token
    assert_db_has_n_legacy_records(1, SAMPLE_USER_EDITED)


def test_unlinked_user_exists(app_with_config, teardown_sample_user):
    """Add a token to an existing user without a paired ORCID."""
    assert_db_has_n_legacy_records(0, SAMPLE_USER)

    # Register sample user
    user = User()
    user.email = SAMPLE_USER['email']
    with db.session.begin_nested():
        db.session.add(user)

    # Register the token
    _register_user(**SAMPLE_USER)

    # Assert new token
    assert_db_has_n_legacy_records(1, SAMPLE_USER)


@mark.parametrize(
    'orcid,email',
    [
        ('0000-0002-1825-0097', 'email.not@in.db'),
        ('9876-5432-0987-6543', 'j.carberry@orcid.org'),
        ('0000-0002-1825-0097', 'j.carberry@orcid.org'),
    ],
    ids=[
        'verify match on orcid',
        'verify match on email',
        'verify match on both',
    ]
)
def test_find_user_matching(app_with_config, teardown_sample_user, orcid, email):
    """Add a token to an existing user with an ORCID paired."""
    assert_db_has_n_legacy_records(0, SAMPLE_USER)

    # Register sample user
    _register_user(**SAMPLE_USER)

    # Check state after migration
    assert_db_has_n_legacy_records(1, SAMPLE_USER)

    # Remove token and remote account
    user_by_orcid = _find_user_matching(orcid, email)

    # Assert the user found is the one added
    assert user_by_orcid.email == SAMPLE_USER['email']
    assert User.query.filter_by(email=SAMPLE_USER['email']).count() == 1
