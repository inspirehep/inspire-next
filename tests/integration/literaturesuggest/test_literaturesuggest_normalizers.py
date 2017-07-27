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

from __future__ import absolute_import, division, print_function

from inspirehep.modules.literaturesuggest.normalizers import (
    find_book_id,
    normalize_journal_title,
)


class MockObj(object):
    pass


def test_find_book_id(app):
    obj = MockObj()
    formdata = {
        'book_title': 'The Large Hadron Collider',
        'parent_book': '',
        'type_of_doc': 'chapter',
    }

    expected = {
        'book_title': 'The Large Hadron Collider',
        'parent_book': 'http://localhost:5000/api/literature/1373790',
        'type_of_doc': 'chapter',
    }
    result = find_book_id(obj, formdata)

    assert expected == result


def test_normalize_to_journal_title_converts_from_series_title(app):
    obj = MockObj()
    formdata = {
        'journal_title': '',
        'series_title': 'Physical Review',
        'type_of_doc': 'book',
    }

    expected = {
        'journal_title': 'Phys.Rev.',
        'series_title': 'Physical Review',
        'type_of_doc': 'book',
    }
    result = normalize_journal_title(obj, formdata)

    assert expected == result
