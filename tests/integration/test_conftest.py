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
"""
The aim of this module is to test db isolation between single tests.
The `app` fixture does not provide db isolation between single tests: this
means that if a test adds an object to the db, the same obj is found
in the next tests.
The `isolated_app` fixture instead provides db isolation between single tests.
"""

from __future__ import absolute_import, division, print_function

import pytest

from flask_sqlalchemy import models_committed

from invenio_db import db
from invenio_oauthclient.models import User
from invenio_pidstore.models import PersistentIdentifier


@pytest.fixture(scope='module')
def pids_count(app):
    # Count the # PIDs currently loaded in the demosite.
    return PersistentIdentifier.query.count()


@pytest.fixture(scope='module')
def users_count(app):
    # Count the # User currently loaded in the demosite.
    return User.query.count()


# Test `app` fixture.


def test_app_fixture_lacks_db_isolation_step1(pids_count, app):
    assert PersistentIdentifier.query.count() == pids_count

    PersistentIdentifier.create(
        pid_type='type1',
        pid_value='value1',
    )
    # The #PIDs must have incremented.
    assert PersistentIdentifier.query.count() == pids_count + 1


def test_app_fixture_lacks_db_isolation_step2(pids_count, app):
    assert PersistentIdentifier.query.count() == pids_count + 1
    # Force the cleanup.
    PersistentIdentifier.get(
        pid_type='type1',
        pid_value='value1',
    ).delete()


# Test `isolated_app` fixture.


def test_isolated_app_db_isolation_step1(pids_count, isolated_app):
    assert PersistentIdentifier.query.count() == pids_count
    pid = PersistentIdentifier.create(pid_type='type1', pid_value='value1')
    assert PersistentIdentifier.query.get(pid.id)
    assert PersistentIdentifier.query.count() == pids_count + 1


def test_isolated_app_db_isolation_step2(pids_count, isolated_app):
    assert PersistentIdentifier.query.count() == pids_count
    pid = PersistentIdentifier.create(pid_type='type1', pid_value='value1')
    assert PersistentIdentifier.query.get(pid.id)
    assert PersistentIdentifier.query.count() == pids_count + 1


def test_isolated_app_session_commit(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    db.session.add(user)
    db.session.commit()

    user.email = 'foo@bar.com'
    db.session.add(user)
    db.session.commit()
    new_email = 'foo@bar2.com'
    user.email = new_email
    db.session.merge(user)
    db.session.commit()

    user = User.query.get(user.id)
    assert user.email == new_email
    assert User.query.count() == users_count + 1


def test_isolated_app_session_rollback(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    db.session.add(user)
    db.session.rollback()
    assert User.query.count() == users_count


def test_isolated_app_session_flush(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    db.session.add(user)
    db.session.flush()
    assert User.query.get(user.id)
    assert User.query.count() == users_count + 1


def test_isolated_app_session_close_after_commit(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    db.session.add(user)
    db.session.commit()
    id_ = user.id
    assert User.query.get(id_)
    # Closing the session within isolated_app fixture must trigger the rollback.
    db.session.close()
    assert User.query.count() == users_count


def test_isolated_app_session_close_before_commit(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    db.session.add(user)
    # Closing the session within isolated_app fixture must trigger the rollback.
    db.session.close()
    assert User.query.count() == users_count


def test_isolated_app_nested_transaction(users_count, isolated_app):
    assert User.query.count() == users_count
    user = User()
    with db.session.begin_nested():
        db.session.add(user)
    assert User.query.get(user.id)
    assert User.query.count() == users_count + 1


count = 0


def test_isolated_app_sqlalchemy_signals(isolated_app):
    @models_committed.connect
    def model_committed_receiver(sender, changes):
        for model_instance, change in changes:
            if isinstance(model_instance, User):
                global count
                count += 1

    user = User()
    db.session.add(user)
    db.session.commit()

    assert count == 1


def test_isolated_app_and_app_together(isolated_app, app):
    # When using `isolated_app` and `app` fixture together, the db isolation
    # feature should prevail.
    user = User()
    db.session.add(user)
    db.session.commit()
    id_ = user.id
    assert User.query.get(id_)
    # Closing the session within isolated_app fixture must trigger the rollback.
    db.session.close()
    assert not User.query.get(id_)
