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

from inspirehep.modules.orcid.utils import _split_lists


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
