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
    result = journals.do(create_record(snippet))

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
    result = journals.do(create_record(snippet))

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
    result = journals.do(create_record(snippet))

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

    result = journals.do(create_record(snippet))

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
    result = journals.do(create_record(snippet))

    assert expected == result['issn']


def test_issn_from_022__a_b_electronic():
    snippet = (
        '<datafield tag="022" ind1=" " ind2=" ">'
        '  <subfield code="a">2469-9888</subfield>'
        '  <subfield code="b">electronic</subfield>'
        '</datafield>'
    )  # record/1415879

    expected = [
        {
            'comment': 'electronic',
            'medium': 'online',
            'value': '2469-9888',
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['issn']


def test_coden_from_030__a_2():
    snippet = (
        '<datafield tag="030" ind1=" " ind2=" ">'
        '  <subfield code="2">CODEN</subfield>'
        '  <subfield code="a">HERAS</subfield>'
        '</datafield>'
    )  # record/1211568

    expected = [
        'HERAS',
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['coden']


def test_coden_from_double_030__a_2():
    snippet = (
        '<record>'
        '  <datafield tag="030" ind1=" " ind2=" ">'
        '    <subfield code="2">CODEN</subfield>'
        '    <subfield code="a">00686</subfield>'
        '  </datafield>'
        '  <datafield tag="030" ind1=" " ind2=" ">'
        '    <subfield code="2">CODEN</subfield>'
        '    <subfield code="a">VLUFB</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        '00686',
        'VLUFB',
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['coden']


def test_publisher_from_643__b():
    snippet = (
        '<datafield tag="643" ind1=" " ind2=" ">'
        '  <subfield code="b">ANITA PUBLICATIONS, INDIA</subfield>'
        '</datafield>'
    )  # record/1211888

    expected = [
        'ANITA PUBLICATIONS, INDIA',
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['publisher']


def test_publisher_from_double_643__b():
    snippet = (
        '<record>'
        '  <datafield tag="643" ind1=" " ind2=" ">'
        '    <subfield code="b">Elsevier</subfield>'
        '  </datafield>'
        '  <datafield tag="643" ind1=" " ind2=" ">'
        '    <subfield code="b">Science Press</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1212635

    expected = [
        'Elsevier',
        'Science Press',
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['publisher']


def test_titles_from_marcxml_130_with_single_a():
    snippet = (
        '<record>'
        '  <datafield tag="130" ind1=" " ind2=" ">'
        '    <subfield code="a">Physical Review Special Topics - Accelerators and Beams</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'Physical Review Special Topics - Accelerators and Beams',
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['titles']


def test_titles_from_marcxml_130_with_a_and_b():
    snippet = (
        '<record>'
        '  <datafield tag="130" ind1=" " ind2=" ">'
        '    <subfield code="a">Humana Mente</subfield>'
        '    <subfield code="b">Journal of Philosophical Studies</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'Humana Mente',
            'subtitle': 'Journal of Philosophical Studies',
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['titles']


def test_short_titles_from_marcxml_711():
    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">Phys.Rev.ST Accel.Beams</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'Phys.Rev.ST Accel.Beams',
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['short_titles']


def test_title_variants_from_marcxml_730():
    snippet = (
        '<record>'
        '  <datafield tag="730" ind1=" " ind2=" ">'
        '    <subfield code="a">PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS'
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['title_variants']


def test_multiple_title_variants_from_marcxml_730():
    snippet = (
        '<record>'
        '  <datafield tag="730" ind1=" " ind2=" ">'
        '    <subfield code="a">PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS</subfield>'
        '  </datafield>'
        '  <datafield tag="730" ind1=" " ind2=" ">'
        '    <subfield code="a">PHYSICS REVIEW ST ACCEL BEAMS</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS',
        },
        {
            'title': 'PHYSICS REVIEW ST ACCEL BEAMS',
        },
    ]
    result = journals.do(create_record(snippet))

    assert expected == result['title_variants']
