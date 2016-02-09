# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for DoJSON utilities."""

from inspirehep.utils.date import create_valid_date, create_earliest_date


def test_create_valid_date():
    """Test date validator used in dojson conversions."""
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
    """Test the date validator that excepts list."""
    assert create_earliest_date([1877, '2002-01-05']) == '1877'
    assert create_earliest_date(['1877-02-03', '1877']) == '1877-02-03'
