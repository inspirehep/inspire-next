# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hep import hep
from inspirehep.dojson.utils import clean_record


def test_dois_from_0247_a_2():
    snippet = (
        '<record>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="a">10.1088/0264-9381/31/24/245004</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': '10.1088/0264-9381/31/24/245004',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['dois']


def test_dois_from_0247_a_2_and_0247_a_2_9():
    snippet = (
        '<record>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="9">bibmatch</subfield>'
        '    <subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
        '  </datafield>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'source': 'bibmatch',
            'value': '10.1088/1475-7516/2015/03/044',
        },
        {
            'value': '10.1088/1475-7516/2015/03/044',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['dois']


def test_dois_from_2472_a_2_and_247_a_2_9():
    snippet = (
        '<record>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="a">10.1103/PhysRevD.89.072002</subfield>'
        '  </datafield>'
        '  <datafield tag="024" ind1="7" ind2=" ">'
        '    <subfield code="2">DOI</subfield>'
        '    <subfield code="9">bibmatch</subfield>'
        '    <subfield code="a">10.1103/PhysRevD.91.019903</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': '10.1103/PhysRevD.89.072002',
        },
        {
            'source': 'bibmatch',
            'value': '10.1103/PhysRevD.91.019903',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['dois']
