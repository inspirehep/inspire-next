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

import inspirehep.modules.orcid.tasks as tasks
from inspirehep.modules.orcid.tasks import (
    attempt_push,
    orcid_push,
    recache_all_author_putcodes
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
    mock_config,
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    # Push as new
    orcid_push(orcid, rec_id, token)

    # Push the same record again
    orcid_push(orcid, rec_id, token)

    # Check that the update request didn't happen:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_update_with_cache(
    mock_config,
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    # Push as new
    orcid_push(orcid, rec_id, token)

    # Push the updated record
    orcid_push(orcid, rec_id, token)

    # Check that the update happened:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_update_no_cache(
    mock_config,
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    # Push update
    orcid_push(orcid, rec_id, token)

    # Check that the record was added:
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_to_orcid_with_putcode_but_without_hash(
    mock_config,
    vcr_cassette,
    redis_setup,
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    # Fetch the putcodes, no hashes present yet
    recache_all_author_putcodes(orcid, token)

    # Push the record
    orcid_push(orcid, rec_id, token)

    # Check that the update request didn't happen:
    assert vcr_cassette.all_played


@pytest.mark.parametrize(
    '_recid,_put_code',
    [
        (1375491, '1001'),
        (524480, '1002'),
        (701585, '1003'),
    ]
)
def test_push_to_orcid_verify_correct_being_pushed(
        redis_setup,
        mock_config,
        monkeypatch,
        _recid,
        _put_code,
):
    _orcid = '0000-0002-2152-2169'

    def _get_author_putcodes(orcid, oauth_token):
        return [
            (1375491, '1001'),
            (524480, '1002'),
            (701585, '1003'),
        ]

    def _push_record_with_orcid(recid, orcid, oauth_token, put_code=None, old_hash=None):
        assert recid == str(_recid)
        assert orcid == _orcid
        assert put_code == _put_code
        assert old_hash is None

        return put_code, 'new-hash'

    monkeypatch.setattr(tasks, 'get_author_putcodes', _get_author_putcodes)
    monkeypatch.setattr(tasks, 'push_record_with_orcid', _push_record_with_orcid)

    attempt_push(_orcid, _recid, 'fake-token')


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

    with mock.patch('inspirehep.modules.orcid.tasks.attempt_push', autospec=True) as mock_attempt_push, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_attempt_push.assert_called_once_with(orcid, mock.ANY, mock.ANY)


def test_orcid_push_feature_flag_orcid_push_whitelist_regex_none(api):
    orcid = '0000-0002-7638-5686'
    regex = '^$'

    with mock.patch('inspirehep.modules.orcid.tasks.attempt_push', autospec=True) as mock_attempt_push, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_attempt_push.assert_not_called()


def test_orcid_push_feature_flag_orcid_push_whitelist_regex_some(api):
    orcid = '0000-0002-7638-5686'
    regex = '^(0000-0002-7638-5686|0000-0002-7638-5687)$'

    with mock.patch('inspirehep.modules.orcid.tasks.attempt_push', autospec=True) as mock_attempt_push, \
            mock.patch.dict(
                'inspirehep.modules.orcid.tasks.current_app.config', {
                    'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX': regex,
                }):
        orcid_push(orcid, 'rec_id', 'token')

    mock_attempt_push.assert_called_once_with(orcid, mock.ANY, mock.ANY)
