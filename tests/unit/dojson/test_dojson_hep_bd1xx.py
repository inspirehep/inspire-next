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

import mock
import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_authors_from_100__a_i_u_x_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Glashow, S.L.</subfield>'
        '  <subfield code="i">INSPIRE-00085173</subfield>'
        '  <subfield code="u">Copenhagen U.</subfield>'
        '  <subfield code="x">1008235</subfield>'
        '  <subfield code="y">1</subfield>'
        '</datafield>'
    )  # record/4328/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'value': 'Copenhagen U.',
                },
            ],
            'curated_relation': True,
            'full_name': 'Glashow, S.L.',
            'ids': [
                {
                    'type': 'INSPIRE ID',
                    'value': 'INSPIRE-00085173',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1008235',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Glashow, S.L.',
        'i': [
            'INSPIRE-00085173',
        ],
        'u': [
            'Copenhagen U.',
        ],
    }
    result = hep2marc.do(result)

    assert expected == result['100']


def test_authors_from_100__a_u_w_y_and_700_a_u_w_x_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Kobayashi, Makoto</subfield>'
        '    <subfield code="u">Kyoto U.</subfield>'
        '    <subfield code="w">M.Kobayashi.5</subfield>'
        '    <subfield code="y">0</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Maskawa, Toshihide</subfield>'
        '    <subfield code="u">Kyoto U.</subfield>'
        '    <subfield code="w">T.Maskawa.1</subfield>'
        '    <subfield code="x">998493</subfield>'
        '    <subfield code="y">1</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/81350/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'value': 'Kyoto U.',
                },
            ],
            'curated_relation': False,
            'full_name': 'Kobayashi, Makoto',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'M.Kobayashi.5',
                },
            ],
        },
        {
            'affiliations': [
                {
                    'value': 'Kyoto U.',
                },
            ],
            'curated_relation': True,
            'full_name': 'Maskawa, Toshihide',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'T.Maskawa.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/998493',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Kobayashi, Makoto',
            'u': [
                'Kyoto U.',
            ],

        },
        '700': [
            {
                'a': 'Maskawa, Toshihide',
                'u': [
                    'Kyoto U.',
                ],
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='Schema 15')
def test_authors_from_100__a_e_w_y_and_700_a_e_w_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = '''
        <record>
          <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Vinokurov, Nikolay A.</subfield>
            <subfield code="e">ed.</subfield>
            <subfield code="w">N.A.Vinokurov.2</subfield>
            <subfield code="y">0</subfield>
          </datafield>
          <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Knyazev, Boris A.</subfield>
            <subfield code="e">ed.</subfield>
            <subfield code="w">B.A.Knyazev.2</subfield>
            <subfield code="y">0</subfield>
          </datafield>
        </record>
    ''' # 1505338/export/xme

    expected = [
        {
            'full_name': 'Vinokurov, Nikolay A.',
            'inspire_roles': ['editor'],
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'N.A.Vinokurov.2',
                },
            ],
            'curated_relation': False
        },
        {
            'full_name': 'Knyazev, Boris A.',
            'inspire_roles': ['editor'],
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'B.A.Knyazev.2',
                },
            ],
            'curated_relation': False
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Vinokurov, Nikolay A.',
        'e': 'ed.',
    }
    expected_700 = [
        {
            'a': 'Knyazev, Boris A.',
            'e': 'ed.'
        }
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


@pytest.mark.xfail(reason='Schema 15')
def test_authors_from_100__a_v_w_x_y_and_700__a_v_w_x_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = '''
        <record>
          <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Balbinot, Eduardo</subfield>
            <subfield code="v">University of Surrey</subfield>
            <subfield code="w">E.Balbinot.1</subfield>
            <subfield code="x">1074657</subfield>
            <subfield code="y">0</subfield>
          </datafield>
          <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Gieles, Mark</subfield>
            <subfield code="v">University of Surrey</subfield>
            <subfield code="w">M.Gieles.1</subfield>
            <subfield code="x">1030594</subfield>
            <subfield code="y">0</subfield>
          </datafield>
        </record>
    ''' # 1512580/export/xme

    expected = [
        {
            'full_name': 'Balbinot, Eduardo',
            'raw_affiliations': {
                'value': 'University of Surrey'
            },
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'E.Balbinot.1',
                }
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1074657'
            },
            'curated_relation': False
        },
        {
            'full_name': 'Gieles, Mark',
            'raw_affiliations': {
                'value': 'University of Surrey'
            },
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'M.Gieles.1',
                }
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1030594'
            },
            'curated_relation': False
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Balbinot, Eduardo',
        'v': 'University of Surrey'
    }
    expected_700 = [
        {
            'a': 'Gieles, Mark',
            'v': 'University of Surrey'
        }
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_i_u_x_y_z_and_double_700__a_u_w_x_y_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Sjostrand, Torbjorn</subfield>'
        '    <subfield code="i">INSPIRE-00126851</subfield>'
        '    <subfield code="u">Lund U., Dept. Theor. Phys.</subfield>'
        '    <subfield code="x">988491</subfield>'
        '    <subfield code="y">1</subfield>'
        '    <subfield code="z">908554</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Mrenna, Stephen</subfield>'
        '    <subfield code="u">Fermilab</subfield>'
        '    <subfield code="w">S.Mrenna.1</subfield>'
        '    <subfield code="x">996606</subfield>'
        '    <subfield code="y">1</subfield>'
        '    <subfield code="z">902796</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Skands, Peter Z.</subfield>'
        '    <subfield code="u">Fermilab</subfield>'
        '    <subfield code="w">P.Z.Skands.1</subfield>'
        '    <subfield code="x">988480</subfield>'
        '    <subfield code="y">1</subfield>'
        '    <subfield code="z">902796</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/712925/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/908554',
                    },
                    'value': 'Lund U., Dept. Theor. Phys.',
                },
            ],
            'curated_relation': True,
            'full_name': 'Sjostrand, Torbjorn',
            'ids': [
                {
                    'type': 'INSPIRE ID',
                    'value': 'INSPIRE-00126851',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/988491',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902796',
                    },
                    'value': 'Fermilab',
                },
            ],
            'curated_relation': True,
            'full_name': 'Mrenna, Stephen',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'S.Mrenna.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/996606',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902796',
                    },
                    'value': 'Fermilab',
                },
            ],
            'curated_relation': True,
            'full_name': 'Skands, Peter Z.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'P.Z.Skands.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/988480',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Sjostrand, Torbjorn',
            'i': 'INSPIRE-00126851',
            'u': [
                'Lund U., Dept. Theor. Phys.',
            ],
        },
        '700': [
            {
                'a': 'Mrenna, Stephen',
                'u': [
                    'Fermilab',
                ],
                'w': 'S.Mrenna.1',
            },
            {
                'a': 'Skands, Peter Z.',
                'u': [
                    'Fermilab',
                ],
                'w': 'P.Z.Skands.1',
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_v_m_w_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Gao, Xu</subfield>'
        '  <subfield code="v">Chern Institute of Mathematics and LPMC, Nankai University, Tianjin, 300071, China</subfield>'
        '  <subfield code="m">gausyu@gmail.com</subfield>'
        '  <subfield code="w">X.Gao.11</subfield>'
        '  <subfield code="y">0</subfield>'
        '</datafield>'
    )  # record/1475380/export/xme

    expected = [
        {
            'curated_relation': False,
            'emails': ['gausyu@gmail.com'],
            'full_name': 'Gao, Xu',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'X.Gao.11',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Gao, Xu',
        'v': [
            'Chern Institute of Mathematics and LPMC, Nankai University, Tianjin, 300071, China',
        ],
        'm': [
            'gausyu@gmail.com',
        ],
        'w': 'X.Gao.11',
    }
    result = hep2marc.do(result)

    assert expected == result['100']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_double_q_u_w_y_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Dineykhan, M.</subfield>'
        '  <subfield code="q">Dineĭkhan, M.</subfield>'
        '  <subfield code="q">Dineikhan, M.</subfield>'
        '  <subfield code="q">Динейхан, М.</subfield>'
        '  <subfield code="u">Dubna, JINR</subfield>'
        '  <subfield code="w">M.Dineykhan.1</subfield>'
        '  <subfield code="y">0</subfield>'
        '  <subfield code="z">902780</subfield>'
        '</datafield>'
    )  # record/144579/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902780',
                    },
                    'value': 'Dubna, JINR',
                },
            ],
            'alternative_names': [
                u'Dineĭkhan, M.',
                u'Dineikhan, M.',
                u'Динейхан, М.',
            ],
            'curated_relation': False,
            'full_name': 'Dineykhan, M.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'M.Dineykhan.1',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Dineykhan, M.',
        'q': [
            u'Dineĭkhan, M.',
            u'Dineikhan, M.',
            u'Динейхан, М.',
        ],
        'u': [
            'Dubna, JINR',
        ],
        'w': 'M.Dineykhan.1',
    }
    result = hep2marc.do(result)

    assert expected == result['100']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_m_u_v_w_y_z_and_700__a_j_v_m_w_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Gao, Xu</subfield>'
        '    <subfield code="m">gausyu@gmail.com</subfield>'
        '    <subfield code="u">Nankai U.</subfield>'
        '    <subfield code="v">Chern Institute of Mathematics and LPMC, Nankai University, Tianjin, 300071, China</subfield>'
        '    <subfield code="w">X.Gao.11</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">906082</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Liu, Ming</subfield>'
        '    <subfield code="j">ORCID:0000-0002-3413-183X</subfield>'
        '    <subfield code="v">School of Mathematics, South China University of Technology, Guangdong, Guangzhou, 510640, China</subfield>'
        '    <subfield code="m">ming.l1984@gmail.com</subfield>'
        '    <subfield code="w">M.Liu.16</subfield>'
        '    <subfield code="y">0</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1475380/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/906082',
                    },
                    'value': 'Nankai U.',
                },
            ],
            'curated_relation': False,
            'emails': [
                'gausyu@gmail.com',
            ],
            'full_name': 'Gao, Xu',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'X.Gao.11',
                },
            ],
        },
        {
            'curated_relation': False,
            'emails': [
                'ming.l1984@gmail.com',
            ],
            'full_name': 'Liu, Ming',
            'ids': [
                {
                    'type': 'ORCID',
                    'value': '0000-0002-3413-183X',
                },
                {
                    'type': 'INSPIRE BAI',
                    'value': 'M.Liu.16',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Gao, Xu',
            'm': [
                'gausyu@gmail.com',
            ],
            'u': [
                'Nankai U.',
            ],
            'w': 'X.Gao.11',
        },
        '700': [
            {
                'a': 'Liu, Ming',
                'j': 'ORCID:0000-0002-3413-183X',
                'v': [
                    'School of Mathematics, South China University of Technology, Guangdong, Guangzhou, 510640, China',
                ],
                'm': [
                    'ming.l1984@gmail.com',
                ],
                'w': 'ming.l1984@gmail.com',
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='wrong roundtrip')
@mock.patch('inspirehep.dojson.hep.fields.bd1xx.logger.warning')
def test_authors_from_100__a_triple_u_w_x_y_triple_z_and_700__double_a_u_w_x_y_z(warning):
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Abe, K.</subfield>'
        '    <subfield code="u">Tokyo U., ICRR</subfield>'
        '    <subfield code="u">Tokyo U.</subfield>'
        '    <subfield code="u">Tokyo U., IPMU</subfield>'
        '    <subfield code="w">Koya.Abe.2</subfield>'
        '    <subfield code="x">1001963</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">903274</subfield>'
        '    <subfield code="z">903273</subfield>'
        '    <subfield code="z">911254</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Gumplinger, P.</subfield>'
        '    <subfield code="a">Hadley, D.R.</subfield>'
        '    <subfield code="u">Warwick U.</subfield>'
        '    <subfield code="w">D.R.Hadley.2</subfield>'
        '    <subfield code="x">1066999</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">903734</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1345256/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903274',
                    },
                    'value': 'Tokyo U., ICRR',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903273',
                    },
                    'value': 'Tokyo U.',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/911254',
                    },
                    'value': 'Tokyo U., IPMU',
                },
            ],
            'curated_relation': False,
            'full_name': 'Abe, K.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'Koya.Abe.2',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1001963',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903734',
                    },
                    'value': 'Warwick U.',
                },
            ],
            'curated_relation': False,
            'full_name': 'Gumplinger, P.',  # XXX: wrong, but the best we can do.
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'D.R.Hadley.2',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1066999',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']
    warning.assert_called_with(
        'Record with mashed up authors list. Taking first author: %s',
        'Gumplinger, P.',
    )

    expected = {
        '100': {
            'a': 'Abe, K.',
            'w': 'Koya.Abe.2',
            'u': [],
        },
        '700': [
            {
                'a': 'Gumplinger, P.',
                'u': [
                    'Warwick U.',
                ],
                'w': 'D.R.Hadley.2',
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100_a_double_u_w_z_y_double_z_and_700__double_u_double_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Dadhich, Naresh</subfield>'
        '    <subfield code="u">Jamia Millia Islamia</subfield>'
        '    <subfield code="u">IUCAA, Pune</subfield>'
        '    <subfield code="w">N.Dadhich.1</subfield>'
        '    <subfield code="x">1012576</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">904738</subfield>'
        '    <subfield code="z">905919</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="u">Jamia Millia Islamia</subfield>'
        '    <subfield code="u">IUCAA, Pune</subfield>'
        '    <subfield code="z">904738</subfield>'
        '    <subfield code="z">905919</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1407917/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/904738',
                    },
                    'value': 'Jamia Millia Islamia',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/905919',
                    },
                    'value': 'IUCAA, Pune',
                },
            ],
            'curated_relation': False,
            'full_name': 'Dadhich, Naresh',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'N.Dadhich.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1012576',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/904738',
                    },
                    'value': 'Jamia Millia Islamia',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/905919',
                    },
                    'value': 'IUCAA, Pune',
                },
            ],
            'curated_relation': False,
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Dadhich, Naresh',
            'u': [
                'Jamia Millia Islamia',
                'IUCAA, Pune',
            ],
            'w': 'N.Dadhich.1',
        },
        '700': [
            {
                'u': [
                    'Jamia Millia Islamia',
                    'IUCAA, Pune',
                ],
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_j_m_u_w_y_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Martins, Ricardo S.</subfield>'
        '  <subfield code="j">ORCID:</subfield>'
        '  <subfield code="m">ricardomartins@iftm.edu.b</subfield>'
        '  <subfield code="u">Unlisted</subfield>'
        '  <subfield code="w">R.S.Martins.1</subfield>'
        '  <subfield code="y">0</subfield>'
        '  <subfield code="z">910325</subfield>'
        '</datafield>'
    )  # record/1475499/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/910325',
                    },
                    'value': 'Unlisted',
                },
            ],
            'curated_relation': False,
            'emails': ['ricardomartins@iftm.edu.b'],
            'full_name': 'Martins, Ricardo S.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'R.S.Martins.1',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Martins, Ricardo S.',
        'j': 'ORCID:',
        'm': [
            'ricardomartins@iftm.edu.b',
        ],
        'u': [
            'Unlisted',
        ],
        'w': 'R.S.Martins.1',
    }
    result = hep2marc.do(result)

    assert expected == result['100']


