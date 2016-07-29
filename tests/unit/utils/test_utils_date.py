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

from inspirehep.utils.date import (
    create_datestruct,
    create_earliest_date,
    create_valid_date,
)


def test_create_valid_date():
    assert create_valid_date(1877) == '1877'
    assert create_valid_date('1877') == '1877'
    assert create_valid_date('1877-02') == '1877-02'
    assert create_valid_date('1877-02-03') == '1877-02-03'
    assert create_valid_date(1977) == '1977'
    assert create_valid_date('1977') == '1977'
    assert create_valid_date('1977-06-02') == '1977-06-02'
    assert create_valid_date('1977-06-022') == '1977-06'
    assert create_valid_date('1977-06-220') == '1977-06'


def test_create_earliest_date():
    assert create_earliest_date([1877, '2002-01-05']) == '1877'
    assert create_earliest_date(['1877-02-03', '1877']) == '1877-02-03'


def test_create_datestruct():
    assert create_datestruct('2002-01-05') == (2002, 1, 5)
    assert create_datestruct('1877-02') == (1877, 2)
    assert create_datestruct('1900') == (1900, )
