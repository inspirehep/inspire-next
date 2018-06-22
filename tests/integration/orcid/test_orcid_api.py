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

"""ORCID util tests."""

from __future__ import absolute_import, division, print_function

import mock
import pytest

from factories.db.invenio_records import TestRecordMetadata
from utils import override_config

from inspirehep.modules.orcid.api import (
    LOGGER,
    distributed_lock,
    get_author_putcodes,
    push_record_with_orcid,
    recache_author_putcodes,
)
from inspirehep.modules.orcid.cache import OrcidCache
from inspirehep.modules.orcid.exceptions import PutcodeNotFoundInCacheException


CONFIG = dict(
    ORCID_SANDBOX=True,
    SERVER_NAME='https://labs.inspirehep.net',
    ORCID_APP_CREDENTIALS={
        'consumer_key': 'CHANGE_ME',
        'consumer_secret': 'CHANGE_ME'
    }
)


@pytest.mark.usefixtures('isolated_app')
class TestPushRecordWithOrcid(object):
    def setup(self):
        TestRecordMetadata.create_from_file(__name__, 'test_orcid_api_test_push_record_with_orcid.json')
        self.recid = '8201'
        self.putcode = '920107'
        self.hash_value = 'sha1:c6d51f84927dd82d16ee0aaccb64d13313a023b2'
        self.orcid = '0000-0002-1825-0097'
        self.oauth_token = 'fake-token'
        self.cache = OrcidCache(self.orcid)

    def teardown(self):
        """
        Cleanup the cache after each test (as atm there is no cache isolation).
        """
        key = self.cache._get_key(self.recid)
        self.cache.redis.delete(key)

    @pytest.mark.vcr()
    def test_new_record(self, vcr_cassette):
        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.recache_author_putcodes', wraps=recache_author_putcodes) as mock_recache_author_putcodes:
            putcode, hash_value = push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        assert putcode == self.putcode
        assert hash_value == self.hash_value
        mock_recache_author_putcodes.assert_not_called()
        assert vcr_cassette.all_played

    @pytest.mark.vcr()
    def test_new_record_alredy_existent_error(self, vcr_cassette):
        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.recache_author_putcodes', wraps=recache_author_putcodes) as mock_recache_author_putcodes:
            putcode, hash_value = push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        assert putcode == self.putcode
        assert hash_value == self.hash_value
        mock_recache_author_putcodes.assert_called_with(self.orcid, self.oauth_token)
        assert vcr_cassette.all_played

    @pytest.mark.vcr()
    def test_new_record_alredy_existent_error_and_putcode_not_found(self, vcr_cassette):
        with override_config(**CONFIG), \
                mock.patch.object(OrcidCache, 'read_record_data', return_value=(None, None)):

            with pytest.raises(PutcodeNotFoundInCacheException):
                push_record_with_orcid(
                    recid=self.recid,
                    orcid=self.orcid,
                    oauth_token=self.oauth_token,
                    putcode=None,
                    old_hash=None,
                )

    @pytest.mark.vcr()
    def test_updated_record_cache_hit(self, vcr_cassette):
        self.cache.write_record_data(self.recid, self.putcode, 'old_hash')

        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.recache_author_putcodes', wraps=recache_author_putcodes) as mock_recache_author_putcodes:
            putcode, hash_value = push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        assert putcode == self.putcode
        assert hash_value == self.hash_value
        mock_recache_author_putcodes.assert_not_called()
        assert vcr_cassette.all_played

    def test_updated_record_cache_hit_same_hash(self):
        self.cache.write_record_data(self.recid, self.putcode, self.hash_value)

        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.recache_author_putcodes', wraps=recache_author_putcodes) as mock_recache_author_putcodes:
            putcode, hash_value = push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        assert putcode == self.putcode
        assert hash_value == self.hash_value
        mock_recache_author_putcodes.assert_not_called()

    @pytest.mark.vcr()
    def test_distributed_lock_with_new_record(self):
        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.distributed_lock', wraps=distributed_lock) as mock_distributed_lock:
            push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        mock_distributed_lock.assert_called_with('orcid:0000-0002-1825-0097', blocking=True)

    @pytest.mark.vcr()
    def test_distributed_lock_with_updated_record(self):
        self.cache.write_record_data(self.recid, self.putcode, 'old_hash')

        with override_config(**CONFIG), \
                mock.patch('inspirehep.modules.orcid.api.distributed_lock', wraps=distributed_lock) as mock_distributed_lock:
            push_record_with_orcid(
                recid=self.recid,
                orcid=self.orcid,
                oauth_token=self.oauth_token,
                putcode=None,
                old_hash=None,
            )

        mock_distributed_lock.assert_called_with('orcid:0000-0002-1825-0097', blocking=True)


@pytest.mark.vcr()
def test_recache_author_putcodes():
    orcid = '0000-0002-1825-0097'
    oauth_token = 'fake-token'

    with override_config(**CONFIG):
        recache_author_putcodes(orcid, oauth_token)

    # Ensure the putcodes have been cached.
    cache = OrcidCache(orcid)
    putcode, _ = cache.read_record_data('4328')
    assert putcode == '912978'


@pytest.fixture
def mock_logger():
    class MockLogger(object):
        def error(self, message, *args):
            self.message = message % args

    mock_logger = MockLogger()

    with mock.patch.object(LOGGER, 'error', mock_logger.error):
        yield mock_logger


@pytest.mark.vcr()
def test_get_author_putcodes(mock_logger):
    with override_config(**CONFIG):
        pairs = get_author_putcodes('0000-0002-1825-0097', 'fake-token')

    assert pairs == [('4328', '912978')]
    assert '912977' in mock_logger.message
