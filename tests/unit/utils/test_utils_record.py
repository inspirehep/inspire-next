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

"""Tests for record-related utilities."""

import pytest

from inspirehep.utils.record import get_title, get_value


@pytest.fixture
def double_title():
    return {
        "titles": [
            {
                "source": "arXiv",
                "title": "Parton distributions with LHC data"
            },
            {
                "title": "Parton distributions with LHC data"
            }
        ]
    }


@pytest.fixture
def single_title():
    return {
        "titles": [
            {
                "subtitle": "Harvest of Run 1",
                "title": "The Large Hadron Collider"
            }
        ]
    }


@pytest.fixture
def empty_title():
    return {
        "titles": []
    }


def test_get_title(double_title, single_title, empty_title):
    """Test get title utility."""
    assert get_title(double_title) == "Parton distributions with LHC data"
    assert get_title(single_title) == "The Large Hadron Collider"
    assert get_title(empty_title) == ""

    no_title_key = {
        "not_titles": []
    }
    assert get_title(no_title_key) == ""


def test_get_value(double_title, single_title, empty_title):
    """Test get_value utility"""
    assert len(get_value(double_title, "titles.title")) == 2
    assert get_value(double_title, "titles.title[0]") == "Parton distributions with LHC data"
    assert get_value(single_title, "titles.title") == ["The Large Hadron Collider"]
    assert get_value(empty_title, "titles.title") == []
    assert get_value(empty_title, "foo", {}) == {}
