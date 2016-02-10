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

from inspirehep.dojson.utils import (
    remove_duplicates_from_list,
    remove_duplicates_from_list_of_dicts
)


def test_remove_duplicates_from_list_preserving_order():
    """Remove duplicates from a list preserving the order."""
    list_with_duplicates = ['foo', 'bar', 'foo']

    expected = ['foo', 'bar']
    result = remove_duplicates_from_list(list_with_duplicates)

    assert expected == result

def test_remove_duplicates_from_list_of_dicts_preserving_order():
    """Remove duplicates from a list of dictionaries preserving the order."""
    list_of_dicts_with_duplicates = [
        {'a': 123, 'b': 1234},
        {'a': 3222, 'b': 1234},
        {'a': 123, 'b': 1234}
    ]

    expected = [{'a': 123, 'b': 1234}, {'a': 3222, 'b': 1234}]
    result = remove_duplicates_from_list_of_dicts(list_of_dicts_with_duplicates)

    assert expected == result