@pytest.mark.xfail(reason='wrong conversion')
def test_authors_from_100__a_v_w_x_y_and_100_a_v_w_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Tojyo, E.</subfield>'
        '    <subfield code="v">University of Tokyo, Tokyo, Japan</subfield>'
        '    <subfield code="w">Eiki.Tojyo.1</subfield>'
        '    <subfield code="x">1477256</subfield>'
        '    <subfield code="y">0</subfield>'
        '  </datafield>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Hattori, T.</subfield>'
        '    <subfield code="v">Tokyo Institute of Technology, Tokyo, Japan</subfield>'
        '    <subfield code="w">T.Hattori.1</subfield>'
        '    <subfield code="y">0</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'curated_relation': False,
            'full_name': 'Tojyo, E.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'Eiki.Tojyo.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1477256',
            },
        },
        {
            'curated_relation': False,
            'full_name': 'Hattori, T.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'T.Hattori.1',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {}
    result = hep2marc.do(result)

    assert expected == result['100']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_j_m_u_v_w_y():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">MacNair, David</subfield>'
        '  <subfield code="j">JACoW-00009522</subfield>'
        '  <subfield code="m">macnair@slac.stanford.edu</subfield>'
        '  <subfield code="u">SLAC</subfield>'
        '  <subfield code="v">SLAC, Menlo Park, California, USA</subfield>'
        '  <subfield code="w">D.Macnair.2</subfield>'
        '  <subfield code="y">0</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'affiliations': [
                {
                    'value': 'SLAC',
                },
            ],
            'curated_relation': False,
            'emails': ['macnair@slac.stanford.edu'],
            'full_name': 'MacNair, David',
            'ids': [
                {
                    'type': 'JACOW',
                    'value': 'JACoW-00009522',
                },
                {
                    'type': 'INSPIRE BAI',
                    'value': 'D.Macnair.2',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'MacNair, David',
        'j': 'JACoW-00009522',
        'm': [
            'macnair@slac.stanford.edu',
        ],
        'u': [
            'SLAC',
        ],
        'v': [
            'SLAC',
        ],
        'w': 'D.Macnair.2',
    }
    result = hep2marc.do(result)

    assert expected == result['100']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_authors_from_100__a_u_x_w_y_z_with_malformed_x():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Bakhrushin, Iu.P.</subfield>'
        '  <subfield code="u">NIIEFA, St. Petersburg</subfield>'
        '  <subfield code="x">БАХРУШИН, Ю.П.</subfield>'
        '  <subfield code="w">I.P.Bakhrushin.1</subfield>'
        '  <subfield code="y">0</subfield>'
        '  <subfield code="z">903073</subfield>'
        '</datafield>'
    )  # record/931310/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903073',
                    },
                    'value': 'NIIEFA, St. Petersburg',
                },
            ],
            'curated_relation': False,
            'full_name': 'Bakhrushin, Iu.P.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'I.P.Bakhrushin.1',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Bakhrushin, Iu.P.',
        'u': [
            'NIIEFA, St. Petersburg',
        ],
        'w': 'I.P.Bakhrushin.1',
    }
    result = hep2marc.do(result)

    assert expected == result['100']


