# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspirehep.modules.refextract.tasks import extract_journal_info


class StubObj(object):
    def __init__(self, data):
        self.data = data
        self.extra_data = {}
        self.files = {}


class DummyEng(object):
    pass


def test_extract_journal_info():

    data = {
        'publication_info': [{'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)'}]
    }

    obj = StubObj(data)
    eng = DummyEng()

    extract_journal_info(obj, eng)

    pub_info = obj.data['publication_info'][0]

    assert '082102' == pub_info.get('artid')
    assert '55' == pub_info.get('journal_volume')
    assert 'J. Math. Phys.' == pub_info.get('journal_title')
    assert 2014 == pub_info.get('year')
