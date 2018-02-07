# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017-2018 CERN.
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

import mock
import pytest

from inspirehep.modules.cache.utils import redis_locking_context
from inspirehep.modules.cache.errors import RedisLockError


@mock.patch(
    'inspirehep.modules.cache.utils.load_config',
    return_value={'CACHE_REDIS_URL': 'redis://test-redis:6379/0'}
)
def test_redis_locking_context_write_string_in_redis(app):
    with redis_locking_context('my_lock') as redis:
        redis.set('key', 'value')
        assert redis.get('key') == 'value'


@mock.patch(
    'inspirehep.modules.cache.utils.load_config',
    return_value={'CACHE_REDIS_URL': 'redis://test-redis:6379/0'}
)
def test_redis_locking_context_write_integer(app):
    with redis_locking_context('my_lock') as redis:
        redis.set('key', 1)
        assert redis.get('key') == '1'


@mock.patch(
    'inspirehep.modules.cache.utils.load_config',
    return_value={'CACHE_REDIS_URL': 'redis://test-redis:6379/0'}
)
def test_redis_locking_context_with_no_lock_name_raises_error(app):
    with pytest.raises(RedisLockError):
        with redis_locking_context(None):
            pytest.fail()
