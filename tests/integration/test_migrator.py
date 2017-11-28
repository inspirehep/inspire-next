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

import os
import pkg_resources
import zlib

import pytest
from simplejson import dumps
from flask import current_app
from redis import StrictRedis

from inspirehep.modules.migrator.models import InspireProdRecords
from inspirehep.modules.migrator.tasks import (
    continuous_migration,
    sync_legacy_claims
)
from inspirehep.utils.record_getter import get_db_record

from utils import _delete_record


def push_to_redis(record_file):
    record = pkg_resources.resource_string(
        __name__, os.path.join('fixtures', record_file))

    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.rpush('legacy_records', zlib.compress(record))

    return record


def push_claim_to_redis(inspire_bai, aut_recid, lit_recid, signature, flag):
    claim = dumps([inspire_bai, aut_recid, lit_recid, signature, flag])
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.rpush('legacy_claims', claim)


def flush_redis(key):
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.delete(key)


@pytest.fixture(scope='function')
def record_1502656():
    record = push_to_redis('1502656.xml')

    yield record

    flush_redis('legacy_records')
    _delete_record('lit', 1502656)


@pytest.fixture(scope='function')
def record_1502655_and_1502656():
    record1 = push_to_redis('1502655.xml')
    record2 = push_to_redis('1502656.xml')

    yield record1, record2

    flush_redis('legacy_records')
    _delete_record('aut', 1502655)
    _delete_record('lit', 1502656)


@pytest.fixture(scope='function')
def record_1502656_and_update():
    record1 = push_to_redis('1502656.xml')
    record2 = push_to_redis('1502656_update.xml')

    yield record1, record2

    flush_redis('legacy_records')
    _delete_record('lit', 1502656)


@pytest.fixture(scope='function')
def record_1472986_unclaimed():
    record = get_db_record('lit', 1472986)
    revision_0 = len(record.revisions) - 1
    kenzie = record['authors'][0]
    del kenzie['ids']
    del kenzie['record']
    record.commit()
    yield
    record.revert(revision_0)
    flush_redis('legacy_claims')


@pytest.fixture(scope='function')
def record_1472986_claimed():
    record = get_db_record('lit', 1472986)
    revision_0 = len(record.revisions) - 1
    yield
    record.revert(revision_0)
    flush_redis('legacy_claims')


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


def test_legacy_claim_sync_unclaimed(app, record_1472986_unclaimed):
    """Test that the record is correctly claimed."""
    server = current_app.config['SERVER_NAME']
    if not server.startswith('http://'):
        server = 'http://{}'.format(server)
    ref_url = '{}/api/authors/1073117'.format(server)

    expected_ids = [{
        'value': 'M.Kenzie.1',
        'schema': 'INSPIRE BAI'
    }]
    expected_record = {
        '$ref': ref_url
    }

    push_claim_to_redis('M.Kenzie.1', 1073117, 1472986, 'Kenzie, Matthew', 2)

    aut_field = get_db_record('lit', 1472986)['authors'][0]
    assert 'ids' not in aut_field and 'record' not in aut_field

    sync_legacy_claims()

    aut_field = get_db_record('lit', 1472986)['authors'][0]
    assert aut_field['ids'] == expected_ids
    assert aut_field['record'] == expected_record


def test_legacy_claim_sync_claimed(app, record_1472986_claimed):
    """Test that if the record is already claimed, no changes are made."""
    push_claim_to_redis('M.Kenzie.1', 1073117, 1472986, 'Kenzie, Matthew', 2)

    record = get_db_record('lit', 1472986)
    revision_before = record.revision_id

    sync_legacy_claims()

    record = get_db_record('lit', 1472986)
    revision_after = record.revision_id

    assert revision_before == revision_after
