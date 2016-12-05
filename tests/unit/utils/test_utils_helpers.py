# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from inspirehep.dojson.utils import force_force_list
from inspirehep.utils.helpers import get_recid_from_url


def test_force_force_list_returns_empty_list_on_none():
    expected = []
    result = force_force_list(None)

    assert expected == result


def test_force_force_list_wraps_strings_in_a_list():
    expected = ['foo']
    result = force_force_list('foo')

    assert expected == result


def test_force_force_list_converts_tuples_to_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_force_list(('foo', 'bar', 'baz'))

    assert expected == result


def test_get_recid_from_url_returns_false_on_none():
    assert get_recid_from_url(None) is False


def test_get_recid_from_url_returns_false_on_simple_strings():
    assert get_recid_from_url('a_string') is False


def test_get_recid_from_url_returns_false_on_ref_malformed():
    assert get_recid_from_url('http://bad_url') is False


def test_get_recid_from_url():
    assert get_recid_from_url('http://localhost:5000/api/literature/111') is 111
