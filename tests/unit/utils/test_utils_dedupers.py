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

from __future__ import absolute_import, division, print_function

from inspirehep.utils.dedupers import dedupe_list, dedupe_list_of_dicts


def test_dedupe_list():
    list_with_duplicates = ['foo', 'bar', 'foo']

    expected = ['foo', 'bar']
    result = dedupe_list(list_with_duplicates)

    assert expected == result


def test_dedupe_list_of_dicts():
    list_of_dicts_with_duplicates = [
        {'a': 123, 'b': 1234},
        {'a': 3222, 'b': 1234},
        {'a': 123, 'b':1234},
    ]

    expected = [{'a': 123, 'b': 1234}, {'a': 3222, 'b': 1234}]
    result = dedupe_list_of_dicts(list_of_dicts_with_duplicates)

    assert expected == result
