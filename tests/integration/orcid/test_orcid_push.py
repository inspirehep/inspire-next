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

import pkg_resources
import pytest
import re
import requests_mock
import vcr

from redis import StrictRedis

from inspirehep.modules.orcid.tasks import push_orcid


@pytest.fixture(scope='function')
def redis_setup(api):
    redis_url = api.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)

    yield r

    r.delete('orcidputcodes:0000-0002-2169-2152:4328')


@pytest.fixture
def mock_allow_orcid(mocked_internal_services):
    mocked_internal_services.register_uri(
        requests_mock.ANY,
        re.compile('.*(orcid).*'),
        real_http=True,
    )
    yield


def test_push_to_orcid_new_update_with_cache(
    api,
    redis_setup,
    mock_allow_orcid,
    mock_config
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with vcr.use_cassette(
        pkg_resources.resource_filename(
            __name__,
            'fixtures/casette_push_with_cache.yaml'
        ),
        decode_compressed_response=True,
        filter_headers=['Authorization'],
        ignore_localhost=True,
        record_mode='none',
    ) as cassette:
        # Push as new
        push_orcid(orcid, rec_id, token)

        # Push update
        push_orcid(orcid, rec_id, token)

        # Check that all requests were made exactly once
        assert cassette.play_counts.values() == [1, 1, 1]


def test_push_to_orcid_update_no_cache(
    api,
    redis_setup,
    mock_allow_orcid,
    mock_config
):
    rec_id = 4328
    orcid = '0000-0002-2169-2152'
    token = 'fake-token'

    with vcr.use_cassette(
        pkg_resources.resource_filename(
            __name__,
            'fixtures/casette_push_no_cache.yaml'
        ),
        decode_compressed_response=True,
        filter_headers=['Authorization'],
        ignore_localhost=True,
        record_mode='none',
    ) as cassette:
        # Push update
        push_orcid(orcid, rec_id, token)

        # Check that all requests were made exactly once
        assert cassette.play_counts.values() == [1, 1, 1]