def test_authors_from_100__a_double_m_double_u_w_y_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<datafield tag="100" ind1=" " ind2=" ">'
        '  <subfield code="a">Puy, Denis</subfield>'
        '  <subfield code="m">puy@tsmi19.sissa.it</subfield>'
        '  <subfield code="m">puy@mesioa.obspm.fr</subfield>'
        '  <subfield code="u">SISSA, Trieste</subfield>'
        '  <subfield code="u">Meudon Observ.</subfield>'
        '  <subfield code="w">D.Puy.2</subfield>'
        '  <subfield code="y">0</subfield>'
        '  <subfield code="z">903393</subfield>'
        '</datafield>'
    )  # record/413614/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'value': 'SISSA, Trieste',
                },
                {
                    'value': 'Meudon Observ.',
                },
            ],
            'curated_relation': False,
            'emails': [
                'puy@tsmi19.sissa.it',
                'puy@mesioa.obspm.fr',
            ],
            'full_name': 'Puy, Denis',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'D.Puy.2',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Puy, Denis',
        'm': [
            'puy@tsmi19.sissa.it',
            'puy@mesioa.obspm.fr',
        ],
        'u': [
            'SISSA, Trieste',
            'Meudon Observ.',
        ],
        'w': 'D.Puy.2',
    }
    result = hep2marc.do(result)


