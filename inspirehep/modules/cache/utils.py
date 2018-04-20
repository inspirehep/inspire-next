# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""Cache."""

from __future__ import absolute_import, division, print_function

from contextlib import contextmanager

from flask import current_app as app
from redis import StrictRedis
from redis_lock import Lock


@contextmanager
def redis_locking_context(lock_name, expire=120, auto_renewal=True, blocking=False):
    """Locked Context Manager to perform operations on Redis."""
    if not lock_name:
        raise RedisLockError('Lock name not specified.')

    redis_url = app.config.get('CACHE_REDIS_URL')

    redis = StrictRedis.from_url(redis_url)
    lock = Lock(redis, lock_name, expire=expire, auto_renewal=auto_renewal)

    if lock.acquire(blocking=blocking):
        try:
            yield redis
        finally:
            lock.release()
    else:
        raise RedisLockError('Can not acquire Redis lock for %s', lock_name)


class RedisLockError(Exception):
    pass
