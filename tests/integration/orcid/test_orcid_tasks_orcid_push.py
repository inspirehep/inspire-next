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

"""ORCID push tests."""

from __future__ import absolute_import, division, print_function

import mock
import pytest
import re

from redis import StrictRedis

from inspirehep.modules.orcid.api import recache_author_putcodes
from inspirehep.modules.orcid.tasks import orcid_push

from utils import override_config


CONFIG = dict(
    ORCID_SANDBOX=True,
    SERVER_NAME='https://labs.inspirehep.net',
    ORCID_APP_CREDENTIALS={
        'consumer_key': 'CHANGE_ME',
        'consumer_secret': 'CHANGE_ME'
    }
)


@pytest.fixture(scope='function')
def redis_setup(app):
    redis_url = app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)

    r.hmset('orcidcache:0000-0002-2152-2169:1375491', {'putcode': '1001'})
    r.hmset('orcidcache:0000-0002-2152-2169:524480', {'putcode': '1002'})
    r.hmset('orcidcache:0000-0002-2152-2169:701585', {'putcode': '1003'})

    yield r

    r.delete(*r.keys('orcidcache:*'))


@pytest.mark.vcr()
def test_push_to_orcid_same_with_cache(
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with override_config(**CONFIG):
        # Push as new
        orcid_push(orcid, rec_id, token)

        # Push the same record again
        orcid_push(orcid, rec_id, token)

    # Check that the update request didn't happen:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_update_with_cache(
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with override_config(**CONFIG):
        # Push as new
        orcid_push(orcid, rec_id, token)

        # Push the updated record
        orcid_push(orcid, rec_id, token)

    # Check that the update happened:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_update_no_cache(
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with override_config(**CONFIG):
        # Push update
        orcid_push(orcid, rec_id, token)

    # Check that the record was added:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_with_putcode_but_without_hash(
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with override_config(**CONFIG):
        # Fetch the putcodes, no hashes present yet
        recache_author_putcodes(orcid, token)

        # Push the record
        orcid_push(orcid, rec_id, token)

    # Check that the update request didn't happen:
    assert vcr_cassette.all_played


def test_feature_flag_orcid_push_whitelist_regex_none():
    FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '^$'

    compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
    assert not re.match(compiled, '0000-0002-7638-5686')
    assert not re.match(compiled, 'foo')
    # Be careful with the empty string.
    assert re.match(compiled, '')


def test_feature_flag_orcid_push_whitelist_regex_any():
    FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '.*'

    compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
    assert re.match(compiled, '0000-0002-7638-5686')
    assert re.match(compiled, 'foo')
    assert re.match(compiled, '')


def test_feature_flag_orcid_push_whitelist_regex_some():
    FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '^(0000-0002-7638-5686|0000-0002-7638-5687)$'

    compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
    assert re.match(compiled, '0000-0002-7638-5686')
    assert not re.match(compiled, '0000-0002-7638-5686XX')
    assert not re.match(compiled, '0000-0002-7638-56')
    assert not re.match(compiled, '0000-0002-7638-5689')
    assert not re.match(compiled, 'foo')
    assert not re.match(compiled, '')


def test_orcid_push_feature_flag_orcid_push_whitelist_regex_any(api):
    orcid = '0000-0002-7638-5686'
    regex = '.*'

    with mock.patch('inspirehep.modules.orcid.tasks.push_record_with_orcid') as mock_push_record_with_orcid, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_push_record_with_orcid.assert_called_once_with(oauth_token='token', orcid='0000-0002-7638-5686', recid='rec_id')


def test_orcid_push_feature_flag_orcid_push_whitelist_regex_none(api):
    orcid = '0000-0002-7638-5686'
    regex = '^$'

    with mock.patch('inspirehep.modules.orcid.tasks.push_record_with_orcid') as mock_push_record_with_orcid, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_push_record_with_orcid.assert_not_called()


def test_orcid_push_feature_flag_orcid_push_whitelist_regex_some(api):
    orcid = '0000-0002-7638-5686'
    regex = '^(0000-0002-7638-5686|0000-0002-7638-5687)$'

    with mock.patch('inspirehep.modules.orcid.tasks.push_record_with_orcid') as mock_push_record_with_orcid, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_push_record_with_orcid.assert_called_once_with(oauth_token='token', orcid='0000-0002-7638-5686', recid='rec_id')
