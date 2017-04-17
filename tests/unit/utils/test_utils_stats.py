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

"""Unit tests for the stats utils."""

from __future__ import absolute_import, division, print_function

import pytest

from inspirehep.utils.stats import calculate_h_index, calculate_i10_index


@pytest.fixture
def citations_with_none_values():
    return {
        '123311': None,
        '123113': 3,
        '3424': 5,
        '3423421': 7,
        '3242346': 8,
        '3426733': 12,
        '1231432': None
    }


def test_calculate_h_index():
    citations_with_h_index_5 = {
        '123311': 34,
        '123113': 3,
        '3424': 5,
        '3423421': 7,
        '3242346': 8,
        '3426733': 12,
        '1231432': 2
    }

    expected = 5
    result = calculate_h_index(citations_with_h_index_5)

    assert expected == result


def test_calculate_h_index_ignores_none_values(citations_with_none_values):
    expected = 4
    result = calculate_h_index(citations_with_none_values)

    assert expected == result


def test_calculate_i10_index():
    citations_with_i10_index_19 = {
        '1': 411,
        '2': 208,
        '3': 164,
        '4': 152,
        '5': 145,
        '6': 64,
        '7': 43,
        '8': 40,
        '9': 34,
        '10': 33,
        '11': 24,
        '12': 22,
        '13': 20,
        '14': 17,
        '15': 15,
        '16': 14,
        '17': 13,
        '18': 12,
        '19': 10,
        '20': 7
    }

    expected = 19
    result = calculate_i10_index(citations_with_i10_index_19)

    assert expected == result


def test_calculate_i10_index_ignores_none_values(citations_with_none_values):
    expected = 1
    result = calculate_i10_index(citations_with_none_values)

    assert expected == result
