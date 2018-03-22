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


@pytest.fixture()
def mock_config(app):
    patch = {
        'ORCID_SANDBOX': True,
        'SERVER_NAME': 'https://labs.inspirehep.net',
        'ORCID_APP_CREDENTIALS': {
            'consumer_key': 'CHANGE_ME',
            'consumer_secret': 'CHANGE_ME',
        }
    }
    with mock.patch.dict(app.config, patch):
        yield


@pytest.fixture
def vcr_config():
    return {
        'decode_compressed_response': True,
        'filter_headers': ['Authorization'],
        'ignore_hosts': ['test-indexer'],
        'record_mode': 'none',
    }


@pytest.fixture
def vcr(vcr):
    vcr.register_matcher(
        'accept',
        lambda r1, r2: r1.headers.get('Accept') == r2.headers.get('Accept'),
    )
    vcr.match_on = ['method', 'scheme', 'host', 'port', 'path', 'query', 'accept']
    return vcr
