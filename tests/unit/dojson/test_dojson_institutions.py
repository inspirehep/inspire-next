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
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.utils import validate


def test_location_from_034__d_f():
    schema = load_schema('institutions')
    subschema = schema['properties']['location']

    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="d">6.07532</subfield>'
        '  <subfield code="f">50.7736</subfield>'
        '</datafield>'
    )  # record/902624

    expected = {
        'longitude': 6.07532,
        'latitude': 50.7736,
    }
    result = institutions.do(create_record(snippet))

    assert validate(result['location'], subschema) is None
    assert expected == result['location']


def test_no_location_from_034__d():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="d">6.07532</subfield>'
        '</datafield>'
    )  # synthetic data

    result = institutions.do(create_record(snippet))

    assert 'location' not in result


def test_no_location_from_034__f():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="f">50.7736</subfield>'
        '</datafield>'
    )  # synthetic data

    result = institutions.do(create_record(snippet))

    assert 'location' not in result


def test_no_location_from_invalid_034__d_f():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="d">foo</subfield>'
        '  <subfield code="f">bar</subfield>'
        '</datafield>'
    )  # synthetic data

    result = institutions.do(create_record(snippet))

    assert 'location' not in result


def test_no_location_from_034__double_d():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '   <subfield code="d">32.540776</subfield>'
        '   <subfield code="d">15.561010</subfield>'
        '</datafield>'
    )  # record/1442294

    result = institutions.do(create_record(snippet))

    assert 'location' not in result


def test_external_system_identifiers_from_035__a_9():
    schema = load_schema('institutions')
    subschema = schema['properties']['external_system_identifiers']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">HAL</subfield>'
        '  <subfield code="a">1969</subfield>'
        '</datafield>'
    )  # record/910133

    expected = [
        {
            'schema': 'HAL',
            'value': '1969',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['external_system_identifiers'], subschema) is None
    assert expected == result['external_system_identifiers']


def test_superseded_institutions_from_110__x_z():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">University of Pittsburgh</subfield>'
        '  <subfield code="t">U. Pittsburgh</subfield>'
        '  <subfield code="u">U. Pittsburgh (main)</subfield>'
        '  <subfield code="x">Pittsburgh U., Dept. Phil.</subfield>'
        '  <subfield code="x">Pittsburgh U., Med. School</subfield>'
        '  <subfield code="z">908047</subfield>'
        '  <subfield code="z">905042</subfield>'
        '</datafield>'
    )  # record/1272953

    expected = [
        {
            'curated_relation': True,
            'name': 'Pittsburgh U., Dept. Phil.',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/908047',
            },
            'relation_type': 'superseded',
        },
        {
            'curated_relation': True,
            'name': 'Pittsburgh U., Med. School',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/905042',
            },
            'relation_type': 'superseded',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_ICN_legacy_ICN_institution_and_institution_acronym_from_110__a_t_u():
    schema = load_schema('institutions')

    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">European Organization for Nuclear Research (CERN)</subfield>'
        '  <subfield code="t">CERN, Geneva</subfield>'
        '  <subfield code="u">CERN</subfield>'
        '</datafield>'
    )  # record/902725

    expected = {
        'ICN': [
            'CERN, Geneva',
        ],
        'legacy_ICN': 'CERN',
        'institution': [
            'European Organization for Nuclear Research',
        ],
        'institution_acronym': 'CERN'
    }
    result = institutions.do(create_record(snippet))

    for key in expected:
        assert validate(result[key], schema['properties'][key]) is None
        assert result[key] == expected[key]


def test_ICN_legacy_ICN_institution_department_and_department_acryonym_from_110__a_b_t_u():
    schema = load_schema('institutions')

    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Université Libre de Bruxelles</subfield>'
        '  <subfield code="b">Physique Theorique et Mathematique (PTM)</subfield>'
        '  <subfield code="t">U. Libre Brussels, PTM</subfield>'
        '  <subfield code="u">Brussels U., PTM</subfield>'
        '</datafield>'
    )  # record/909579

    expected = {
        'ICN': [
            'U. Libre Brussels, PTM',
        ],
        'legacy_ICN': 'Brussels U., PTM',
        'institution': [
            u'Université Libre de Bruxelles',
        ],
        'department': [
            'Physique Theorique et Mathematique',
        ],
        'department_acronym': 'PTM'
    }
    result = institutions.do(create_record(snippet))

    for key in expected:
        assert validate(result[key], schema['properties'][key]) is None
        assert result[key] == expected[key]


