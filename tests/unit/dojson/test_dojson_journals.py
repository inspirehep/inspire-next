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

from inspirehep.dojson.journals import journals
from inspirehep.dojson.utils import strip_empty_values


def test_issn_from_marcxml_022_with_a():
    """Test simple ISSN without medium."""
    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">2213-1337</subfield>'
        '  </datafield> '
        '</record>'
    )

    expected = [
        {
            'value': '2213-1337',
        },
    ]
    result = strip_empty_values(journals.do(create_record(snippet)))

    assert expected == result['issn']


def test_issn_from_marcxml_022_with_a_and_b():
    """Test ISSN with medium normalization."""
    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">2213-1337</subfield>'
        '    <subfield code="b">Print</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'medium': 'print',
            'value': '2213-1337',
        },
    ]
    result = strip_empty_values(journals.do(create_record(snippet)))

    assert expected == result['issn']


def test_issn_from_marcxml_022_with_a_and_b_and_comment():
    """Test ISSN with medium normalization.

    The original 'b' value will be stored in 'comment'.
    """
    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">2213-1337</subfield>'
        '    <subfield code="b">ebook</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'medium': 'online',
            'value': '2213-1337',
            'comment': 'ebook',
        },
    ]
    result = strip_empty_values(journals.do(create_record(snippet)))

    assert expected == result['issn']


def test_issn_from_marcxml_022_with_b_no_a():
    """Test ISSN in wrong subfield."""
    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="b">9780486632827</subfield>'
        '  </datafield> '
        '</record>'
    )

    result = strip_empty_values(journals.do(create_record(snippet)))

    assert 'issn' not in result


def test_multiple_issn_from_marcxml_022():
    """Test multiple ISSNs."""
    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">2349-2716</subfield>'
        '    <subfield code="b">Online</subfield>'
        '  </datafield>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">2349-6088</subfield>'
        '    <subfield code="b">Print</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'medium': 'online',
            'value': '2349-2716',
        },
        {
            'medium': 'print',
            'value': '2349-6088',
        },
    ]
    result = strip_empty_values(journals.do(create_record(snippet)))

    assert expected == result['issn']
