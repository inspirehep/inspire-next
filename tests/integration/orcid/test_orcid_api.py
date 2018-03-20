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

import os

import mock
import pkg_resources
import pytest
import vcr

from inspirehep.modules.orcid.api import push_record_with_orcid, get_author_putcodes, LOGGER


@pytest.fixture
def mock_orcid_api(app, mocked_internal_services):
    """Yield a MemberAPI and mock responses"""
    mocked_internal_services.put(
        'https://api.sandbox.orcid.org/v2.0/0000-0002-1825-0097/work/895497',
        text='200 OK'
    )
    mocked_internal_services.post(
        'https://api.sandbox.orcid.org/v2.0/0000-0002-1825-0097/work',
        headers={
            'Location': 'https://api.sandbox.orcid.org/v2.0/0000-0002-1825-0097/work/123456'
        },
    )
    return mocked_internal_services


def test_push_record_with_orcid(api_client, mock_orcid_api, mock_config):
    expected_put_code = '895497'
    expected_hash = '2995c60336bce71134ebdc12fc50b1ccaf0fd7cd'

    result_put_code, result_hash = push_record_with_orcid(
        recid='4328',
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        put_code='895497',
    )

    assert expected_put_code == result_put_code
    assert expected_hash == result_hash

    orcid_requests_made = [
        str(r) for r in mock_orcid_api.request_history if 'orcid' in r.url
    ]
    orcid_requests_expected = [
        'PUT https://api.sandbox.orcid.org/v2.0/0000-0002-1825-0097/work/895497'
    ]
    assert orcid_requests_made == orcid_requests_expected


def test_push_record_with_orcid_new(api_client, mock_orcid_api, mock_config):
    expected_put_code = '123456'
    expected_hash = '2995c60336bce71134ebdc12fc50b1ccaf0fd7cd'

    result_put_code, result_hash = push_record_with_orcid(
        recid='4328',
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        put_code=None,
    )

    assert expected_put_code == result_put_code
    assert expected_hash == result_hash

    orcid_requests_made = [
        str(r) for r in mock_orcid_api.request_history if 'orcid' in r.url
    ]
    orcid_requests_expected = [
        'POST https://api.sandbox.orcid.org/v2.0/0000-0002-1825-0097/work'
    ]
    assert orcid_requests_made == orcid_requests_expected


def get_file_contents(fixture_name):
    """Get contents of fixture files"""
    path = pkg_resources.resource_filename(
        __name__,
        os.path.join('fixtures', fixture_name)
    )
    with open(path, 'r') as fixture_fd:
        return fixture_fd.read()


@pytest.fixture
def mock_logger():
    class MockLogger(object):
        def error(self, message):
            self.message = message

    mock_logger = MockLogger()

    with mock.patch.object(LOGGER, 'error', mock_logger.error):
        yield mock_logger


def test_get_author_putcodes(app, mock_config, mock_logger):
    with vcr.use_cassette(
        pkg_resources.resource_filename(
            __name__,
            'fixtures/casette_get_putcodes.yaml'
        ),
        decode_compressed_response=True,
        filter_headers=['Authorization'],
        ignore_localhost=True,
        record_mode='none'
    ):
        pairs = get_author_putcodes('0000-0001-7102-4649', 'fake-token')

        assert pairs == [('4328', '912978')]
        assert '912977' in mock_logger.message