@pytest.mark.xfail(reason='Schema 15')
def test_authors_supervisors_from_100__a_i_j_u_v_x_y_z_and_multiple_701__u_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Spannagel, Simon</subfield>'
        '    <subfield code="i">INSPIRE-00392783</subfield>'
        '    <subfield code="j">ORCID:0000-0003-4708-3774</subfield>'
        '    <subfield code="u">U. Hamburg, Dept. Phys.</subfield>'
        '    <subfield code="v">Deutsches Elektronen-Synchrotron</subfield>'
        '    <subfield code="x">1268225</subfield>'
        '    <subfield code="y">1</subfield>'
        '    <subfield code="z">1222717</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Garutti, Erika</subfield>'
        '    <subfield code="u">U. Hamburg (main)</subfield>'
        '    <subfield code="z">924289</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Mnich, Joachim</subfield>'
        '    <subfield code="u">DESY</subfield>'
        '    <subfield code="u">U. Hamburg (main)</subfield>'
        '    <subfield code="z">902770</subfield>'
        '    <subfield code="z">924289</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Pohl, Martin</subfield>'
        '    <subfield code="u">U. Geneva (main)</subfield>'
        '    <subfield code="z">913279</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1462486/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'value': 'U. Hamburg, Dept. Phys.',
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/1222717',
                    },
                },
            ],
            'curated_relation': True,
            'full_name': 'Spannagel, Simon',
            'ids': [
                {
                    'type': 'INSPIRE ID',
                    'value': 'INSPIRE-00392783',
                },
                {
                    'type': 'ORCID',
                    'value': '0000-0003-4708-3774',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1268225',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/924289',
                    },
                    'value': 'U. Hamburg (main)',
                },
            ],
            'inspire_roles': ['supervisor'],
            'full_name': 'Garutti, Erika',
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902770',
                    },
                    'value': 'DESY',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/924289',
                    },
                    'value': 'U. Hamburg (main)',
                },
            ],
            'inspire_roles': ['supervisor'],
            'full_name': 'Mnich, Joachim',
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/913279',
                    },
                    'value': 'U. Geneva (main)',
                },
            ],
            'inspire_roles': ['supervisor'],
            'full_name': 'Pohl, Martin',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Spannagel, Simon',
            'i': 'INSPIRE-00392783',
            'j': 'ORCID:0000-0003-4708-3774',
            'u': [
                'U. Hamburg, Dept. Phys.',
            ],
            'v': [
                'Deutsches Elektronen-Synchrotron',
            ],
        },
        '701': [
            {
                'a': 'Garutti, Erika',
                'u': [
                    'U. Hamburg',
                ],
            },
            {
                'a': 'Mnich, Joachim',
                'u': [
                    'DESY',
                    'U. Hamburg (main)',
                ],
            },
            {
                'a': 'Pohl, Martin',
                'u': [
                    'U. Geneva (main)',
                ],
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result


@pytest.mark.xfail(reason='Schema 15')
def test_authors_supervisors_from_100_a_u_w_y_z_and_701__double_a_u_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Lang, Brian W.</subfield>'
        '    <subfield code="u">Minnesota U.</subfield>'
        '    <subfield code="w">B.W.Lang.1</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">903010</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Poling, Ron</subfield>'
        '    <subfield code="a">Kubota, Yuichi</subfield>'
        '    <subfield code="u">Minnesota U.</subfield>'
        '    <subfield code="z">903010</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/776962/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                    'value': 'Minnesota U.',
                },
            ],
            'curated_relation': False,
            'full_name': 'Lang, Brian W.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'B.W.Lang.1',
                },
            ],
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                    'value': 'Minnesota U.',
                },
            ],
            'inspire_roles': ['supervisor'],
            'full_name': 'Poling, Ron',
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                    'value': 'Minnesota U.',
                },
            ],
            'inspire_roles': ['supervisor'],
            'full_name': 'Kubota, Yuichi',
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        '100': {
            'a': 'Lang, Brian W.',
            'u': [
                'Minnesota U.',
            ],
            'w': 'B.W.Lang.1',
        },
        '701': [
            {
                'a': 'Poling, Ron',
                'u': [
                    'Minnesota U.',
                ],
            },
            {
                'a': 'Kubota, Yuichi',
                'u': [
                    'Minnesota U.',
                ],
            },
        ],
    }
    result = hep2marc.do(result)

    assert expected == result
