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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.utils import strip_empty_values


def test_location_from_034__d_f():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['location']


def test_location_from_034__d():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="d">6.07532</subfield>'
        '</datafield>'
    )  # synthetic data

    expected = {
        'longitude': 6.07532,
    }
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['location']


def test_location_from_034__f():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="f">50.7736</subfield>'
        '</datafield>'
    )  # synthetic data

    expected = {
        'latitude': 50.7736,
    }
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['location']


def test_no_location_from_invalid_034__d_f():
    snippet = (
        '<datafield tag="034" ind1=" " ind2=" ">'
        '  <subfield code="d">foo</subfield>'
        '  <subfield code="f">bar</subfield>'
        '</datafield>'
    )  # synthetic data

    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert 'location' not in result


def test_timezone_from_043__t():
    snippet = (
        '<datafield tag="043" ind1=" " ind2=" ">'
        '  <subfield code="t">+05</subfield>'
        '</datafield>'
    )  # record/902635

    expected = ['+05']
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['timezone']


def test_name_from_110__a():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Mid-America Christian U.</subfield>'
        '</datafield>'
    )  # record/1439728

    expected = [['Mid-America Christian U.']]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name']


def test_name_from_110__a_b_u():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Fukushima University</subfield>'
        '  <subfield code="b">Department of Physics</subfield>'
        '  <subfield code="u">Fukushima U.</subfield>'
        '</datafield>'
    )  # record/902812

    expected = [['Fukushima University', 'Fukushima U.']]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name']


def test_name_from_110__b_t_u():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '   <subfield code="b">Institute of Physics</subfield>'
        '   <subfield code="t">Inst. Phys., Belgrade</subfield>'
        '   <subfield code="u">Belgrade, Inst. Phys.</subfield>'
        '</datafield>'
    )   # record/903416

    expected = [['Belgrade, Inst. Phys.', 'Inst. Phys., Belgrade']]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name']


def test_name_from_110__a_b_t_u():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Adelphi University</subfield>'
        '  <subfield code="b">Department of Physics</subfield>'
        '  <subfield code="t">Adelphi U., Dept. Phys.</subfield>'
        '  <subfield code="u">Adelphi U.</subfield>'
        '</datafield>'
    )  # record/902628

    expected = [['Adelphi University', 'Adelphi U.', 'Adelphi U., Dept. Phys.']]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name']


def test_address_from_marcxml_371__a_b_c_d_e_g():
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
            'country': 'Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': [
                'Philosophenweg 16',
            ],
            'postal_code': '69120',
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml_371__double_a_b_c_d_e_g():
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
            'country': 'Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': [
                'Philosophenweg 16',
                'Heidelberg',
            ],
            'postal_code': '69120',
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml_371__a_double_b_c_d_e_g():
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
            'country': 'Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': [
                'Philosophenweg 16',
            ],
            'postal_code': '69120',
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


