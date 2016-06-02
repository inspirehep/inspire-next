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

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.utils import strip_empty_values


def test_address_from_marcxml__111_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        }
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_multiple_marcxml__111_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '  </datafield>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Den Haag, Nederlands</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        },
        {
            'country_code': 'NL',
            'original_address': 'Den Haag, Nederlands'
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml__111_multiple_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '    <subfield code="c">Den Haag, Nederlands</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        },
        {
            'country_code': 'NL',
            'original_address': 'Den Haag, Nederlands'
        }
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']
