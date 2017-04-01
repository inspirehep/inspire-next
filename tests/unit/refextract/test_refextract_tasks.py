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

from inspirehep.modules.refextract.tasks import extract_journal_info


def test_extract_journal_info(dummy_eng_cls, stub_obj_cls):
    obj = stub_obj_cls(
        {
            'publication_info': [
                {'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)'},
            ],
        },
        {}
    )
    eng = dummy_eng_cls()

    assert extract_journal_info(obj, eng) is None
    assert obj.data['publication_info'] == [
        {
            'artid': '082102',
            'journal_title': 'J. Math. Phys.',
            'journal_volume': '55',
            'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)',
            'year': 2014,
        }
    ]