def test_address_from_marcxml_371__a_b_c_d_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_marcxml_371__double_a_b_c_d_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="a">Heidelberg</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16\nHeidelberg',
            'postal_code': '69120',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_marcxml_371__a_double_b_c_d_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="b">Altstadt</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Altstadt, Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


@pytest.mark.xfail(reason='country_code not populated')
def test_address_from_marcxml_371__a_b_c_double_d_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="d">Deutschland</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_marcxml_371__a_b_c_d_double_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="e">DE-119</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120, DE-119',
        }
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_marcxml_371__a_b_c_d_e_double_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Philosophenweg 16</subfield>'
        '  <subfield code="b">Heidelberg</subfield>'
        '  <subfield code="c">Baden-Wuerttemberg</subfield>'
        '  <subfield code="d">Germany</subfield>'
        '  <subfield code="e">69120</subfield>'
        '  <subfield code="g">DE</subfield>'
        '  <subfield code="g">DE</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120',
            'state': 'Baden-Wuerttemberg',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_address_from_multiple_marcxml_371__a_b_c_d_e_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['address']

    snippet = (
        '<record> '
        '  <datafield tag="371" ind1=" " ind2=" ">'
        '    <subfield code="a">Philosophenweg 16</subfield>'
        '    <subfield code="b">Heidelberg</subfield>'
        '    <subfield code="c">Baden-Wuerttemberg</subfield>'
        '    <subfield code="d">Germany</subfield>'
        '    <subfield code="e">69120</subfield>'
        '    <subfield code="g">DE</subfield>'
        '  </datafield>'
        '  <datafield tag="371" ind1=" " ind2=" ">'
        '    <subfield code="e">88003</subfield>'
        '    <subfield code="a">Physical Science Lab</subfield>'
        '    <subfield code="a">Las Cruces, NM 88003</subfield>'
        '    <subfield code="b">Las Cruces</subfield>'
        '    <subfield code="c">New Mexico</subfield>'
        '    <subfield code="d">USA</subfield>'
        '    <subfield code="g">US</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'city': 'Heidelberg',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': 'Philosophenweg 16',
            'postal_code': '69120'
        },
        {
            'city': 'Las Cruces',
            'country_code': 'US',
            'state': 'US-NM',
            'original_address': 'Physical Science Lab\nLas Cruces, NM 88003',
            'postal_code': '88003'
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['address'], subschema) is None
    assert expected == result['address']


def test_field_activity_from_372__a():
    schema = load_schema('institutions')
    subschema = schema['properties']['field_activity']

    snippet = (
        '<datafield tag="372" ind1=" " ind2=" ">'
        '  <subfield code="a">Research center</subfield>'
        '</datafield>'
    )

    expected = ['Research Center']
    result = institutions.do(create_record(snippet))

    assert validate(result['field_activity'], subschema) is None
    assert expected == result['field_activity']


def test_name_variants_from_410__a_9():
    schema = load_schema('institutions')
    subschema = schema['properties']['name_variants']

    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRE</subfield>'
        '  <subfield code="a">Aachen Tech. Hochsch.</subfield>'
        '</datafield>'
    )  # record/902624

    expected = [
        {
            'source': 'INSPIRE',
            'value': 'Aachen Tech. Hochsch.',
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['name_variants'], subschema) is None
    assert expected == result['name_variants']


def test_name_variants_from_410__9_with_invalid_source():
    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="9">Tech</subfield>'
        '  <subfield code="a">CIIT</subfield>'
        '  <subfield code="g">Inst</subfield>'
        '</datafield>'
    )  # record/1338296

    expected = {}
    result = institutions.do(create_record(snippet))

    assert expected == result.get('name_variants', {})


def test_name_variants_from_410__double_a():
    schema = load_schema('institutions')
    subschema = schema['properties']['name_variants']

    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="a">Theoretische Teilchenphysik und Kosmologie</subfield>'
        '  <subfield code="a">Elementarteilchenphysik</subfield>'
        '</datafield>'
    )  # record/902624

    expected = [
        {'value': 'Theoretische Teilchenphysik und Kosmologie'},
        {'value': 'Elementarteilchenphysik'},
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['name_variants'], subschema) is None
    assert expected == result['name_variants']


