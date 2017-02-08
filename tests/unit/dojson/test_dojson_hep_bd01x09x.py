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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_isbns_from_020__a():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9780198759713</subfield>'
        '</datafield>'
    )  # record/1510325

    expected = [
        {
            'value': '9780198759713',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9780198759713',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_online():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">978-94-024-0999-4</subfield>'
        '  <subfield code="b">Online</subfield>'
        '</datafield>'
    )  # record/1504286

    expected = [
        {
            'value': '978-94-024-0999-4',
            'material': 'online',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9789402409994',
            'b': 'online',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_print():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9781786341105</subfield>'
        '  <subfield code="b">Print</subfield>'
        '</datafield>'
    )  # record/1509456

    expected = [
        {
            'value': '9781786341105',
            'material': 'print',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9781786341105',
            'b': 'print',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_electronic():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9783319006260</subfield>'
        '  <subfield code="b">electronic version</subfield>'
        '</datafield>'
    )  # record/1292006

    expected = [
        {
            'value': '9783319006260',
            'material': 'online',
            'comment': 'electronic',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9783319006260',
            'b': 'online',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_ebook():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">9783319259017</subfield>'
        '  <subfield code="b">eBook</subfield>'
        '</datafield>'
    )  # record/1430829

    expected = [
        {
            'value': '9783319259017',
            'material': 'online',
            'comment': 'ebook',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9783319259017',
            'b': 'online',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_b_normalizes_hardcover():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">978-981-4571-66-1</subfield>'
        '  <subfield code="b">hardcover</subfield>'
        '</datafield>'
    )  # record/1351311

    expected = [
        {
            'value': '9789814571661',
            'material': 'print',
            'comment': 'hardcover',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9789814571661',
            'b': 'print',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_persistent_identifiers_from_0247_a_2_corrects_to_hdl():
    schema = load_schema('hep')
    subschema = schema['properties']['persistent_identifiers']

    snippet = (
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">2027.42/97915</subfield>'
        '</datafield>'
    )  # record/1429523

    expected = [
        {
            'value': '2027.42/97915',
            'schema': 'HDL',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert 'dois' not in result
    assert validate(result['persistent_identifiers'], subschema) is None
    assert expected == result['persistent_identifiers']

    expected = [
        {
            'a': '2027.42/97915',
            '2': 'HDL',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['024']


def test_dois_from_0247_a_2_double_9_ignores_curator_source():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="9">bibcheck</subfield>'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="a">10.1590/S1806-11172008005000006</subfield>'
        '</datafield>'
    )  # record/1117362

    expected = [
        {
            'source': 'bibcheck',
            'value': '10.1590/S1806-11172008005000006',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1590/S1806-11172008005000006',
            '9': 'bibcheck',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['024']


def test_dois_from_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    snippet = (
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">10.1088/0264-9381/31/24/245004</subfield>'
        '</datafield>'
    )  # record/1302395

    expected = [
        {'value': '10.1088/0264-9381/31/24/245004'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1088/0264-9381/31/24/245004',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['024']


def test_dois_from_0247_a_2_9_and_0247_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

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
    )  # record/1286727

    expected = [
        {
            'source': 'bibmatch',
            'value': '10.1088/1475-7516/2015/03/044',
        },
        {
            'value': '10.1088/1475-7516/2015/03/044',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1088/1475-7516/2015/03/044',
            '9': 'bibmatch',
            '2': 'DOI',
        },
        {
            'a': '10.1088/1475-7516/2015/03/044',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['024']


def test_dois_from_0247_a_2_and_0247_a_2_9():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

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
    )  # record/1273665

    expected = [
        {
            'value': '10.1103/PhysRevD.89.072002',
        },
        {
            'source': 'bibmatch',
            'value': '10.1103/PhysRevD.91.019903',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['dois'], subschema) is None
    assert expected == result['dois']

    expected = [
        {
            'a': '10.1103/PhysRevD.89.072002',
            '2': 'DOI',
        },
        {
            'a': '10.1103/PhysRevD.91.019903',
            '9': 'bibmatch',
            '2': 'DOI',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['024']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_external_system_numbers_from_035__a():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_numbers']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">0248362CERCER</subfield>'
        '</datafield>'
    )  # record/1403324

    expected = [
        {
            'value': '0248362CERCER',
            'obsolete': False,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_numbers'], subschema) is None
    assert expected == result['external_system_numbers']

    expected = [
        {'a': '0248362CERCER'},
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_external_system_numbers_from_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_numbers']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRETeX</subfield>'
        '  <subfield code="a">Hagedorn:1963hdh</subfield>'
        '</datafield>'
    )  # record/1403324

    expected = [
        {
            'value': 'Hagedorn:1963hdh',
            'institute': 'INSPIRETeX',
            'obsolete': False,
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_numbers'], subschema) is None
    assert expected == result['external_system_numbers']

    expected = [
        {
            '9': 'INSPIRETeX',
            'a': 'Hagedorn:1963hdh',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


@pytest.mark.xfail(reason='Schema 13')
def test_texkeys_from_multiple_035__a_z_9():
    '''035__9:INSPIRETeX or SPIRESTeX go to texkeys'''
    schema = load_schema('hep')
    subschema = schema['properties']['texkeys']

    snippet = '''
        <record>
          <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="9">SPIRESTeX</subfield>
            <subfield code="z">N.Cartiglia:2015cn</subfield>
          </datafield>
          <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="9">INSPIRETeX</subfield>
            <subfield code="a">Akiba:2016ofq</subfield>
          </datafield>
        </record>
    ''' # record/1498308

    # the first is the one containing the a, the rest is from the z
    expected_head = ['Akiba:2016ofq', 'N.Cartiglia:2015cn']
    result = hep.do(create_record(snippet))

    assert validate(result['texkeys'], subschema) is None
    assert expected == result['texkeys']
    assert [{}] == result['external_system_identifiers']

    expected = [
        {'9': 'INSPIRETeX', 'a': 'Akiba:2016ofq'},
        {'9': 'INSPIRETeX', 'z': 'N.Cartiglia:2015cn'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['035'])


@pytest.mark.xfail(reason='Schema 13')
def test_discard_035__9_arXiv():
    '''035__9:arXiv is redundant with 037__9:arXiv, throw it away'''
    schema = load_schema('hep')

    snippet = '''
        <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="9">arXiv</subfield>
          <subfield code="a">oai:arXiv.org:1611.05079</subfield>
        </datafield>
    ''' # record/1498308

    expected = [{}]
    result = hep.do(create_record(snippet))

    assert validate(result, schema) is None
    assert expected == result['external_system_identifiers']
    assert expected == result['arxiv_eprints']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_external_system_numbers_from_035__a_d_h_m_9():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_numbers']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">http://cds.cern.ch/oai2d</subfield>'
        '  <subfield code="a">oai:cds.cern.ch:325030</subfield>'
        '  <subfield code="d">2015-06-05T13:24:42Z</subfield>'
        '  <subfield code="h">2015-11-09T16:22:48Z</subfield>'
        '  <subfield code="m">marcxml</subfield>'
        '</datafield>'
    )  # record/1403324

    expected = [
        {
            'value': 'oai:cds.cern.ch:325030',
            'institute': 'http://cds.cern.ch/oai2d',
            'obsolete': False,
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_numbers'], subschema) is None
    assert expected == result['external_system_numbers']

    expected = [
        {
            '9': 'http://cds.cern.ch/oai2d',
            'a': 'oai:cds.cern.ch:325030',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_arxiv_eprints_from_037__a_c_9():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">arXiv:1505.01843</subfield>'
        '  <subfield code="c">hep-ph</subfield>'
        '</datafield>'
    )  # record/1368891

    expected = [
        {
            'categories': [
                'hep-ph',
            ],
            'value': 'arXiv:1505.01843',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            'a': 'arXiv:1505.01843',
            'c': [
                'hep-ph',
            ],
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_037__a():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN-EP-2016-319</subfield>'
        '</datafield>'
    )  # record/1511277

    expected = [
        {'value': 'CERN-EP-2016-319'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {'a': 'CERN-EP-2016-319'},
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_two_037__a():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (
        '<record>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="a">UTPT-89-27</subfield>'
        '  </datafield>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="a">CALT-68-1585</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/26564

    expected = [
        {
            'value': 'UTPT-89-27',
        },
        {
            'value': 'CALT-68-1585',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {
            'a': 'UTPT-89-27',
        },
        {
            'a': 'CALT-68-1585',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


@pytest.mark.xfail(reason='Schema 13')
def test_report_numbers_hidden_from_037__z():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = '''
        <datafield tag="037" ind1=" " ind2=" ">
          <subfield code="z">FERMILAB-PUB-17-011-CMS</subfield>
        </datafield>
    ''' # record/1508174

    expected = [
        {'hidden': True, 'value': 'FERMILAB-PUB-17-011-CMS'}
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {'z': 'FERMILAB-PUB-17-011-CMS'}
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


@pytest.mark.xfail(reason='Schema 13')
def test_report_numbers_source_from_037__z_9():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = '''
        <datafield tag="037" ind1=" " ind2=" ">
          <subfield code="9">SLAC</subfield>
          <subfield code="a">SLAC-PUB-16140</subfield>
        </datafield>
    ''' # record/1326454

    expected = [
        {'source': 'SLAC', 'value': 'SLAC-PUB-16140'}
    ]
    result = hep2marc.do(result)

    assert validate(result['arxiv_eprints'], subschema)


@pytest.mark.xfail(reason='Schema 13')
def test_arxiv_eprints_from_037__a_c_9_and_multiple_65017_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = '''
        <record>
          <datafield tag="037" ind1=" " ind2=" ">
            <subfield code="9">arXiv</subfield>
            <subfield code="a">arXiv:1702.00702</subfield>
            <subfield code="c">math-ph</subfield>
          </datafield>
          <datafield tag="650" ind1="1" ind2="7">
            <subfield code="a">math-ph</subfield>
            <subfield code="2">arXiv</subfield>
          </datafield><datafield tag="650" ind1="1" ind2="7">
            <subfield code="a">gr-qc</subfield>
            <subfield code="2">arXiv</subfield></datafield>
        </record>
    ''' # record/1511862

    expected = [
        {
            # the first element is the one in 037__c
            'categories': ['math-ph', 'gr-qc'],
            'value': '1702.00702'
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = {
        # 035 is discarded in hep.do, so it needs to be derived here
        '035': [
            {'9': 'arXiv', 'a': 'oai:arXiv.org:1702.00702'}
        ],
        '037': [
            {'9': 'arXiv', 'a': 'arXiv:1702.00702', 'c': 'math-ph'}
        ],
        '65017': [
            {'2': 'arXiv', 'a': 'math-ph'},
            {'2': 'arXiv', 'a': 'gr-qc'}
        ]
    }
    result = hep2marc.do(result)

    assert expected == result


def test_languages_from_041__a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Italian</subfield>'
        '</datafield>'
    )  # record/1503566

    expected = [
        'it',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'italian'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']


def test_languages_from_041__a_handles_multiple_languages_in_one_a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Russian / English</subfield>'
        '</datafield>'
    )  # record/116959

    expected = [
        'ru',
        'en',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'russian'},
        {'a': 'english'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']


def test_languages_from_double_041__a():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    snippet = (
        '<record>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">French</subfield>'
        '  </datafield>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">German</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1231408

    expected = [
        'fr',
        'de',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['languages'], subschema) is None
    assert expected == result['languages']

    expected = [
        {'a': 'french'},
        {'a': 'german'},
    ]
    result = hep2marc.do(result)

    assert expected == result['041']
