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

"""ORCID push common fixtures."""

from __future__ import absolute_import, division, print_function

import mock
import pytest
import re
import requests
import requests_mock


@pytest.fixture()
def mock_config(api):
    with mock.patch.dict(api.config, {
        'ORCID_SANDBOX': True,
        'SERVER_NAME': 'http://labs.inspirehep.net',
    }):
        yield


@pytest.fixture
def mocked_internal_services(api_client):
    predownload = ['4328', '1375491', '524480', '701585']
    hep_responses = {}
    bibtex_responses = {}

    for recid in predownload:
        url = 'http://labs.inspirehep.net/api/literature/' + recid
        hep_resp = api_client.get('/literature/' + recid)
        bibtex_resp = api_client.get('/literature/' + recid, headers={
            'Accept': 'application/x-bibtex',
        })
        hep_responses[url] = hep_resp
        bibtex_responses[url] = bibtex_resp

    def api_matcher(request):
        resp = requests.Response()
        resp.status_code = 200
        if request.headers['Accept'] == 'application/json':
            resp._content = hep_responses[request.url].data
            return resp
        elif request.headers['Accept'] == 'application/x-bibtex':
            resp._content = bibtex_responses[request.url].data
            return resp

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer).*'),
            real_http=True,
        )
        requests_mocker.add_matcher(api_matcher)
        yield requests_mocker
