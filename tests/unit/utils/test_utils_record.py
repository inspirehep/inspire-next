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

from inspirehep.utils.record import get_title


def test_get_title():
    """Test get title utility."""
    double_title = {
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

    assert get_title(double_title) == "Parton distributions with LHC data"

    single_title = {
        "titles": [
            {
                "subtitle": "Harvest of Run 1",
                "title": "The Large Hadron Collider"
            }
        ]
    }

    assert get_title(single_title) == "The Large Hadron Collider"

    empty_title = {
        "titles": []
    }

    assert get_title(empty_title) == ""

    no_title_key = {
        "not_titles": []
    }

    assert get_title(no_title_key) == ""
