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

import pkg_resources
import os
import zlib

import pytest

from redis import StrictRedis

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.migrator.tasks.records import continuous_migration
from inspirehep.modules.migrator.models import InspireProdRecords
from inspirehep.utils.record import get_title
from inspirehep.utils.record_getter import get_db_record


def _delete_record(pid_type, pid_value):
    get_db_record(pid_type, pid_value)._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, pid_value)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def push_to_redis(app, record_name):
    record = pkg_resources.resource_string(
        __name__, os.path.join('fixtures', record_name + '.xml'))
    redis_url = app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.rpush('legacy_records', zlib.compress(record))
    return record


def flush_redis(app):
    redis_url = app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.delete('legacy_records')


@pytest.fixture(scope='function')
def record_1502656_and_update(app):
    record1 = push_to_redis(app, "1502656")
    record2 = push_to_redis(app, "1502656_update")
    yield record1, record2
    flush_redis(app)
    _delete_record("lit", "1502656")


@pytest.fixture(scope='function')
def record_1502656(app):
    record = push_to_redis(app, "1502656")
    yield record
    flush_redis(app)
    _delete_record("lit", "1502656")


@pytest.fixture(scope='function')
def record_1502655_and_1502656(app):
    record1 = push_to_redis(app, "1502655")
    record2 = push_to_redis(app, "1502656")
    yield record1, record2
    flush_redis(app)
    _delete_record("aut", "1502655")
    _delete_record("lit", "1502656")


def test_continuous_migration_single_record(app, record_1502656):
    r = StrictRedis.from_url(app.config.get('CACHE_REDIS_URL'))
    assert r.lrange('legacy_records', 0, 0) != []
    continuous_migration()
    assert r.lrange('legacy_records', 0, 0) == []
    assert InspireProdRecords.query.get(1502656).marcxml == record_1502656
    assert get_title(get_db_record('lit', 1502656)) == \
        'Proceedings, 12th International Conference on Beauty, Charm, and Hyperons in Hadronic Interactions (BEACH 2016)'


def test_continuous_migration_different_records(app, record_1502655_and_1502656):
    r = StrictRedis.from_url(app.config.get('CACHE_REDIS_URL'))
    assert r.lrange('legacy_records', 0, 0) != []
    continuous_migration()
    assert r.lrange('legacy_records', 0, 0) == []
    assert InspireProdRecords.query.get(1502655).marcxml == record_1502655_and_1502656[0]
    assert InspireProdRecords.query.get(1502656).marcxml == record_1502655_and_1502656[1]
    assert get_db_record('aut', 1502655)
    assert get_db_record('lit', 1502656)


def test_continuous_migration_record_update(app, record_1502656_and_update):
    r = StrictRedis.from_url(app.config.get('CACHE_REDIS_URL'))
    assert r.lrange('legacy_records', 0, 0) != []
    continuous_migration()
    assert r.lrange('legacy_records', 0, 0) == []
    assert InspireProdRecords.query.get(1502656).marcxml == record_1502656_and_update[1]
    assert get_db_record('lit', 1502656)
