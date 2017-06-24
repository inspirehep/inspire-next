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
from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.utils import validate


def test_acronyms_from_111__a_c_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

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

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


def test_acronyms_from_111__a_c_d_double_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

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

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


def test_acronyms_from_111__a_c_double_e_g_x_y():
    schema = load_schema('conferences')
    subschema = schema['properties']['acronyms']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">2013 IEEE Nuclear Science Symposium and Medical Imaging Conference and Workshop on Room-Temperature Semiconductor Detectors</subfield>'
        '  <subfield code="c">Seoul, Korea</subfield>'
        '  <subfield code="e">NSS/MIC 2013</subfield>'
        '  <subfield code="e">RTSD 2013</subfield>'
        '  <subfield code="g">C13-10-26</subfield>'
        '  <subfield code="x">2013-10-26</subfield>'
        '  <subfield code="y">2013-11-02</subfield>'
        '</datafield>'
    )  # record/1218346

    expected = [
        'NSS/MIC 2013',
        'RTSD 2013',
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['acronyms'], subschema) is None
    assert expected == result['acronyms']


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
            'cities': [
                'Austin',
            ],
            'country_code': 'US',
            'postal_address': [
                'Austin, Tex.',
            ],
            'state': 'TX',
        },
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
            'cities': [
                'Yerevan',
            ],
            'country_code': 'AM',
            'postal_address': [
                'Yerevan, Armenia',
            ],
        },
        {
            'cities': [
                'Tbilisi',
            ],
            'country_code': 'GE',
            'postal_address': [
                'Tbilisi, Georgia',
            ],
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
            'cities': [
                'QCD 12',
            ],
            'postal_address': [
                'QCD 12',
            ],
        },  # XXX: Wrong, but the best we can do.
        {
            'cities': [
                'Montpellier',
            ],
            'country_code': 'FR',
            'postal_address': [
                'Montpellier, France',
            ],
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_270__b():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="b">British Columbia</subfield>'
        '</datafield>'
    )  # record/1430104

    expected = [
        {'place_name': 'British Columbia'},
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
            'cities': [
                'Cleveland',
            ],
            'country_code': 'US',
            'postal_address': [
                'Cleveland, Ohio, USA',
            ],
            'state': 'OH',
        },
        {'place_name': 'Case Western Reserve University'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_titles_from_111__a_c_d_g_x_y():
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
        {'title': 'NASA Laboratory Astrophysics Workshop'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_111__double_a_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="111" ind1=" " ind2=" ">'
        '  <subfield code="a">Conférence IAP 2013</subfield>'
        '  <subfield code="a">75 Anniversary Conference</subfield>'
        '  <subfield code="b">The origin of the Hubble sequence</subfield>'
        '</datafield>'
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


def test_contact_details_from_270__m_p():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">jonivar@thphys.nuim.ie</subfield>'
        '  <subfield code="p">Jon-Ivar Skullerud</subfield>'
        '</datafield>'
    )  # record/1517305

    expected = [
        {
            'email': 'jonivar@thphys.nuim.ie',
            'name': 'Jon-Ivar Skullerud',
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_270__triple_m():
    schema = load_schema('conferences')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">mborn37@ift.uni.wroc.pl</subfield>'
        '  <subfield code="m">mb37_wg3@ift.uni.wroc.pl</subfield>'
        '  <subfield code="m">andrzej.borowiec@ift.uni.wroc.pl</subfield>'
        '</datafield>'
    )  # record/1436421

    expected = [
        {'email': 'mborn37@ift.uni.wroc.pl'},
        {'email': 'mb37_wg3@ift.uni.wroc.pl'},
        {'email': 'andrzej.borowiec@ift.uni.wroc.pl'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_series_from_411__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['series']

    snippet = (
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="a">DPF Series</subfield>'
        '</datafield>'
    )  # record/1430017

    expected = [
        {'name': 'DPF Series'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n():
    snippet = (
        '<datafield tag="411" ind1=" " ind2=" ">'
        '  <subfield code="n">7</subfield>'
        '</datafield>'
    )  # record/1447029

    result = conferences.do(create_record(snippet))

    assert 'series' not in result


def test_series_from_411__a_n():
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


def test_series_from_411__a_n_and_411__a():
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


def test_series_from_411__a_n_and_411__n():
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
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_double_411__a_n():
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
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n_and_411__a_n():
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
        },
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['series'], subschema) is None
    assert expected == result['series']


def test_series_from_411__n_and_411__a():
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


def test_series_from_double_411__a():
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


def test_series_from_411__a_and_411__a_n():
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


def test_public_notes_from_500__a():
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


def test_short_description_from_520__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['short_description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">QNP2015 is the Seventh International Conference on Quarks and Nuclear Physics. It is anticipated that QCD practitioners, both experimentalists and theorists, will gather at the Universidad Técnica Federico Santa María, in Valparaíso, Chile during the week of March 2, 2015 to present and discuss the latest advances in the field. The following topics will be covered: quarks and gluons content of nucleons and nuclei, hadron spectroscopy, non-perturbative methods in QCD (including lattice calculations), effective field theories, nuclear matter under extreme conditions and nuclear medium. Participants should register at the conference website https://indico.cern.ch/event/304663/</subfield>'
        '</datafield>'
    )  # record/1326067

    expected = {
            'value': u'QNP2015 is the Seventh International Conference on Quarks and Nuclear Physics. It is anticipated that QCD practitioners, both experimentalists and theorists, will gather at the Universidad Técnica Federico Santa María, in Valparaíso, Chile during the week of March 2, 2015 to present and discuss the latest advances in the field. The following topics will be covered: quarks and gluons content of nucleons and nuclei, hadron spectroscopy, non-perturbative methods in QCD (including lattice calculations), effective field theories, nuclear matter under extreme conditions and nuclear medium. Participants should register at the conference website https://indico.cern.ch/event/304663/',
    }
    result = conferences.do(create_record(snippet))

    assert validate(result['short_description'], subschema) is None
    assert expected == result['short_description']


def test_short_description_from_multiple_520__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['short_description']

    snippet = (
        '<record>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">The alliance "Physics at the Terascale" will host "Proton Structure in the LHC Era", from 29 September - 2 October, 2014 at DESY in Hamburg. The planned structure will be a 2 day SCHOOL (Monday-Tuesday) followed by a 2 day WORKSHOP (Wednesday-Thursday) devoted to the current problems of the LHC data interpretation, related to the particularities of QCD, factorization, proton structure and higher order calculations.</subfield>'
        '  </datafield>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">SCHOOL: (Monday-Tuesday, September 29-30, 2014) The school will address mainly Ph.D. students and postdocs working at the LHC experiments. It includes introductory lectures, accompanied by tutorials in HERAFitter, FastNLO, Applgrid and further tools.</subfield>'
        '  </datafield>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">WORKSHOP: (Wednesday-Thursday, October 1-2, 2014) The following workshop will encompass the open issues in theory and experiment concerning the determination of PDFs, heavy quark masses and strong coupling. The workshop will run as an open session and is more expert-oriented</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1288023

    expected = {
        'value': (
            'The alliance "Physics at the Terascale" will host "Proton Structure in the LHC Era", from 29 September - 2 October, 2014 at DESY in Hamburg. The planned structure will be a 2 day SCHOOL (Monday-Tuesday) followed by a 2 day WORKSHOP (Wednesday-Thursday) devoted to the current problems of the LHC data interpretation, related to the particularities of QCD, factorization, proton structure and higher order calculations.\n'
            'SCHOOL: (Monday-Tuesday, September 29-30, 2014) The school will address mainly Ph.D. students and postdocs working at the LHC experiments. It includes introductory lectures, accompanied by tutorials in HERAFitter, FastNLO, Applgrid and further tools.\n'
            'WORKSHOP: (Wednesday-Thursday, October 1-2, 2014) The following workshop will encompass the open issues in theory and experiment concerning the determination of PDFs, heavy quark masses and strong coupling. The workshop will run as an open session and is more expert-oriented'
        ),
    }
    result = conferences.do(create_record(snippet))

    assert validate(result['short_description'], subschema) is None
    assert expected == result['short_description']


def test_alternative_titles_from_711__a():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (
        '<datafield tag="711" ind1=" " ind2=" ">'
        '  <subfield code="a">GCACSE16</subfield>'
        '</datafield>'
    )  # record/1436454

    expected = [
        {'title': 'GCACSE16'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']


def test_alternative_titles_from_double_711__a():
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
    )  # record/1436454

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


def test_alternative_titles_from_711__double_b():
    schema = load_schema('conferences')
    subschema = schema['properties']['alternative_titles']

    snippet = (
        '<datafield tag="711" ind1=" " ind2=" ">'
        '  <subfield code="b">high energy</subfield>'
        '  <subfield code="b">ACAT</subfield>'
        '</datafield>'
    )  # record/967859

    expected = [
        {'title': 'high energy'},
        {'title': 'ACAT'},
    ]
    result = conferences.do(create_record(snippet))

    assert validate(result['alternative_titles'], subschema) is None
    assert expected == result['alternative_titles']
