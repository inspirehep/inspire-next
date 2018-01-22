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

from invenio_pidstore.models import PersistentIdentifier
from invenio_db import db


# Test `app` fixture.

@pytest.fixture(scope='module')
def pids_count_in_app(app):
    # Count the #PIDs currently loaded in the demosite.
    return PersistentIdentifier.query.count()


def test_app_fixture_lacks_db_isolation_step1(pids_count_in_app):
    assert PersistentIdentifier.query.count() == pids_count_in_app

    PersistentIdentifier.create(
        pid_type='type1',
        pid_value='value1',
    )
    # The #PIDs must have incremented.
    assert PersistentIdentifier.query.count() == pids_count_in_app + 1


def test_app_fixture_lacks_db_isolation_step2(pids_count_in_app):
    assert PersistentIdentifier.query.count() == pids_count_in_app + 1
    # Force the cleanup.
    PersistentIdentifier.get(
        pid_type='type1',
        pid_value='value1',
    ).delete()


# Test `isolated_app` fixture.


def test_isolated_app_fixture_has_db_isolation_step1(pids_count_in_app, isolated_app):
    assert PersistentIdentifier.query.count() == pids_count_in_app

    PersistentIdentifier.create(
        pid_type='type1',
        pid_value='value1',
    )
    # The #PIDs must have incremented.
    assert PersistentIdentifier.query.count() == pids_count_in_app + 1


def test_isolated_app_fixture_has_db_isolation_step2(pids_count_in_app, isolated_app):
    # This proves that the step1 and the step2 are isolated.
    # The #PIDs must NOT have incremented.
    assert PersistentIdentifier.query.count() == pids_count_in_app


def test_isolated_app_fixture_commit(isolated_app):
    pids_count = PersistentIdentifier.query.count()

    PersistentIdentifier.create(
        pid_type='type1',
        pid_value='value1',
    )
    db.session.commit()
    assert PersistentIdentifier.query.count() == pids_count + 1


def test_isolated_app_fixture_rollback(isolated_app):
    pids_count = PersistentIdentifier.query.count()

    PersistentIdentifier.create(
        pid_type='type1',
        pid_value='value1',
    )
    db.session.rollback()
    assert PersistentIdentifier.query.count() == pids_count
