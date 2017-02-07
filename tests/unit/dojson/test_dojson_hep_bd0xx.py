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
        {'value': '9780198759713'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {'a': '9780198759713'},
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


def test_isbns_from_020__a_handles_capital_x():
    schema = load_schema('hep')
    subschema = schema['properties']['isbns']

    snippet = (
        '<datafield tag="020" ind1=" " ind2=" ">'
        '  <subfield code="a">069114558X</subfield>'
        '</datafield>'
    )  # record/1230427

    expected = [
        {'value': '069114558X'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {'a': '069114558X'},
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
            'value': '9789402409994',
            'medium': 'online',
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
            'medium': 'print',
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
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9783319006260',
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
            'medium': 'online',
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
            'medium': 'hardcover',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['isbns'], subschema) is None
    assert expected == result['isbns']

    expected = [
        {
            'a': '9789814571661',
            'b': 'hardcover',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['020']


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

    assert expected == result['0247']


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

    assert expected == result['0247']


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

    assert expected == result['0247']


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

    assert expected == result['0247']


def test_texkeys_from_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['texkeys']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRETeX</subfield>'
        '  <subfield code="a">Hagedorn:1963hdh</subfield>'
        '</datafield>'
    )  # record/1403324

    expected = [
        'Hagedorn:1963hdh',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['texkeys'], subschema) is None
    assert expected == result['texkeys']

    expected = [
        {
            '9': 'INSPIRETeX',
            'a': 'Hagedorn:1963hdh',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_texkeys_from_035__z_9_and_035__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['texkeys']

    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRESTeX</subfield>'
        '    <subfield code="z">N.Cartiglia:2015cn</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRETeX</subfield>'
        '    <subfield code="a">Akiba:2016ofq</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1498308

    expected = [
        'Akiba:2016ofq',       # XXX: the first one is the one coming
        'N.Cartiglia:2015cn',  # from the "a" field.
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['texkeys'], subschema) is None
    assert expected == result['texkeys']

    expected = [
        {
            '9': 'INSPIRETeX',
            'a': 'Akiba:2016ofq',
        },
        {
            '9': 'INSPIRETeX',
            'z': 'N.Cartiglia:2015cn',
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_external_system_identifiers_from_035__a_9_discards_arxiv():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">oai:arXiv.org:1611.05079</subfield>'
        '</datafield>'
    )  # record/1498308

    result = hep.do(create_record(snippet))

    assert 'external_system_identifiers' not in result


def test_external_system_identifiers_from_035__z_9_handles_cernkey():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERNKEY</subfield>'
        '  <subfield code="z">0263439</subfield>'
        '</datafield>'
    )  # record/451647

    expected = [
        {
            'schema': 'CERNKEY',
            'value': '0263439',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

    expected = [
        {
            '9': 'CERNKEY',
            'z': '0263439',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['035']


def test_external_system_numbers_from_035__a_d_h_m_9():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_identifiers']

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
            'schema': 'http://cds.cern.ch/oai2d',
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']

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
            'value': '1505.01843',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected = [
        {
            '9': 'arXiv',
            'a': 'arXiv:1505.01843',
            'c': 'hep-ph',
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
        {'a': 'UTPT-89-27'},
        {'a': 'CALT-68-1585'},
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_hidden_from_037__z():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="z">FERMILAB-PUB-17-011-CMS</subfield>'
        '</datafield>'
    )  # record/1508174

    expected = [
        {
            'hidden': True,
            'value': 'FERMILAB-PUB-17-011-CMS',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {'z': 'FERMILAB-PUB-17-011-CMS'}
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_report_numbers_from_037__z_9():
    schema = load_schema('hep')
    subschema = schema['properties']['report_numbers']

    snippet = (
        '<datafield tag="037" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-PUB-16140</subfield>'
        '</datafield>'
    )  # record/1326454

    expected = [
        {
            'source': 'SLAC',
            'value': 'SLAC-PUB-16140',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['report_numbers'], subschema) is None
    assert expected == result['report_numbers']

    expected = [
        {
            '9': 'SLAC',
            'a': 'SLAC-PUB-16140',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['037']


def test_arxiv_eprints_from_037__a_c_9_and_multiple_65017_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    snippet = (
        '<record>'
        '  <datafield tag="037" ind1=" " ind2=" ">'
        '    <subfield code="9">arXiv</subfield>'
        '    <subfield code="a">arXiv:1702.00702</subfield>'
        '    <subfield code="c">math-ph</subfield>'
        '  </datafield>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="a">math-ph</subfield>'
        '    <subfield code="2">arXiv</subfield>'
        '  </datafield>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="a">gr-qc</subfield>'
        '    <subfield code="2">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1511862

    expected = [
        {
            'categories': [
                'math-ph',
                'gr-qc',
            ],
            'value': '1702.00702'
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['arxiv_eprints'], subschema) is None
    assert expected == result['arxiv_eprints']

    expected_035 = [
        {
            '9': 'arXiv',
            'a': 'oai:arXiv.org:1702.00702',
        },
    ]
    expected_037 = [
        {
            '9': 'arXiv',
            'a': 'arXiv:1702.00702',
            'c': 'math-ph',
        },
    ]
    expected_65017 = [
        {
            '2': 'arXiv',
            'a': 'math-ph',
        },
        {
            '2': 'arXiv',
            'a': 'gr-qc',
        },
    ]
    result = hep2marc.do(result)

    assert expected_035 == result['035']
    assert expected_037 == result['037']
    assert expected_65017 == result['65017']


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
