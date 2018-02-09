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
import re
import requests
import requests_mock

from inspirehep.modules.orcid.utils import (
    push_record_with_orcid,
    _get_api_url_for_recid,
)


@pytest.fixture
def mocked_internal_services(api_client):
    hep_response = api_client.get('/literature/4328')
    bibtex_response = api_client.get('/literature/4328', headers={
        'Accept': 'application/x-bibtex',
    })

    def api_matcher(request):
        if request.url == 'http://localhost:5000/api/literature/4328':
            resp = requests.Response()
            resp.status_code = 200
            if request.headers['Accept'] == 'application/json':
                resp._content = hep_response.data
                return resp
            elif request.headers['Accept'] == 'application/x-bibtex':
                resp._content = bibtex_response.data
                return resp

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer).*'),
            real_http=True,
        )
        requests_mocker.add_matcher(api_matcher)
        yield requests_mocker


@pytest.fixture(scope='module')
def mock_config():
    """Fake ORCID_APP_CREDENTIALS"""
    with mock.patch(
        'inspirehep.modules.orcid.utils.load_config',
        return_value={
            'ORCID_APP_CREDENTIALS': {
                'consumer_key': '0000-0002-3874-0886',
                'consumer_secret': '01234567-89ab-cdef-0123-456789abcdef',
            },
            'SERVER_NAME': 'http://localhost:5000',
            'SEARCH_UI_SEARCH_API': '/api/literature/'
        }
    ):
        yield


@pytest.fixture
def mock_orcid_api(mock_config, mocked_internal_services):
    """Yield a MemberAPI and mock responses"""
    mocked_internal_services.put(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work/895497',
        text='200 OK'
    )
    mocked_internal_services.post(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work',
        headers={
            'Location': 'https://api.orcid.org/v2.0/0000-0002-1825-0097/'
                        'work/123456'
        },
    )
    return mocked_internal_services


def test_push_record_with_orcid(api_client, mock_orcid_api):
    sample_orcid = '0000-0002-1825-0097'
    expected_put_code = '895497'

    result_put_code = push_record_with_orcid(
        '4328', sample_orcid, 'fake-token', '895497'
    )

    assert expected_put_code == result_put_code


def test_push_record_with_orcid_new(api_client, mock_orcid_api):
    sample_orcid = '0000-0002-1825-0097'
    expected_put_code = '123456'

    result_put_code = push_record_with_orcid(
        '4328', sample_orcid, 'fake-token', None
    )

    assert expected_put_code == result_put_code


@pytest.mark.parametrize(
    'server_name,api_endpoint,recid,expected',
    [
        ('inspirehep.net', '/api/literature/', '123', 'http://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net', '/api/literature/', '123', 'http://inspirehep.net/api/literature/123'),
        ('https://inspirehep.net', '/api/literature/', '123', 'https://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net', 'api/literature', '123', 'http://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net/', '/api/literature', '123', 'http://inspirehep.net/api/literature/123'),
    ]
)
def test_get_api_url_for_recid(server_name, api_endpoint, recid, expected):
    result = _get_api_url_for_recid(server_name, api_endpoint, recid)
    assert expected == result
