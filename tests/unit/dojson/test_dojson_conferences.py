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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.utils import validate


def test_acronym_from_111__a_c_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronym']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">16th Conference on Flavor Physics and CP Violation</subfield>'
        '  <subfield code="c">Hyderabad, INDIA</subfield>'
        '  <subfield code="e">FPCP 2018</subfield>'
        '  <subfield code="g">C18-07-09</subfield>'
        '  <subfield code="x">2018-07-09</subfield>'
        '  <subfield code="y">2018-07-12</subfield>'
        '</datafield>'
    )  # record/1468357

    expected = [
        'FPCP 2018',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronym'], subschema) is None
    assert expected == result['acronym']


@pytest.mark.xfail(reason='tuple produced instead')
def test_acronym_from_111__a_c_d_double_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronym']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">11th international vacuum congress and 7th international conference on solid surfaces</subfield>'
        '  <subfield code="c">Cologne, Germany</subfield>'
        '  <subfield code="d">25 – 29 Sep 1989</subfield>'
        '  <subfield code="e">IVC-11</subfield>'
        '  <subfield code="e">ICSS-7</subfield>'
        '  <subfield code="g">C89-09-25.3</subfield>'
        '  <subfield code="x">1989-09-25</subfield>'
        '  <subfield code="y">1989-09-29</subfield>'
        '</datafield>'
    )  # record/1308774

    expected = [
        'IVC-11',
        'ICSS-7',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronym'], subschema) is None
    assert expected == result['acronym']


def test_address_from_111__a_c_d_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">11th Texas Symposium on Relativistic Astrophysics</subfield>'
        '  <subfield code="c">Austin, Tex.</subfield>'
        '  <subfield code="d">13-17 Dec 1982</subfield>'
        '  <subfield code="g">C82-12-13</subfield>'
        '  <subfield code="x">1982-12-13</subfield>'
        '  <subfield code="y">1982-12-17</subfield>'
        '</datafield>'
    )  # record/965081

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.',
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_111__a_c_d_g_x_y_and_111__c():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="a">Low dimensional physics and gauge principles</subfield>'
        '    <subfield code="c">Yerevan, Armenia</subfield>'
        '    <subfield code="d">21-29 Sep 2011</subfield>'
        '    <subfield code="g">C11-09-21.2</subfield>'
        '    <subfield code="x">2011-09-21</subfield>'
        '    <subfield code="y">2011-09-29</subfield>'
        '  </datafield>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Tbilisi, Georgia</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1220831

    expected = [
        {
            'country_code': 'AM',
            'original_address': 'Yerevan, Armenia',
        },
        {
            'country_code': 'GE',
            'original_address': 'Tbilisi, Georgia',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_111__a_double_c_d_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">16th High-Energy Physics International Conference in Quantum Chromodynamics</subfield>'
        '  <subfield code="c">QCD 12</subfield>'
        '  <subfield code="c">Montpellier, France</subfield>'
        '  <subfield code="d">2-7 Jul 2012</subfield>'
        '  <subfield code="e">QCD 12</subfield>'
        '  <subfield code="g">C12-07-02</subfield>'
        '  <subfield code="x">2012-07-02</subfield>'
        '  <subfield code="y">2012-07-07</subfield>'
        '</datafield>'
    )  # record/1085463

    expected = [
        {
            'original_address': 'QCD 12'
        },
        {
            'country_code': 'FR',
            'original_address': 'Montpellier, France'
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_contact_details_from_marcxml_270_single_p_single_m():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Manfred Lindner',
            'email': 'lindner@mpi-hd.mpg.de',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_double_p_single_m():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '  <subfield code="p">Boogeyman</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'email': 'lindner@mpi-hd.mpg.de',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_single_p_double_m():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="m">lindner@ecmrecords.com</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Manfred Lindner'
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_multiple_marcxml_270():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<record> '
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '    <subfield code="p">Manfred Lindner</subfield>'
        '  </datafield>'
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="p">Wynton Marsalis</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Manfred Lindner',
            'email': 'lindner@mpi-hd.mpg.de',
        },
        {
            'name': 'Wynton Marsalis',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_address_from_270__b():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="b">British Columbia</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'country_code': 'CA',
            'original_address': 'British Columbia',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_111__a_c_e_g_x_y_and_270__b():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="a">2017 International Workshop on Baryon and Lepton Number Violation: From the Cosmos to the LHC</subfield>'
        '    <subfield code="c">Cleveland, Ohio, USA</subfield>'
        '    <subfield code="e">BLV 2017</subfield>'
        '    <subfield code="g">C17-05-15</subfield>'
        '    <subfield code="x">2017-05-15</subfield>'
        '    <subfield code="y">2017-05-18</subfield>'
        '  </datafield>'
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="b">Case Western Reserve University</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1353313

    expected = [
        {
            'original_address': 'Cleveland, Ohio, USA',
            'country_code': 'US',
            'state': 'US-OH',
        },
        {
            'original_address': 'Case Western Reserve University',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_keywords_from_multiple_6531_a_9():
    schema = load_schema('conferences')
    subschema = schema['properties']['keywords']

    snippet = (
        '<record>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">Flavour</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">Flavor</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">Symmetries</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">Neutrino</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">LHC</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">Elementary particle physics</subfield>'
        '  </datafield>'
        '  <datafield tag="653" ind1="1" ind2=" ">'
        '    <subfield code="9">submitter</subfield>'
        '    <subfield code="a">High energy physics</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'source': 'submitter',
            'value': 'Flavour',
        },
        {
            'source': 'submitter',
            'value': 'Flavor',
        },
        {
            'source': 'submitter',
            'value': 'Symmetries',
        },
        {
            'source': 'submitter',
            'value': 'Neutrino',
        },
        {
            'source': 'submitter',
            'value': 'LHC',
        },
        {
            'source': 'submitter',
            'value': 'Elementary particle physics',
        },
        {
            'source': 'submitter',
            'value': 'High energy physics',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']


def test_titles_from_marcxml_111():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">NASA Laboratory Astrophysics Workshop</subfield>'
        '  <subfield code="d">14-16 Feb 2006</subfield>'
        '  <subfield code="x">2006-02-14</subfield>'
        '  <subfield code="c">Las Vegas, Nevada</subfield>'
        '  <subfield code="g">C06-02-14</subfield>'
        '  <subfield code="y">2006-02-16</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'title': 'NASA Laboratory Astrophysics Workshop',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_marcxml_111_with_two_a():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="a">Conférence IAP 2013</subfield>'
        '    <subfield code="a">75 Anniversary Conference</subfield>'
        '    <subfield code="b">The origin of the Hubble sequence</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': u'Conférence IAP 2013',
            'subtitle': 'The origin of the Hubble sequence',
        },
        {
            'title': '75 Anniversary Conference',
            'subtitle': 'The origin of the Hubble sequence',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_alternative_titles_from_marcxml_711():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE16</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'GCACSE16',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_alternative_titles_from_multiple_marcxml_711():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE16</subfield>'
        '  </datafield>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE 2016</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {'title': 'GCACSE16'},
        {'title': 'GCACSE 2016'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_alternative_titles_from_711__a_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (
        '<datafield tag="711" ind1=" " ind2=" ">'
        '  <subfield code="a">XX Riunione Nazionale di Elettromagnetismo</subfield>'
        '  <subfield code="b">Padova</subfield>'
        '</datafield>'
    )  # record/1403856

    expected = [
        {'title': 'XX Riunione Nazionale di Elettromagnetismo'},
        {'title': 'Padova'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_public_notes_from__500_a():
    schema = load_schema('conferences')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">Same conf. as Kyoto 1975: none in intervening years</subfield>'
        '</datafield>'
    )  # record/963579

    expected = [
        {'value': 'Same conf. as Kyoto 1975: none in intervening years'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_public_notes_from_double_500__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">Marion White, PhD (Argonne) Conference Chair Vladimir Shiltsev, PhD (FNAL) Scientific Program Chair Maria Power (Argonne) Conference Editor/Scientific Secretariat</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">Will be published in: JACoW</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1445071

    expected = [
        {'value': 'Marion White, PhD (Argonne) Conference Chair Vladimir Shiltsev, PhD (FNAL) Scientific Program Chair Maria Power (Argonne) Conference Editor/Scientific Secretariat'},
        {'value': 'Will be published in: JACoW'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


@pytest.mark.xfail(reason='tuple is not unpacked')
def test_note_from_500__multiple_a():
    schema = load_schema('conferences')
    subschema = schema['properties']['note']

    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="a">(BSS2011) Trends in Modern Physics: 19 - 21 August, 2011</subfield>'
        '  <subfield code="a">(BS2011) Cosmology and Particle Physics Beyond the Standard Models: 21-17 August, 2011</subfield>'
        '  <subfield code="a">(JW2011) Scientific and Human Legacy of Julius Wess: 27-28 August, 2011</subfield>'
        '  <subfield code="a">(BW2011) Particle Physcs from TeV to Plank Scale: 28 August - 1 September, 2011</subfield>'
        '</datafield>'
    )

    expected = [
        '(BSS2011) Trends in Modern Physics: 19 - 21 August, 2011',
        '(BS2011) Cosmology and Particle Physics Beyond the Standard Models: 21-17 August, 2011',
        '(JW2011) Scientific and Human Legacy of Julius Wess: 27-28 August, 2011',
        '(BW2011) Particle Physcs from TeV to Plank Scale: 28 August - 1 September, 2011',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['note'], subschema) is None
    assert expected == result['note']


def test_series_name_from_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="a">DPF Series</subfield>'
        '</datafield>'
    )  # record/1430017

    expected = [
        {
            'name': 'DPF Series',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_number_from_411__n():
    snippet = (
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="n">7</subfield>'
        '</datafield>'
    )  # record/1447029

    result = conferences.do(create_record(snippet))

    assert 'series' not in result


def test_series_name_and_number_from_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="a">FPCP</subfield>'
        '  <subfield code="n">16</subfield>'
        '</datafield>'
    )  # record/1468357

    expected = [
        {
            'name': 'FPCP',
            'number': 16,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_name_and_number_and_series_name_from_411__a_n_and_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Rencontres de Moriond</subfield>'
        '    <subfield code="n">51</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Moriond EW</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1404073

    expected = [
        {
            'name': 'Rencontres de Moriond',
            'number': 51,
        },
        {
            'name': 'Moriond EW',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_name_and_number_and_series_number_from_411__a_n_and_411__n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">SSI</subfield>'
        '    <subfield code="n">x</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">2</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/963769

    expected = [
        {
            'name': 'SSI',
            'number': 2,
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_double_series_name_and_number_from_double_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">ICHEP</subfield>'
        '    <subfield code="n">5</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Rochester</subfield>'
        '    <subfield code="n">5</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/974856

    expected = [
        {
            'name': 'ICHEP',
            'number': 5,
        },
        {
            'name': 'Rochester',
            'number': 5,
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_name_and_number_from_411__n_and_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">WIN</subfield>'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/963914

    expected = [
        {
            'name': 'WIN',
            'number': 3,
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_name_and_number_from_411__n_and_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="n">3</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">Gordon</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/972145

    expected = [
        {
            'name': 'Gordon',
            'number': 3,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_double_series_name_from_double_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">SNPS</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">NSS</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/964177

    expected = [
        {
            'name': 'SNPS',
        },
        {
            'name': 'NSS',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_and_series_name_and_number_from_411__a_and_411__a_n():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">CEC</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">ICMC</subfield>'
        '    <subfield code="n">2</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/964448

    expected = [
        {
            'name': 'CEC',
        },
        {
            'name': 'ICMC',
            'number': 2,
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_name_and_number_and_series_number_from_411__a_n_and_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<record>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '    <subfield code="a">EDS</subfield>'
        '    <subfield code="n">13</subfield>'
        '  </datafield>'
        '  <datafield tag="411" ind1=" " ind2=" ">'
        '     <subfield code="a">BLOIS</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/980229

    expected = [
        {
            'name': 'EDS',
            'number': 13,
        },
        {
            'name': 'BLOIS',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_short_description_from_520__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['short_description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">QNP2015 is the Seventh International Conference on Quarks and Nuclear Physics. It is anticipated that QCD practitioners, both experimentalists and theorists, will gather at the Universidad Técnica Federico Santa María, in Valparaíso, Chile during the week of March 2, 2015 to present and discuss the latest advances in the field. The following topics will be covered: quarks and gluons content of nucleons and nuclei, hadron spectroscopy, non-perturbative methods in QCD (including lattice calculations), effective field theories, nuclear matter under extreme conditions and nuclear medium. Participants should register at the conference website https://indico.cern.ch/event/304663/</subfield>'
        '</datafield>'
    )  # record/1326067

    expected = [
        {
            'value': u'QNP2015 is the Seventh International Conference on Quarks and Nuclear Physics. It is anticipated that QCD practitioners, both experimentalists and theorists, will gather at the Universidad Técnica Federico Santa María, in Valparaíso, Chile during the week of March 2, 2015 to present and discuss the latest advances in the field. The following topics will be covered: quarks and gluons content of nucleons and nuclei, hadron spectroscopy, non-perturbative methods in QCD (including lattice calculations), effective field theories, nuclear matter under extreme conditions and nuclear medium. Participants should register at the conference website https://indico.cern.ch/event/304663/',
        }
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['short_description'], subschema) is None
    assert expected == result['short_description']
