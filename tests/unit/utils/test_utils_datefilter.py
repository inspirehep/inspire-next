# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Unit tests for the datefilter utility functions."""

from datetime import datetime

from inspirehep.utils.datefilter import date_older_than


def test_older_date():
    """date_older_than recognizes older dates."""
    some_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
    three_days_later = datetime.strptime("2015-01-04", "%Y-%m-%d")

    assert date_older_than(some_date, three_days_later, days=2)

def test_newer_date():
    """date_older_than recognizes newer dates."""
    some_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
    three_days_later = datetime.strptime("2015-01-04", "%Y-%m-%d")

    assert not date_older_than(some_date, three_days_later, days=6)
