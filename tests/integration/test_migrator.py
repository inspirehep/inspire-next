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

import os
import pkg_resources
import zlib

import pytest
from flask import current_app
from redis import StrictRedis

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.migrator.models import InspireProdRecords
from inspirehep.modules.migrator.tasks.records import continuous_migration
from inspirehep.utils.record_getter import get_db_record


def _delete_record(pid_type, pid_value):
    get_db_record(pid_type, pid_value)._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, pid_value)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def push_to_redis(record_file):
    record = pkg_resources.resource_string(
        __name__, os.path.join('fixtures', record_file))

    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.rpush('legacy_records', zlib.compress(record))

    return record


def flush_redis():
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.delete('legacy_records')


@pytest.fixture(scope='function')
def record_1502656():
    record = push_to_redis('1502656.xml')

    yield record

    flush_redis()
    _delete_record('lit', 1502656)


@pytest.fixture(scope='function')
def record_1502655_and_1502656():
    record1 = push_to_redis('1502655.xml')
    record2 = push_to_redis('1502656.xml')

    yield record1, record2

    flush_redis()
    _delete_record('aut', 1502655)
    _delete_record('lit', 1502656)


@pytest.fixture(scope='function')
def record_1502656_and_update():
    record1 = push_to_redis('1502656.xml')
    record2 = push_to_redis('1502656_update.xml')

    yield record1, record2

    flush_redis()
    _delete_record('lit', 1502656)


def test_continuous_migration_handles_a_single_record(app, record_1502656):
    r = StrictRedis.from_url(current_app.config.get('CACHE_REDIS_URL'))

    assert r.lrange('legacy_records', 0, 0) != []

    continuous_migration()

    assert r.lrange('legacy_records', 0, 0) == []

    get_db_record('lit', 1502656)  # Does not raise.

    expected = record_1502656
    result = InspireProdRecords.query.get(1502656).marcxml

    assert expected == result



def test_continuous_migration_handles_multiple_records(app, record_1502655_and_1502656):
    r = StrictRedis.from_url(current_app.config.get('CACHE_REDIS_URL'))

    assert r.lrange('legacy_records', 0, 0) != []

    continuous_migration()

    assert r.lrange('legacy_records', 0, 0) == []

    get_db_record('aut', 1502655)  # Does not raise.

    expected = record_1502655_and_1502656[0]
    result = InspireProdRecords.query.get(1502655).marcxml

    assert expected == result

    get_db_record('lit', 1502656)  # Does not raise.

    expected = record_1502655_and_1502656[1]
    result = InspireProdRecords.query.get(1502656).marcxml

    assert expected == result



def test_continuous_migration_handles_record_updates(app, record_1502656_and_update):
    r = StrictRedis.from_url(current_app.config.get('CACHE_REDIS_URL'))

    assert r.lrange('legacy_records', 0, 0) != []

    continuous_migration()

    assert r.lrange('legacy_records', 0, 0) == []

    record = get_db_record('lit', 1502656)

    expected = 1
    result = len(record['authors'])

    assert expected == result

    expected = record_1502656_and_update[1]
    result = InspireProdRecords.query.get(1502656).marcxml

    assert expected == result
