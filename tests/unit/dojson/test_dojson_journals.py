# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from inspire_schemas.utils import load_schema
from inspirehep.dojson.journals import journals
from inspirehep.dojson.utils import validate


def test_issn_from_022__a():
    schema = load_schema('journals')
    subschema = schema['properties']['issn']

    snippet = (
        '<datafield tag="022" ind1=" " ind2=" ">'
        '  <subfield code="a">2213-1337</subfield>'
        '</datafield> '
    )  # record/1445059

    expected = [
        {'value': '2213-1337'},
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['issn'], subschema) is None
    assert expected == result['issn']


def test_issn_from_022__a_b():
    schema = load_schema('journals')
    subschema = schema['properties']['issn']

    snippet = (
        '<datafield tag="022" ind1=" " ind2=" ">'
        '  <subfield code="a">1812-9471</subfield>'
        '  <subfield code="b">Print</subfield>'
        '</datafield>'
    )  # record/1513418

    expected = [
        {
            'medium': 'print',
            'value': '1812-9471',
        },
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['issn'], subschema) is None
    assert expected == result['issn']


def test_issn_from_double_022__a_b():
    schema = load_schema('journals')
    subschema = schema['properties']['issn']

    snippet = (
        '<record>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">1812-9471</subfield>'
        '    <subfield code="b">Print</subfield>'
        '  </datafield>'
        '  <datafield tag="022" ind1=" " ind2=" ">'
        '    <subfield code="a">1817-5805</subfield>'
        '    <subfield code="b">Online</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1513418

    expected = [
        {
            'medium': 'print',
            'value': '1812-9471',
        },
        {
            'medium': 'online',
            'value': '1817-5805',
        },
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['issn'], subschema) is None
    assert expected == result['issn']


def test_issn_from_022__a_b_handles_electronic():
    schema = load_schema('journals')
    subschema = schema['properties']['issn']

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

    assert validate(result['issn'], subschema) is None
    assert expected == result['issn']


def test_coden_from_030__a_2():
    schema = load_schema('journals')
    subschema = schema['properties']['coden']

    snippet = (
        '<datafield tag="030" ind1=" " ind2=" ">'
        '  <subfield code="2">CODEN</subfield>'
        '  <subfield code="a">HERAS</subfield>'
        '</datafield>'
    )  # record/1211568

    expected = ['HERAS']
    result = journals.do(create_record(snippet))

    assert validate(result['coden'], subschema) is None
    assert expected == result['coden']


def test_coden_from_double_030__a_2():
    schema = load_schema('journals')
    subschema = schema['properties']['coden']

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
    )  # record/1213834

    expected = [
        '00686',
        'VLUFB',
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['coden'], subschema) is None
    assert expected == result['coden']


def test_journal_titles_from_130__a():
    schema = load_schema('journals')
    subschema = schema['properties']['journal_titles']

    snippet = (
        '<datafield tag="130" ind1=" " ind2=" ">'
        '  <subfield code="a">Physical Review Special Topics - Accelerators and Beams</subfield>'
        '</datafield>'
    )

    expected = [
        {'title': 'Physical Review Special Topics - Accelerators and Beams'},
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['journal_titles'], subschema) is None
    assert expected == result['journal_titles']


def test_journal_titles_from_130__a_b():
    schema = load_schema('journals')
    subschema = schema['properties']['journal_titles']

    snippet = (
        '<datafield tag="130" ind1=" " ind2=" ">'
        '  <subfield code="a">Humana Mente</subfield>'
        '  <subfield code="b">Journal of Philosophical Studies</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'title': 'Humana Mente',
            'subtitle': 'Journal of Philosophical Studies',
        },
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['journal_titles'], subschema) is None
    assert expected == result['journal_titles']


def test_publisher_from_643__b():
    schema = load_schema('journals')
    subschema = schema['properties']['publisher']

    snippet = (
        '<datafield tag="643" ind1=" " ind2=" ">'
        '  <subfield code="b">ANITA PUBLICATIONS, INDIA</subfield>'
        '</datafield>'
    )  # record/1211888

    expected = ['ANITA PUBLICATIONS, INDIA']
    result = journals.do(create_record(snippet))

    assert validate(result['publisher'], subschema) is None
    assert expected == result['publisher']


def test_publisher_from_double_643__b():
    schema = load_schema('journals')
    subschema = schema['properties']['publisher']

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

    assert validate(result['publisher'], subschema) is None
    assert expected == result['publisher']


def test_short_titles_from_711__a():
    schema = load_schema('journals')
    subschema = schema['properties']['short_titles']

    snippet = (
        '<datafield tag="711" ind1=" " ind2=" ">'
        '  <subfield code="a">Phys.Rev.ST Accel.Beams</subfield>'
        '</datafield>'
    )  # record/1212820

    expected = [
        {'title': 'Phys.Rev.ST Accel.Beams'},
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['short_titles'], subschema) is None
    assert expected == result['short_titles']


def test_title_variants_from_730__a():
    schema = load_schema('journals')
    subschema = schema['properties']['title_variants']

    snippet = (
        '<datafield tag="730" ind1=" " ind2=" ">'
        '  <subfield code="a">PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS</subfield>'
        '</datafield>'
    )  # record/1212820

    expected = [
        {'title': 'PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS'},
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['title_variants'], subschema) is None
    assert expected == result['title_variants']


def test_title_variants_from_double_730__a():
    schema = load_schema('journals')
    subschema = schema['properties']['title_variants']

    snippet = (
        '<record>'
        '  <datafield tag="730" ind1=" " ind2=" ">'
        '    <subfield code="a">PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS</subfield>'
        '  </datafield>'
        '  <datafield tag="730" ind1=" " ind2=" ">'
        '    <subfield code="a">PHYSICS REVIEW ST ACCEL BEAMS</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1212820

    expected = [
        {'title': 'PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS'},
        {'title': 'PHYSICS REVIEW ST ACCEL BEAMS'},
    ]
    result = journals.do(create_record(snippet))

    assert validate(result['title_variants'], subschema) is None
    assert expected == result['title_variants']
