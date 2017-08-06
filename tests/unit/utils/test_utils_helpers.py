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

from inspirehep.utils.helpers import force_list, maybe_int


def test_force_list_returns_empty_list_on_none():
    expected = []
    result = force_list(None)

    assert expected == result


def test_force_list_wraps_strings_in_a_list():
    expected = ['foo']
    result = force_list('foo')

    assert expected == result


def test_force_list_converts_tuples_to_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_list(('foo', 'bar', 'baz'))

    assert expected == result


def test_force_list_does_not_touch_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_list(['foo', 'bar', 'baz'])

    assert expected == result


def test_maybe_int_returns_int_if_possible():
    expected = 10
    result = maybe_int('10')

    assert expected == result


def test_maybe_int_returns_none_otherwise():
    assert maybe_int('216+337') is None
