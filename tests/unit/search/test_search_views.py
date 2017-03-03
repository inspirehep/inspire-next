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

from inspirehep.modules.search.views import (
    default_sortoption, format_sortoptions, sorted_options
)


def test_sorted_options():
    sort_options = {
        'foo': {'title': 'foo', 'default_order': 'asc'},
        'bar': {'title': 'bar', 'default_order': 'desc', 'order': 1},
        'baz': {'title': 'baz', 'order': 2},
    }

    expected = [
        {'title': 'foo', 'value': 'foo'},
        {'title': 'bar', 'value': '-bar'},
        {'title': 'baz', 'value': 'baz'},
    ]
    result = sorted_options(sort_options)

    assert expected == result


def test_format_sortoptions():
    sort_options = {'foo': {'title': 'foo'}}

    expected = '{"options": [{"title": "foo", "value": "foo"}]}'
    result = format_sortoptions(sort_options)

    assert expected == result


def test_default_sortoption():
    sort_options = {'foo': {'title': 'foo'}}

    expected = 'foo'
    result = default_sortoption(sort_options)

    assert expected == result
