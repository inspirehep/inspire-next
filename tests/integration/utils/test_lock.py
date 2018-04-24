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

from threading import Thread, Event
from time import sleep

from redis import StrictRedis
from redis_lock import Lock

from inspirehep.utils.lock import (
    distributed_lock,
    DistributedLockError,
)


def test_distributed_lock_raises_if_locked(app):
    with distributed_lock('my_lock'):
        with pytest.raises(DistributedLockError):
            with distributed_lock('my_lock'):
                pass


def test_distributed_lock_locks(app):
    with distributed_lock('my_lock'):
        redis_url = app.config.get('CACHE_REDIS_URL')
        redis = StrictRedis.from_url(redis_url)
        lock = Lock(redis, 'my_lock', expire=60)
        lock_acquired = lock.acquire(blocking=False)

    assert not lock_acquired


def test_distributed_lock_blocks(app):
    def work(lock_acquired_event):
        with app.app_context(), distributed_lock('my_lock'):
            lock_acquired_event.set()
            sleep(2)

    lock_acquired_event = Event()

    locking_thread = Thread(target=work, args=(lock_acquired_event,))
    locking_thread.daemon = True
    locking_thread.start()

    lock_acquired_event.wait()
    with distributed_lock('my_lock', blocking=True):
        for _ in range(10):
            if locking_thread.is_alive():
                sleep(1)
            else:
                break
        assert not locking_thread.is_alive()


def test_distributed_lock_auto_renews_lock(app):
    def work(lock_maybe_expired_event):
        with app.app_context(), distributed_lock('my_lock', expire=2, auto_renewal=True):
            sleep(3)
            lock_maybe_expired_event.set()
            sleep(30)

    redis_url = app.config.get('CACHE_REDIS_URL')
    redis = StrictRedis.from_url(redis_url)
    lock = Lock(redis, 'my_lock', expire=60)

    lock_maybe_expired_event = Event()

    locking_thread = Thread(target=work, args=(lock_maybe_expired_event,))
    locking_thread.daemon = True
    locking_thread.start()

    lock_maybe_expired_event.wait()

    lock_still_acquired = not lock.acquire(blocking=False)
    assert lock_still_acquired
