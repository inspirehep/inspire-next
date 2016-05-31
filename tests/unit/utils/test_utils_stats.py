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

"""Tests the stats module."""

import pytest

from inspirehep.utils.stats import Stats


@pytest.fixture
def citations_h5():
    return {
        "123311": 34,
        "123113": 3,
        "3424": 5,
        "3423421": 7,
        "3242346": 8,
        "3426733": 12,
        "1231432": 2
    }


@pytest.fixture
def citations_none():
    return {
        "123311": None,
        "123113": 3,
        "3424": 5,
        "3423421": 7,
        "3242346": 8,
        "3426733": 12,
        "1231432": None
    }


@pytest.fixture
def citations_list():
    return [
        5, 4, 3, 6, 3, 2, 5, 7
    ]


@pytest.fixture
def citations_h15i1019():
    return {
        "1": 411,
        "2": 208,
        "3": 164,
        "4": 152,
        "5": 145,
        "6": 64,
        "7": 43,
        "8": 40,
        "9": 34,
        "10": 33,
        "11": 24,
        "12": 22,
        "13": 20,
        "14": 17,
        "15": 15,
        "16": 14,
        "17": 13,
        "18": 12,
        "19": 10,
        "20": 7
    }


def test_stats_hindex(citations_h5, citations_h15i1019):
    """Test h5 index calculation."""
    assert 5 == Stats.calculate_hindex(citations=citations_h5)
    assert 15 == Stats.calculate_hindex(citations=citations_h15i1019)


def test_stats_nones(citations_none):
    assert 4 == Stats.calculate_hindex(citations=citations_none)
    assert 1 == Stats.calculate_i10(citations=citations_none)


def test_stats_list_hindex(citations_list):
    try:
        assert 4 == Stats.calculate_hindex(citations=citations_list)
        assert 1 == Stats.calculate_i10(citations=citations_list)
        assert False
    except TypeError:
        assert True


def test_stats_list_i10(citations_list):
    try:
        assert 1 == Stats.calculate_i10(citations=citations_list)
        assert False
    except TypeError:
        assert True


def test_stats_i10(citations_h5, citations_h15i1019):
    """Test i10 index calculation."""
    assert 2 == Stats.calculate_i10(citations=citations_h5)
    assert 19 == Stats.calculate_i10(citations=citations_h15i1019)
