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

from inspirehep.utils.normalizers import normalize_journal_title
from inspirehep.modules.literaturesuggest import normalizers


class MockObj:
    pass


def test_normalize_journal_title(app):
    journal_title = 'Physical Review'
    abbreviated_journal_title = 'Phys.Rev.'

    normalized_journal_title = normalize_journal_title(journal_title)

    assert abbreviated_journal_title == normalized_journal_title


def test_convert_to_journal():
    obj = MockObj()
    formdata = {
        'series_title': 'Physical Review',
        'journal_title': '',
        'type_of_doc': 'book'
    }

    expected = {'series_title': 'Physical Review',
                'journal_title': 'Phys.Rev.',
                'type_of_doc': 'book'}
    result = normalizers.normalize_journal_title(obj, formdata)
    assert expected == result


def test_find_book():
    obj = MockObj()
    formdata = {
        'book_title': 'The Large Hadron Collider',
        'parent_book': '',
        'type_of_doc': 'chapter'
    }

    expected = {'book_title': 'The Large Hadron Collider',
                'parent_book': "http://localhost:5000/api/literature/1373790",
                'type_of_doc': 'chapter'}
    result = normalizers.find_book_id(obj, formdata)
    assert expected == result
