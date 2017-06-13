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

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_collaborations_from_710__g():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">Pierre Auger</subfield>'
        '</datafield>'
    )  # record/1510404

    expected = [
        {'value': 'Pierre Auger'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'Pierre Auger'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_710__g_0():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">ANTARES</subfield>'
        '  <subfield code="0">1110619</subfield>'
        '</datafield>'
    )  # record/1422032/export/xme

    expected = [
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110619',
            },
            'value': 'ANTARES',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'ANTARES'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_collaborations_from_multiple_710__g_0_and_710__g():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    snippet = (
        '<record>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">ANTARES</subfield>'
        '    <subfield code="0">1110619</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">IceCube</subfield>'
        '    <subfield code="0">1108514</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">LIGO Scientific</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">Virgo</subfield>'
        '    <subfield code="0">1110601</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1422032/export/xme

    expected = [
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110619',
            },
            'value': 'ANTARES',
        },
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108514',
            },
            'value': 'IceCube',
        },
        {
            'value': 'LIGO Scientific',
        },
        {
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110601',
            },
            'value': 'Virgo',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collaborations'], subschema) is None
    assert expected == result['collaborations']

    expected = [
        {'g': 'ANTARES'},
        {'g': 'IceCube'},
        {'g': 'LIGO Scientific'},
        {'g': 'Virgo'},
    ]
    result = hep2marc.do(result)

    assert expected == result['710']


def test_publication_info_from_773_c_m_p_v_y_1():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="m">Erratum</subfield>'
        '  <subfield code="p">Phys.Rev.Lett.</subfield>'
        '  <subfield code="v">35</subfield>'
        '  <subfield code="c">130</subfield>'
        '  <subfield code="y">1975</subfield>'
        '  <subfield code="1">1214495</subfield>'
        '</datafield>'
    )  # record/1104/export/xme

    expected = [
        {
            'artid': '130',
            'material': 'erratum',
            'journal_record': {
                '$ref': 'http://localhost:5000/api/journals/1214495',
            },
            'journal_title': 'Phys.Rev.Lett.',
            'journal_volume': '35',
            'page_start': '130',
            'year': 1975,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '130',
            ],
            'm': 'erratum',
            'p': 'Phys.Rev.Lett.',
            'v': '35',
            'y': 1975,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


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


def test_publication_info_from_773__c_w_y_z_0_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="c">95-104</subfield>'
        '  <subfield code="w">C16-03-17</subfield>'
        '  <subfield code="y">2016</subfield>'
        '  <subfield code="z">9783945931080</subfield>'
        '  <subfield code="2">1407887</subfield>'
        '  <subfield code="0">1500425</subfield>'
        '</datafield>'
    )  # record/1501319/export/xme

    expected = [
        {
            'cnum': 'C16-03-17',
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/1407887',
            },
            'page_end': '104',
            'page_start': '95',
            'parent_isbn': '9783945931080',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1500425',
            },
            'year': 2016,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1500425,
            'c': [
                '95-104',
            ],
            'w': 'C16-03-17',
            'y': 2016,
            'z': '9783945931080',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_773__c_r_w_triple_0_2():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (
        '<datafield tag="773" ind1=" " ind2=" ">'
        '  <subfield code="0">1512294</subfield>'
        '  <subfield code="c">122-127</subfield>'
        '  <subfield code="r">arXiv:1702.01329</subfield>'
        '  <subfield code="w">C16-11-21.1</subfield>'
        '  <subfield code="0">1512294</subfield>'
        '  <subfield code="2">1484403</subfield>'
        '  <subfield code="0">1512294</subfield>'
        '</datafield>'
    )  # record/1513005/export/xme

    expected = [
        {
            'cnum': 'C16-11-21.1',
            'conference_record': {
                '$ref': 'http://localhost:5000/api/conferences/1484403',
            },
            'page_end': '127',
            'page_start': '122',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1512294',
            },
            'parent_report_number': 'arXiv:1702.01329',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            '0': 1512294,
            'c': [
                '122-127',
            ],
            'r': 'arXiv:1702.01329',
            'w': 'C16-11-21.1',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['773']


def test_publication_info_from_7731_c_p_v_y():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    snippet = (
        '<datafield tag="773" ind1="1" ind2=" ">'
        '  <subfield code="c">948-979</subfield>'
        '  <subfield code="p">Adv.Theor.Math.Phys.</subfield>'
        '  <subfield code="v">12</subfield>'
        '  <subfield code="y">2008</subfield>'
        '</datafield>'
    )  # record/697133

    expected = [
        {
            'hidden': True,
            'journal_title': 'Adv.Theor.Math.Phys.',
            'journal_volume': '12',
            'page_end': '979',
            'page_start': '948',
            'year': 2008,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_info'], subschema) is None
    assert expected == result['publication_info']

    expected = [
        {
            'c': [
                '948-979',
            ],
            'p': 'Adv.Theor.Math.Phys.',
            'v': '12',
            'y': 2008,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['7731']


def test_publication_info2marc_handles_unicode():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        'publication_info': [
            {
                'artid': u'207–214',
                'journal_issue': '36',
                'journal_title': 'Electronic Journal of Theoretical Physics',
                'journal_volume': '13',
                'year': 2016,
            },
        ],
    }  # holdingpen/650664
    assert validate(record['publication_info'], subschema) is None

    expected = [
        {
            'c': [
                u'207–214',
            ],
            'n': '36',
            'p': 'Electronic Journal of Theoretical Physics',
            'v': '13',
            'y': 2016,
        },
    ]
    result = hep2marc.do(record)

    assert expected == result['773']


def test_related_records_from_78002i_r_w():
    schema = load_schema('hep')
    subschema = schema['properties']['related_records']

    snippet = (
        '<datafield tag="780" ind1="0" ind2="2">'
        '  <subfield code="i">supersedes</subfield>'
        '  <subfield code="r">ATLAS-CONF-2016-113</subfield>'
        '  <subfield code="w">1503270</subfield>'
        '</datafield>'
    )  # record/1510564

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1503270',
            },
            'relation': 'predecessor',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']

    expected = [
        {
            'i': 'supersedes',
            'w': 1503270,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['78002']


def test_related_records_from_78708i_w():
    schema = load_schema('hep')
    subschema = schema['properties']['related_records']

    snippet = (
        '<datafield tag="787" ind1="0" ind2="8">'
        '  <subfield code="i">Addendum</subfield>'
        '  <subfield code="w">1474710</subfield>'
        '</datafield>'
    )  # record/1415979

    expected = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1474710',
            },
            'relation_freetext': 'Addendum',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']

    expected = [
        {
            'i': 'Addendum',
            'w': 1474710,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['78708']
