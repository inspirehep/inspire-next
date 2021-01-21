# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2021 CERN.
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

from inspirehep.utils.errors import NoUsersFound
from inspirehep.utils.tickets import _get_from_cache, get_rt_user_by_email
from invenio_cache import current_cache
from mock import patch


def test_get_from_cache(app):
    def _test_generator():
        return [1, 2, 3]

    def _second_generator_which_should_not_run():
        raise AssertionError

    expected = [1, 2, 3]

    current_cache.delete('test')
    # Cache empty, so run generator and return data
    result = _get_from_cache('test', _test_generator)
    assert result == expected

    # Cache set so generator should not run
    result = _get_from_cache('test', _second_generator_which_should_not_run)
    assert result == expected


def test_get_from_cache_when_forced(app):
    def _test_generator():
        return [1, 2, 3]

    def _second_generator_which_should_run():
        return [4, 5, 6]

    expected = [1, 2, 3]

    current_cache.delete('test')
    # Cache empty, so run generator and return data
    result = _get_from_cache('test', _test_generator)
    assert result == expected

    # Forcing so generator should run again
    expected = [4, 5, 6]
    result = _get_from_cache('test', _second_generator_which_should_run, force_update=True)
    assert result == expected

    # Cache is set and not forcing so cached data should be returned
    result = _get_from_cache('test', _test_generator)
    assert result == expected


@patch("inspirehep.utils.tickets.query_rt")
def test_get_user_by_email(mock_query_rt, app):
    mock_query_rt.return_value = [
        u'id: user/1',
        u'Name: user1',
        u'EmailAddress: user1@cern.ch',
        u'',
        u'--',
        u'',
        u'id: user/2',
        u'Name: user2',
        u'EmailAddress: user2@cern.ch',
    ]

    expected_user = {"id": "user/2", "Name": "user2", "EmailAddress": "user2@cern.ch"}
    current_cache.delete('rt_users_with_emails')
    user = get_rt_user_by_email('user2@cern.ch')
    assert user == expected_user
    mock_query_rt.assert_called_once_with('user', fields="Name,EmailAddress")


@patch("inspirehep.utils.tickets.query_rt")
def test_get_user_by_email_forces_to_refresh_cache_when_nothing_found_first_time(mock_query_rt, app):
    mock_query_rt.side_effect = [
        [
            u'id: user/1',
            u'Name: user1',
            u'EmailAddress: user1@cern.ch',
        ],
        [
            u'id: user/1',
            u'Name: user1',
            u'EmailAddress: user1@cern.ch',
            u'',
            u'--',
            u'',
            u'id: user/2',
            u'Name: user2',
            u'EmailAddress: user2@cern.ch',
        ]
    ]

    expected_user = {"id": "user/2", "Name": "user2", "EmailAddress": "user2@cern.ch"}
    current_cache.delete('rt_users_with_emails')
    user = get_rt_user_by_email('user2@cern.ch')
    assert user == expected_user
    assert mock_query_rt.call_count == 2


@patch("inspirehep.utils.tickets.query_rt")
def test_get_user_by_email_forces_to_refresh_only_once_per_call(mock_query_rt, app):
    mock_query_rt.return_value = [
        u'id: user/1',
        u'Name: user1',
        u'EmailAddress: user1@cern.ch',

    ]
    current_cache.delete('rt_users_with_emails')
    with pytest.raises(NoUsersFound):
        get_rt_user_by_email('user2@cern.ch')

    assert mock_query_rt.call_count == 2