def test_extra_words_from_410__decuple_g():
    schema = load_schema('institutions')
    subschema = schema['properties']['extra_words']

    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="g">Institut Theoretische Physik,</subfield>'
        '  <subfield code="g">RWTH, Inst.</subfield>'
        '  <subfield code="g">institute A</subfield>'
        '  <subfield code="g">III. Physikalisches Institut, Technische Hochschule Aachen, Aachen, West</subfield>'
        '  <subfield code="g">physics</subfield>'
        '  <subfield code="g">52056</subfield>'
        '  <subfield code="g">D-52056</subfield>'
        '  <subfield code="g">DE-52056</subfield>'
        '  <subfield code="g">phys</subfield>'
        '  <subfield code="g">I. Physikalisches Institut</subfield>'
        '</datafield>'
    )  # record/902624

    expected = [
        'Institut Theoretische Physik,',
        'RWTH, Inst.',
        'institute A',
        'III. Physikalisches Institut, Technische Hochschule Aachen, Aachen, West',
        'physics',
        '52056',
        'D-52056',
        'DE-52056',
        'phys',
        'I. Physikalisches Institut',
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['extra_words'], subschema) is None
    assert expected == result['extra_words']


def test_core_from_690c_a_core():
    schema = load_schema('institutions')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="690" ind1="C" ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )  # record/902645

    result = institutions.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert result['core']


def test_core_from_690c_a_noncore():
    schema = load_schema('institutions')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="690" ind1="C" ind2=" ">'
        '  <subfield code=a">NONCORE</subfield>'
        '</datafield>'
    )  # record/916025

    result = institutions.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert not result['core']


