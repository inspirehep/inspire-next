# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import json
import pytest

from invenio_accounts.testutils import login_user_via_session

from factories.db.inspire_migrator import TestLegacyRecordsMirror


@pytest.fixture(scope='function')
def isolated_log_in_as_cataloger(isolated_api_client):
    """Ensure that we're logged in as a privileged user."""
    login_user_via_session(isolated_api_client, email='cataloger@inspirehep.net')

    yield


def test_get_returns_the_records_in_descending_order_by_last_updated(
        isolated_api_client,
        isolated_log_in_as_cataloger,
):
    TestLegacyRecordsMirror.create_from_file(__name__, '1674997.xml', collection='HEP',
                                             _errors='Error: Least recent error.', valid=False)
    TestLegacyRecordsMirror.create_from_file(__name__, '1674989.xml', collection='HEP',
                                             _errors='Error: Middle error.', valid=False)
    TestLegacyRecordsMirror.create_from_file(__name__, '1674987.xml', collection='HEP',
                                             _errors='Error: Most recent error.', valid=False)

    response = isolated_api_client.get(
        '/migrator/errors',
        content_type='application/json',
    )

    expected_data = {
        'data': [
            {
                'recid': 1674987,
                'collection': 'HEP',
                'valid': False,
                'error': 'Error: Most recent error.'
            },
            {
                'recid': 1674989,
                'collection': 'HEP',
                'valid': False,
                'error': 'Error: Middle error.'
            },
            {
                'recid': 1674997,
                'collection': 'HEP',
                'valid': False,
                'error': 'Error: Least recent error.'
            },
        ]
    }

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert expected_data == response_data


def test_get_does_not_return_deleted_records(
        isolated_api_client,
        isolated_log_in_as_cataloger,
):
    TestLegacyRecordsMirror.create_from_file(__name__, '1674997.xml', collection='HEP',
                                             _errors='Error: Least recent error.', valid=False)
    TestLegacyRecordsMirror.create_from_file(__name__, '1674989.xml', collection='DELETED',
                                             _errors='Error: Middle error.', valid=False)
    TestLegacyRecordsMirror.create_from_file(__name__, '1674987.xml', collection='HEPNAMES',
                                             _errors='Error: Most recent error.', valid=False)

    response = isolated_api_client.get(
        '/migrator/errors',
        content_type='application/json',
    )

    expected_data = {
        'data': [
            {
                'recid': 1674987,
                'collection': 'HEPNAMES',
                'valid': False,
                'error': 'Error: Most recent error.'
            },
            {
                'recid': 1674997,
                'collection': 'HEP',
                'valid': False,
                'error': 'Error: Least recent error.'
            },
        ]
    }

    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert expected_data == response_data


def test_get_returns_empty_data_because_there_are_no_mirror_records_with_errors(
        isolated_api_client,
        isolated_log_in_as_cataloger,
):
    response = isolated_api_client.get(
        '/migrator/errors',
        content_type='application/json',
    )

    expected_data = {
        'data': [],
    }

    assert response.status_code == 200
    assert json.loads(response.data) == expected_data


def test_get_returns_permission_denied_if_not_logged_in_as_privileged_user(isolated_api_client):
    response = isolated_api_client.get(
        '/migrator/errors',
        content_type='application/json',
    )

    assert response.status_code == 403
