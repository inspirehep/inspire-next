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

import pytest

import mock
import os
import pkg_resources
import requests_mock

from sqlalchemy.orm.exc import NoResultFound

from inspirehep.modules.orcid.utils import (
    _split_lists,
)


def get_file(fixture_name):
    """Get contents of fixtures files"""
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


@pytest.mark.parametrize(
    'test_sequence,test_length,expected',
    [
        ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
        ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),
        (['a', 'b', 'c'], 1, [['a'], ['b'], ['c']]),
        (['just_one'], 1, [['just_one']]),
        (['just_one'], 10, [['just_one']]),
        ([], 10, []),
    ]
)
def test_split_lists(test_sequence, test_length, expected):
    result = _split_lists(test_sequence, test_length)
    assert expected == result


def mock_get_account_token_not_found(*args, **kwargs):
    raise NoResultFound


def mock_get_account_token_not_allowed(*args, **kwargs):
    token = mock.Mock()
    token.token.return_value = 'dummy_token', None
    account = mock.Mock()
    account.extra_data = {}
    return account, token


def mock_get_account_token_allowed(*args, **kwargs):
    token = mock.Mock()
    token.token.return_value = 'dummy_token', None
    account = mock.Mock()
    account.extra_data = {
        'allow_push': True
    }
    return account, token
