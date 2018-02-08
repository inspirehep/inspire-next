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

"""Test lock cache."""

from __future__ import absolute_import, division, print_function

import pytest

from redis import StrictRedis
from redis_lock import Lock

from inspirehep.modules.cache.utils import (
    redis_locking_context,
    RedisLockError,
)


@pytest.fixture
def lock_redis(app):
    redis_url = app.config.get('CACHE_REDIS_URL')
    redis = StrictRedis.from_url(redis_url)
    lock = Lock(redis, 'my_lock', expire=60)
    lock.acquire(blocking=False)

    yield

    lock.release()


def test_redis_locking_context_fail_if_locked(lock_redis, app):
    with pytest.raises(RedisLockError):
        with redis_locking_context('my_lock'):
            pass


def test_redis_locking_context_test_locks(app):
    with redis_locking_context('my_lock') as redis:
        lock = Lock(redis, 'my_lock', expire=60)
        lock_acquired = lock.acquire(blocking=False)

    assert not lock_acquired
