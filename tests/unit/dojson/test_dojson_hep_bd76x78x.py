# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_publication_info_from_773_c_p_w_double_v_double_y_0_1_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="p">IAU Symp.</subfield>'
        '  <subfield code="w">C08-06-09</subfield>'
        '  <subfield code="v">354</subfield>'
        '  <subfield code="y">2008</subfield>'
        '  <subfield code="v">254</subfield>'
        '  <subfield code="y">2009</subfield>'
        '  <subfield code="c">45</subfield>'
        '  <subfield code="1">1212883</subfield>'
        '  <subfield code="2">978924</subfield>'
        '  <subfield code="0">1408366</subfield>'
        '</datafield>'
    )  # record/820763/export/xme

    expected = [
        {
            'journal_title': 'IAU Symp.',
            'cnum': 'C08-06-09',
            'journal_volume': '354',
            'year': 2008,
            'artid': '45',
            'page_start': '45',
            'journal_record': {
                '$ref': 'http://localhost:5000/api/journals/1212883',
            },
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1408366',
            },
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/978924',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1408366,
            'c': [
                '45',
            ],
            'p': 'IAU Symp.',
            'v': '354',
            'w': 'C08-06-09',
            'y': 2008,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']
