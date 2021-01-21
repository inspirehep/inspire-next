# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

from inspirehep.utils.tickets import _strip_lines, query_rt, _get_all_of
from mock import patch


def test__strip_lines():
    multiline_string = """Line 1
    Line2 with space at the end """

    expected = "Line 1\n Line2 with space at the end"

    stripped = _strip_lines(multiline_string)

    assert expected == stripped


@patch('inspirehep.utils.tickets.rt_instance')
def test_query_rt_pass_all_arguments(mock_rt_instance):
    mock_rt_instance.url = "http://test_instance"

    query_rt("type", "body", "field1,field2")
    expected_url = "http://test_instance/search/type?query=body&fields=field1,field2"

    mock_rt_instance.session.get.assert_called_once_with(expected_url)


@patch('inspirehep.utils.tickets.rt_instance')
def test_query_rt_pass_only_type(mock_rt_instance):
    mock_rt_instance.url = "http://test_instance"

    query_rt("type")
    expected_url = "http://test_instance/search/type?query="

    mock_rt_instance.session.get.assert_called_once_with(expected_url)


@patch('inspirehep.utils.tickets.rt_instance')
def test_query_rt_pass_type_and_body(mock_rt_instance):
    mock_rt_instance.url = "http://test_instance"

    query_rt("type", "body")
    expected_url = "http://test_instance/search/type?query=body"

    mock_rt_instance.session.get.assert_called_once_with(expected_url)


@patch('inspirehep.utils.tickets.rt_instance')
def test_query_rt_pass_type_and_fields(mock_rt_instance):
    mock_rt_instance.url = "http://test_instance"

    query_rt("type", fields="field1,field2")
    expected_url = "http://test_instance/search/type?query=&fields=field1,field2"

    mock_rt_instance.session.get.assert_called_once_with(expected_url)


@patch('inspirehep.utils.tickets.rt_instance')
def test_query_rt_response(mock_rt_instance):
    mock_rt_instance.session.get.return_value.content.decode.return_value = "u'RT/4.2.16 200 Ok\n\nline_1\nline_2\nline_3\n\n\n"
    mock_rt_instance.url = "http://test_instance"

    expected_response = ["line_1", "line_2", "line_3"]
    response = query_rt("type", "body", "field1, field2")

    assert response == expected_response


@patch('inspirehep.utils.tickets.query_rt')
def test_get_all_of(mock_query_rt):
    mock_query_rt.return_value = [
        "1: user1",
        "2: user2",
    ]

    expected = [
        {'id': '1', 'name': 'user1'},
        {'id': '2', 'name': 'user2'}
    ]

    response = _get_all_of('user')

    assert response == expected
    mock_query_rt.called_once_with("user")
