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

from inspirehep.modules.orcid.api import push_record_with_orcid, get_author_putcodes, LOGGER


@pytest.fixture
def mock_logger():
    class MockLogger(object):
        def error(self, message, *args):
            self.message = message % args

    mock_logger = MockLogger()

    with mock.patch.object(LOGGER, 'error', mock_logger.error):
        yield mock_logger


@pytest.mark.vcr()
def test_push_record_with_orcid_new(mock_config, vcr_cassette):
    expected_put_code = '920107'
    expected_hash = 'sha1:2995c60336bce71134ebdc12fc50b1ccaf0fd7cd'

    result_put_code, result_hash = push_record_with_orcid(
        recid='4328',
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        put_code=None,
        old_hash=None,
    )

    assert expected_put_code == result_put_code
    assert expected_hash == result_hash
    assert vcr_cassette.all_played


@pytest.mark.vcr()
def test_push_record_with_orcid_update(mock_config, vcr_cassette):
    expected_put_code = '920107'
    expected_hash = 'sha1:2995c60336bce71134ebdc12fc50b1ccaf0fd7cd'

    result_put_code, result_hash = push_record_with_orcid(
        recid='4328',
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        put_code='920107',
        old_hash=None,
    )

    assert expected_put_code == result_put_code
    assert expected_hash == result_hash
    assert vcr_cassette.all_played


def test_push_record_with_orcid_dont_push_if_no_change(mock_config):
    expected_put_code = '920107'
    expected_hash = 'sha1:2995c60336bce71134ebdc12fc50b1ccaf0fd7cd'

    result_put_code, result_hash = push_record_with_orcid(
        recid='4328',
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        put_code='920107',
        old_hash='sha1:2995c60336bce71134ebdc12fc50b1ccaf0fd7cd',
    )

    assert expected_put_code == result_put_code
    assert expected_hash == result_hash


@pytest.mark.vcr()
def test_get_author_putcodes(mock_config, mock_logger):
    pairs = get_author_putcodes('0000-0002-1825-0097', 'fake-token')

    assert pairs == [('4328', '912978')]
    assert '912977' in mock_logger.message
