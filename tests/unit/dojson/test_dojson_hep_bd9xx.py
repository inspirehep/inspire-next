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

from inspire_schemas.api import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_citeable_from_980__a_citeable():
    schema = load_schema('hep')
    subschema = schema['properties']['citeable']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Citeable</subfield>'
        '</datafield>'
    )  # record/1511471

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['citeable'], subschema) is None
    assert expected == result['citeable']

    expected = [
        {'a': 'Citeable'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


def test_core_from_980__a_core():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )  # record/1509993

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'CORE'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_core_from_980__a_noncore():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">NONCORE</subfield>'
        '</datafield>'
    )  # record/1411887

    expected = False
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'NONCORE'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )  # record/1508668/export/xme

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_special_collections_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['special_collections']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HALhidden</subfield>'
        '</datafield>'
    )  # record/1505341

    expected = [
        'HALHIDDEN',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['special_collections'], subschema) is None
    assert expected == result['special_collections']

    expected = [
        {'a': 'HALHIDDEN'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_refereed_from_980__a_published():
    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Published</subfield>'
        '</datafield>'
    )  # record/1509992

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['refereed'], subschema) is None
    assert expected == result['refereed']

    expected = [
        {'a': 'Published'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_defaults_to_article():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<record></record>'
    )  # synthetic data

    expected = [
        'article',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Book</subfield>'
        '</datafield>'
    )  # record/1512050

    expected = [
        'book',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'book'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_publication_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Review</subfield>'
        '</datafield>'
    )  # record/1509993

    expected = [
        'review',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_type'], subschema) is None
    assert expected == result['publication_type']

    expected = [
        {'a': 'review'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_withdrawn_from_980__a_withdrawn():
    schema = load_schema('hep')
    subschema = schema['properties']['withdrawn']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Withdrawn</subfield>'
        '</datafield>'
    )  # record/1486153

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['withdrawn'], subschema) is None
    assert expected == result['withdrawn']

    expected = [
        {'a': 'Withdrawn'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_references_from_999C5h_m_o_r_s_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">857215</subfield>'
        '  <subfield code="h">R. C. Myers and A. Sinha</subfield>'
        '  <subfield code="m">Seeing a c-theorem with holography ; [hep-th]</subfield>'
        '  <subfield code="o">10</subfield>'
        '  <subfield code="r">arXiv:1006.1263</subfield>'
        '  <subfield code="s">Phys.Rev.,D82,046006</subfield>'
        '  <subfield code="y">2010</subfield>'
        '</datafield>'
    )  # record/1498589/export/xme

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/857215',
            },
            'reference': {
                'arxiv_eprints': [
                    '1006.1263',
                ],
                'authors': [
                    {'full_name': 'R. C. Myers'},
                    {'full_name': 'A. Sinha'},
                ],
                'misc': [
                    'Seeing a c-theorem with holography ; [hep-th]',
                ],
                'number': 10,
                'publication_info': {
                    'artid': '046006',
                    'journal_title': 'Phys.Rev.',
                    'journal_volume': 'D82',
                    'year': 2010,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 857215,
            'h': [
                'R. C. Myers',
                'A. Sinha',
            ],
            'm': [
                'Seeing a c-theorem with holography ; [hep-th]',
            ],
            'o': 10,
            'r': [
                'arXiv:1006.1263',
            ],
            's': 'Phys.Rev.,D82,046006',
            'y': 2010,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']