@pytest.mark.xfail(reason='country_code not populated')
def test_address_from_marcxml_371__a_b_c_double_d_e_g():
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
            'country': 'Deutschland, Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': ('Philosophenweg 16',),
            'postal_code': '69120',
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml_371__a_b_c_d_double_e_g():
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
            'country': 'Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': [
                'Philosophenweg 16',
            ],
            'postal_code': '69120, DE-119',
        }
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml_371__a_b_c_d_e_double_g():
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
            "city": "Heidelberg",
            "country": "Germany",
            "country_code": "DE",
            "state": "Baden-Wuerttemberg",
            "original_address": [
                "Philosophenweg 16",
            ],
            "postal_code": "69120",
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_multiple_marcxml_371__a_b_c_d_e_g():
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
            'country': 'Germany',
            'country_code': 'DE',
            'state': 'Baden-Wuerttemberg',
            'original_address': [
                'Philosophenweg 16',
            ],
            'postal_code': '69120'
        },
        {
            'city': 'Las Cruces',
            'country': 'USA',
            'country_code': 'US',
            'state': 'US-NM',
            'original_address': [
                'Physical Science Lab',
                'Las Cruces, NM 88003',
            ],
            "postal_code": "88003"
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['address']


def test_field_activity_from_372__a():
    snippet = (
        '<datafield tag="372" ind1=" " ind2=" ">'
        '  <subfield code="a">Research center</subfield>'
        '</datafield>'
    )

    expected = ['Research center']
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['field_activity']


def test_name_variants_from_410__a_9():
    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="9">DESY</subfield>'
        '  <subfield code="a">Aachen Tech. Hochsch.</subfield>'
        '</datafield>'
    )  # record/902624

    expected = [
        {
            'source': 'DESY',
            'value': [
                'Aachen Tech. Hochsch.',
            ],
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name_variants']


def test_name_variants_from_410__double_a():
    snippet = (
        '<datafield tag="410" ind1=" " ind2=" ">'
        '  <subfield code="a">Theoretische Teilchenphysik und Kosmologie</subfield>'
        '  <subfield code="a">Elementarteilchenphysik</subfield>'
        '</datafield>'
    )  # record/902624

    expected = [
        {
            'value': [
                'Theoretische Teilchenphysik und Kosmologie',
                'Elementarteilchenphysik',
            ],
        },
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['name_variants']


def test_extra_words_from_410__decuple_g():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['extra_words']


def test_core_from_690c_a_core():
    snippet = (
        '<datafield tag="690" ind1="C" ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )  # record/902645

    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert result['core']


def test_core_from_690c_a_noncore():
    snippet = (
        '<datafield tag="690" ind1="C" ind2=" ">'
        '  <subfield code=a">NONCORE</subfield>'
        '</datafield>'
    )  # record/916025

    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert not result['core']


def test_non_public_notes_from_667__a():
    snippet = (
        '<datafield tag="667" ind1=" " ind2=" ">'
        '  <subfield code="a">Former ICN = Negev U.</subfield>'
        '</datafield>'
    )  # record/902663

    expected = ['Former ICN = Negev U.']
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['non_public_notes']


def test_hidden_notes_from_595__a():
    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="a">The Division is located inside the Department of Physics and Astronomy of the University of Catania Scientific Campus ("Città Universitaria" or "Cittadella"). Via Santa Sofia 64 95123 CATANIA</subfield>'
        '</datafield>'
    )  # record/902879

    expected = [u'The Division is located inside the Department of Physics and Astronomy of the University of Catania Scientific Campus ("Città Universitaria" or "Cittadella"). Via Santa Sofia 64 95123 CATANIA']
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['hidden_notes']


def test_hidden_notes_from_double_595__a():
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
        u'The Roma II Structure was established in 1989 at the University of Rome “Tor Vergata” - cc',
        u'REDACTED thinks we don\'t have to write 110__t: "INFN, Rome 2" because Rome 2 is only in the url but not in the site. She\'ll ask to REDACTED (from INFN) to have her feedback.',
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['hidden_notes']


def test_public_notes_from_680__a():
    snippet = (
        '<datafield tag="680" ind1=" " ind2=" ">'
        '  <subfield code="i">2nd address: Organisation Européenne pour la Recherche Nucléaire (CERN), F-01631 Prévessin Cedex, France</subfield>'
        '</datafield>'
    )  # record/902725

    expected = [
        u'2nd address: Organisation Européenne pour la Recherche Nucléaire (CERN), F-01631 Prévessin Cedex, France'
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['public_notes']


def test_historical_data_from_6781_a():
    snippet = (
        '<datafield tag="678" ind1="1" ind2=" ">'
        '  <subfield code="a">Became IFH (Inst for Hochenergiephysik)in 1968. Since 1992 the official name of the Inst. is simply DESY Zeuthen. Changed 1/26/99 AMR</subfield>'
        '</datafield>'
    )  # record/902666

    expected = [
        'Became IFH (Inst for Hochenergiephysik)in 1968. Since 1992 the official name of the Inst. is simply DESY Zeuthen. Changed 1/26/99 AMR'
    ]
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['historical_data']


def test_historical_data_from_6781_a():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['historical_data']


def test_related_institutes_from__510_a_w_0():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']


def test_related_institutes_from__double_510_a_w_0():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']


def test_related_institutes_from__510_a_w_0_other():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']


def test_related_institutes_from__double_510_a_w_0_predecessor():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']


def test_related_institutes_from__510_a_w_0_successor():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']


def test_related_institutes_from__invalid_510__0():
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
    result = strip_empty_values(institutions.do(create_record(snippet)))

    assert expected == result['related_institutes']
