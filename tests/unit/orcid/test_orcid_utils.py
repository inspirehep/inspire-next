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

from __future__ import absolute_import, division, print_function

import os
import pkg_resources
import pytest
import requests_mock

from mock import patch

from inspirehep.modules.orcid.utils import get_author_putcodes, CONFIG


def get_file(fixture_name):
    """Get contents of fixture files"""
    path = pkg_resources.resource_filename(
        __name__,
        os.path.join('fixtures', fixture_name)
    )
    with open(path, 'r') as file:
        return file.read()


@pytest.fixture
def mock_api():
    """Yield with fake responses"""
    with requests_mock.mock() as mock_api:
        mock_api.get(
            'https://api.orcid.org/v2.0/0000-0002-1825-0097/works',
            text=get_file('works.json'),
            headers={'Content-Type': 'application/orcid+json'},
        )
        mock_api.get(
            'https://api.orcid.org/v2.0/0000-0002-1825-0097/works/912982,912977',
            text=get_file('work_details.json'),
            headers={'Content-Type': 'application/orcid+json'}
        )
        yield


@pytest.fixture
def mock_config():
    """Yield with fake config"""
    mock_conf = {
        'ORCID_APP_CREDENTIALS': {
            'consumer_key': "0000-0002-3874-0886",
            'consumer_secret': "01234567-89ab-cdef-0123-456789abcdef",
        }
    }
    with patch.dict(CONFIG, mock_conf):
        yield


def test_get_author_putcodes(mock_api, mock_config):
    pairs, errors = get_author_putcodes('0000-0002-1825-0097', 'fake-token')

    assert pairs == [('4328', 912982)]
    assert errors == [912977]