def test_private_notes_from_667__a():
    schema = load_schema('institutions')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<datafield tag="667" ind1=" " ind2=" ">'
        '  <subfield code="a">Former ICN = Negev U.</subfield>'
        '</datafield>'
    )  # record/902663

    expected = [
        {'value': 'Former ICN = Negev U.'},
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']


def test_private_notes_from_595__a():
    schema = load_schema('institutions')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="a">The Division is located inside the Department of Physics and Astronomy of the University of Catania Scientific Campus ("Città Universitaria" or "Cittadella"). Via Santa Sofia 64 95123 CATANIA</subfield>'
        '</datafield>'
    )  # record/902879

    expected = [
        {'value': u'The Division is located inside the Department of Physics and Astronomy of the University of Catania Scientific Campus ("Città Universitaria" or "Cittadella"). Via Santa Sofia 64 95123 CATANIA'},
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']


def test_private_notes_from_double_595__a():
    schema = load_schema('institutions')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<record>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="a">The Roma II Structure was established in 1989 at the University of Rome “Tor Vergata” - cc</subfield>'
        '  </datafield>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="a">REDACTED thinks we don\'t have to write 110__t: "INFN, Rome 2" because Rome 2 is only in the url but not in the site. She\'ll ask to REDACTED (from INFN) to have her feedback.</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/907691

    expected = [
        {'value': u'The Roma II Structure was established in 1989 at the University of Rome “Tor Vergata” - cc'},
        {'value': u'REDACTED thinks we don\'t have to write 110__t: "INFN, Rome 2" because Rome 2 is only in the url but not in the site. She\'ll ask to REDACTED (from INFN) to have her feedback.'},
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']


def test_public_notes_from_680__i():
    schema = load_schema('institutions')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<datafield tag="680" ind1=" " ind2=" ">'
        '  <subfield code="i">2nd address: Organisation Européenne pour la Recherche Nucléaire (CERN), F-01631 Prévessin Cedex, France</subfield>'
        '</datafield>'
    )  # record/902725

    expected = [
        {'value': u'2nd address: Organisation Européenne pour la Recherche Nucléaire (CERN), F-01631 Prévessin Cedex, France'}
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_historical_data_from_6781_a():
    schema = load_schema('institutions')
    subschema = schema['properties']['historical_data']

    snippet = (
        '<datafield tag="678" ind1="1" ind2=" ">'
        '  <subfield code="a">Became IFH (Inst for Hochenergiephysik)in 1968. Since 1992 the official name of the Inst. is simply DESY Zeuthen. Changed 1/26/99 AMR</subfield>'
        '</datafield>'
    )  # record/902666

    expected = [
        'Became IFH (Inst for Hochenergiephysik)in 1968. Since 1992 the official name of the Inst. is simply DESY Zeuthen. Changed 1/26/99 AMR'
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['historical_data'], subschema) is None
    assert expected == result['historical_data']


def test_historical_data_from_6781_multiple_a():
    schema = load_schema('institutions')
    subschema = schema['properties']['historical_data']

    snippet = (
        '<datafield tag="678" ind1="1" ind2=" ">'
        '  <subfield code="a">Conseil européen pour la Recherche Nucléaire (1952-1954)</subfield>'
        '  <subfield code="a">Organisation européenne pour la Recherche nucléaire (1954-now)</subfield>'
        '  <subfield code="a">Sub title: Laboratoire européen pour la Physique des Particules (1984-now)</subfield>'
        '  <subfield code="a">Sub title: European Laboratory for Particle Physics (1984-now)</subfield>'
        '</datafield>'
    )  # record/902725

    expected = [
        u'Conseil européen pour la Recherche Nucléaire (1952-1954)',
        u'Organisation européenne pour la Recherche nucléaire (1954-now)',
        u'Sub title: Laboratoire européen pour la Physique des Particules (1984-now)',
        u'Sub title: European Laboratory for Particle Physics (1984-now)',
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['historical_data'], subschema) is None
    assert expected == result['historical_data']


def test_related_institutes_from__510_a_w_0():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">1385404</subfield>'
        '  <subfield code="a">U. Caen (main)</subfield>'
        '  <subfield code="w">t</subfield>'
        '</datafield>'
    )  # record/1430106

    expected = [
        {
            'curated_relation': True,
            'name': 'U. Caen (main)',
            'relation_type': 'parent',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/1385404',
            },
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_related_institutes_from__double_510_a_w_0():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<record>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">1385404</subfield>'
        '    <subfield code="a">U. Caen (main)</subfield>'
        '    <subfield code="w">t</subfield>'
        '  </datafield>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">926589</subfield>'
        '    <subfield code="a">CNRS, France</subfield>'
        '    <subfield code="w">t</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1430106

    expected = [
        {
            'curated_relation': True,
            'name': 'U. Caen (main)',
            'relation_type': 'parent',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/1385404',
            },
        },
        {
            'curated_relation': True,
            'name': 'CNRS, France',
            'relation_type': 'parent',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/926589',
            },
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_related_institutes_from__510_a_w_0_other():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">945696</subfield>'
        '  <subfield code="a">UMass Amherst</subfield>'
        '  <subfield code="w">r</subfield>'
        '</datafield>'
    )  # record/902971

    expected = [
        {
            'curated_relation': True,
            'name': 'UMass Amherst',
            'relation_type': 'other',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/945696',
            },
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_related_institutes_from__double_510_a_w_0_predecessor():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<record>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">903276</subfield>'
        '    <subfield code="a">INS, Tokyo</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">905439</subfield>'
        '    <subfield code="a">U. Tokyo, Meson Sci. Lab.</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/902916

    expected = [
        {
            'curated_relation': True,
            'name': 'INS, Tokyo',
            'relation_type': 'predecessor',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/903276',
            },
        },
        {
            'curated_relation': True,
            'name': 'U. Tokyo, Meson Sci. Lab.',
            'relation_type': 'predecessor',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/905439',
            },
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_related_institutes_from__510_a_w_0_successor():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">911753</subfield>'
        '  <subfield code="a">HZB, Berlin</subfield>'
        '  <subfield code="w">b</subfield>'
        '</datafield>'
    )  # record/902831

    expected = [
        {
            'curated_relation': True,
            'name': 'HZB, Berlin',
            'relation_type': 'successor',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/911753',
            },
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']


def test_related_institutes_from__invalid_510__0():
    schema = load_schema('institutions')
    subschema = schema['properties']['related_institutes']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="w">foo</subfield>'
        '</datafield>'
    )  # synthetic data

    expected = [
        {
            'curated_relation': False,
        },
    ]
    result = institutions.do(create_record(snippet))

    assert validate(result['related_institutes'], subschema) is None
    assert expected == result['related_institutes']
