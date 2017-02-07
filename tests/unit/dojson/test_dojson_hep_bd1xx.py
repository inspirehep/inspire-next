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
                    'schema': 'INSPIRE ID',
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
            'full_name': 'Kobayashi, Makoto',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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
                    'schema': 'INSPIRE BAI',
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

    expected_100 = {
        'a': 'Kobayashi, Makoto',
        'u': [
            'Kyoto U.',
        ],
    }
    expected_700 = [
        {
            'a': 'Maskawa, Toshihide',
            'u': [
                'Kyoto U.',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


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
    '''  # 1505338/export/xme

    expected = [
        {
            'full_name': 'Vinokurov, Nikolay A.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'N.A.Vinokurov.2',
                },
            ],
            'inspire_roles': [
                'editor',
            ],
        },
        {
            'full_name': 'Knyazev, Boris A.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'B.A.Knyazev.2',
                },
            ],
            'inspire_roles': [
                'editor',
            ],
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Vinokurov, Nikolay A.',
        'e': [
            'ed.',
        ],
    }
    expected_700 = [
        {
            'a': 'Knyazev, Boris A.',
            'e': [
                'ed.',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


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
                    'schema': 'INSPIRE ID',
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
                    'schema': 'INSPIRE BAI',
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
                    'schema': 'INSPIRE BAI',
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

    expected_100 = {
        'a': 'Sjostrand, Torbjorn',
        'i': [
            'INSPIRE-00126851'
        ],
        'u': [
            'Lund U., Dept. Theor. Phys.',
        ],
    }
    expected_700 = [
        {
            'a': 'Mrenna, Stephen',
            'u': [
                'Fermilab',
            ],
        },
        {
            'a': 'Skands, Peter Z.',
            'u': [
                'Fermilab',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


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
            'emails': [
                'gausyu@gmail.com',
            ],
            'full_name': 'Gao, Xu',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'X.Gao.11',
                },
            ],
            'raw_affiliations': [
                {
                    'value': 'Chern Institute of Mathematics and LPMC, Nankai University,'
                             ' Tianjin, 300071, China',
                }
            ]
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
    }
    result = hep2marc.do(result)

    assert expected == result['100']


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
            'full_name': 'Dineykhan, M.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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
    }
    result = hep2marc.do(result)

    assert expected == result['100']


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
            'emails': [
                'gausyu@gmail.com',
            ],
            'full_name': 'Gao, Xu',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'X.Gao.11',
                },
            ],
            'raw_affiliations': [
                {
                    'value': 'Chern Institute of Mathematics and LPMC, Nankai University,'
                             ' Tianjin, 300071, China',
                }
            ]
        },
        {
            'emails': [
                'ming.l1984@gmail.com',
            ],
            'full_name': 'Liu, Ming',
            'ids': [
                {
                    'schema': 'ORCID',
                    'value': '0000-0002-3413-183X',
                },
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'M.Liu.16',
                },
            ],
            'raw_affiliations': [
                {
                    'value': 'School of Mathematics, South China University of Technology,'
                             ' Guangdong, Guangzhou, 510640, China',
                }
            ]
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Gao, Xu',
        'm': [
            'gausyu@gmail.com',
        ],
        'u': [
            'Nankai U.',
        ],
        'v': [
            'Chern Institute of Mathematics and LPMC, Nankai University,'
            ' Tianjin, 300071, China',
        ]
    }
    expected_700 = [
        {
            'a': 'Liu, Ming',
            'j': [
                'ORCID:0000-0002-3413-183X',
            ],
            'v': [
                'School of Mathematics, South China University of '
                'Technology, Guangdong, Guangzhou, 510640, China',
            ],
            'm': [
                'ming.l1984@gmail.com',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


@mock.patch('inspirehep.dojson.hep.rules.bd1xx.logger.warning')
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
            'full_name': 'Abe, K.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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
            'full_name': 'Gumplinger, P.',  # XXX: wrong, but the best we can do.
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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

    expected_100 = {
        'a': 'Abe, K.',
        'u': [
            'Tokyo U., ICRR',
            'Tokyo U.',
            'Tokyo U., IPMU'
        ],
    }
    expected_700 = [
        {
            'a': 'Gumplinger, P.',
            'u': [
                'Warwick U.',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


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
            'emails': [
                'ricardomartins@iftm.edu.b',
            ],
            'full_name': 'Martins, Ricardo S.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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
        'm': [
            'ricardomartins@iftm.edu.b',
        ],
        'u': [
            'Unlisted',
        ],
    }
    result = hep2marc.do(result)

    assert expected == result['100']


def test_authors_from_100__a_v_w_x_y_and_100__a_v_w_y():
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
            'full_name': 'Tojyo, E.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'Eiki.Tojyo.1',
                },
            ],
            'raw_affiliations': [
                {
                    'value': 'University of Tokyo, Tokyo, Japan',
                }
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1477256',
            },
        },
        {
            'full_name': 'Hattori, T.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'T.Hattori.1',
                },
            ],
            'raw_affiliations': [
                {
                    'value': 'Tokyo Institute of Technology, Tokyo, Japan',
                }
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Tojyo, E.',
        'v': [
            'University of Tokyo, Tokyo, Japan',
        ],
    }
    expected_700 = [
        {
            'a': 'Hattori, T.',
            'v': [
                'Tokyo Institute of Technology, Tokyo, Japan',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']


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
                {'value': 'SLAC'},
            ],
            'emails': [
                'macnair@slac.stanford.edu',
            ],
            'full_name': 'MacNair, David',
            'ids': [
                {
                    'schema': 'JACOW',
                    'value': 'JACoW-00009522',
                },
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'D.Macnair.2',
                },
            ],
            'raw_affiliations': [
                {'value': 'SLAC, Menlo Park, California, USA'}
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'MacNair, David',
        'j': [
            'JACoW-00009522',
        ],
        'm': [
            'macnair@slac.stanford.edu',
        ],
        'u': [
            'SLAC',
        ],
        'v': [
            'SLAC, Menlo Park, California, USA',
        ],
    }
    result = hep2marc.do(result)

    assert expected == result['100']


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
            'full_name': 'Bakhrushin, Iu.P.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'I.P.Bakhrushin.1',
                },
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected = {
        'a': 'Bakhrushin, Iu.P.',
        'u': [
            'NIIEFA, St. Petersburg',
        ],
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
                {'value': 'SISSA, Trieste'},
                {'value': 'Meudon Observ.'},
            ],
            'emails': [
                'puy@tsmi19.sissa.it',
                'puy@mesioa.obspm.fr',
            ],
            'full_name': 'Puy, Denis',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
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
    }
    result = hep2marc.do(result)

    assert expected == result['100']


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
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00392783',
                },
                {
                    'schema': 'ORCID',
                    'value': '0000-0003-4708-3774',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1268225',
            },
            'raw_affiliations': [
                {
                    'value': 'Deutsches Elektronen-Synchrotron',
                }
            ],
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
            'inspire_roles': [
                'supervisor',
            ],
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
            'full_name': 'Mnich, Joachim',
            'inspire_roles': [
                'supervisor',
            ],
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
            'full_name': 'Pohl, Martin',
            'inspire_roles': [
                'supervisor',
            ],
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Spannagel, Simon',
        'i': [
            'INSPIRE-00392783',
        ],
        'j': [
            'ORCID:0000-0003-4708-3774',
        ],
        'u': [
            'U. Hamburg, Dept. Phys.',
        ],
        'v': [
            'Deutsches Elektronen-Synchrotron',
        ],
    }
    expected_701 = [
        {
            'a': 'Garutti, Erika',
            'u': [
                'U. Hamburg (main)',
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
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_701 == result['701']


@pytest.mark.xfail(reason='should split mashed up author list')
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
            'full_name': 'Lang, Brian W.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'B.W.Lang.1',
                },
            ],
        },
        {
            'affiliations': [
                {
                    'value': 'Minnesota U.',
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010'
                    }
                }
            ],
            'full_name': 'Poling, Ron',
            'inspire_roles': [
                'supervisor',
            ],
        },
        {
            'affiliations': [
                {
                    'value': 'Minnesota U.',
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                },
            ],
            'full_name': 'Kubota, Yuichi',
            'inspire_roles': [
                'supervisor',
            ],
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Lang, Brian W.',
        'u': [
            'Minnesota U.',
        ],
    }
    expected_701 = [
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
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_701 == result['701']


def test_authors_supervisors_from_100_a_j_u_w_y_z_and_701__a_i_j_u_x_y_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Teroerde, Marius</subfield>'
        '    <subfield code="j">CCID-759515</subfield>'
        '    <subfield code="u">Aachen, Tech. Hochsch.</subfield>'
        '    <subfield code="w">M.Teroerde.1</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">902624</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Feld, Lutz Werner</subfield>'
        '    <subfield code="i">INSPIRE-00315477</subfield>'
        '    <subfield code="j">CCID-456299</subfield>'
        '    <subfield code="u">Aachen, Tech. Hochsch.</subfield>'
        '    <subfield code="x">1060887</subfield>'
        '    <subfield code="y">1</subfield>'
        '    <subfield code="z">902624</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1504133/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902624',
                    },
                    'value': 'Aachen, Tech. Hochsch.',
                },
            ],
            'full_name': 'Teroerde, Marius',
            'ids': [
                {
                    'schema': 'CERN',
                    'value': 'CERN-759515',
                },
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'M.Teroerde.1',
                },
            ],
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902624',
                    },
                    'value': 'Aachen, Tech. Hochsch.',
                },
            ],
            'curated_relation': True,
            'full_name': 'Feld, Lutz Werner',
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00315477',
                },
                {
                    'schema': 'CERN',
                    'value': 'CERN-456299',
                },
            ],
            'inspire_roles': [
                'supervisor'
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1060887',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Teroerde, Marius',
        'j': [
            'CCID-759515',
        ],
        'u': [
            'Aachen, Tech. Hochsch.',
        ],
    }

    expected_701 = [
        {
            'a': 'Feld, Lutz Werner',
            'i': [
                'INSPIRE-00315477',
            ],
            'j': [
                'CCID-456299',
            ],
            'u': [
                'Aachen, Tech. Hochsch.',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_701 == result['701']


def test_authors_from_100_a_double_u_w_z_y_double_z_and_700__a_double_u_w_y_double_z():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    snippet = (
        '<record>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Billo, M.</subfield>'
        '    <subfield code="u">INFN, Turin</subfield>'
        '    <subfield code="u">Turin U.</subfield>'
        '    <subfield code="w">Marco.Billo.1</subfield>'
        '    <subfield code="x">1016336</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">902889</subfield>'
        '    <subfield code="z">903297</subfield>'
        '  </datafield>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">Gliozzi, F.</subfield>'
        '    <subfield code="u">INFN, Turin</subfield>'
        '    <subfield code="u">Turin U.</subfield>'
        '    <subfield code="w">F.Gliozzi.1</subfield>'
        '    <subfield code="x">1008206</subfield>'
        '    <subfield code="y">0</subfield>'
        '    <subfield code="z">902889</subfield>'
        '    <subfield code="z">903297</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1088610/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902889',
                    },
                    'value': 'INFN, Turin',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903297',
                    },
                    'value': 'Turin U.',
                },
            ],
            'full_name': 'Billo, M.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'Marco.Billo.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1016336',
            },
        },
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902889',
                    },
                    'value': 'INFN, Turin',
                },
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903297',
                    },
                    'value': 'Turin U.',
                },
            ],
            'full_name': 'Gliozzi, F.',
            'ids': [
                {
                    'schema': 'INSPIRE BAI',
                    'value': 'F.Gliozzi.1',
                },
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/1008206',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['authors'], subschema) is None
    assert expected == result['authors']

    expected_100 = {
        'a': 'Billo, M.',
        'u': [
            'INFN, Turin',
            'Turin U.',
        ]
    }
    expected_700 = [
        {
            'a': 'Gliozzi, F.',
            'u': [
                'INFN, Turin',
                'Turin U.',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected_100 == result['100']
    assert expected_700 == result['700']
