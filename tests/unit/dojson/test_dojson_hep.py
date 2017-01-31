# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016, 2017 CERN.
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

from inspirehep.dojson.hep import hep, hep2marc


def test_doi_but_should_be_hdl_from_0247_a():
    snippet = (
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">2027.42/97915</subfield>'
        '</datafield>'
    ) # 1429523

    expected = [{
        'value': '2027.42/97915',
        'type': 'HDL',
    }]
    result = hep.do(create_record(snippet))

    assert result.get('persistent_identifiers', []) == expected
    assert result.get('dois', []) == []


def test_invalid_doi_but_should_be_hdl_from_0247_a():
    snippet = (
        '<datafield tag="024" ind1="7" ind2=" ">'
        '  <subfield code="2">DOI</subfield>'
        '  <subfield code="a">blablabla</subfield>'
        '</datafield>'
    )

    expected = []
    result = hep.do(create_record(snippet))

    assert result.get('dois', []) == expected


def test_dois_from_0247__a_ignores_curator_source():
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
    result = hep.do(create_record(snippet))

    assert expected == result['dois']


def test_dois_from_0247_a_2():
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

    assert expected == result['dois']


def test_dois_from_0247_a_2_9_and_0247_a_2():
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

    assert expected == result['dois']


def test_dois_from_0247_a_2_and_0247_a_2_9():
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

    assert expected == result['dois']


def test_external_system_numbers_from_970__double_a():
    snippet = (
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">SPIRES-9663061</subfield>'
        '  <subfield code="a">SPIRES-9949933</subfield>'
        '</datafield>'
    )  # record/1217763

    expected = [
        {
            'institute': 'SPIRES',
            'obsolete': True,
            'value': 'SPIRES-9663061',
        },
        {
            'institute': 'SPIRES',
            'obsolete': True,
            'value': 'SPIRES-9949933',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['external_system_numbers']


def test_simple_language():
    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Italian</subfield>'
        '</datafield>'
    )

    expected = ["it"]
    result = hep.do(create_record(snippet))

    assert expected == result['languages']


def test_multiple_languages_same_field():
    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Italian</subfield>'
        '  <subfield code="a">English</subfield>'
        '</datafield>'
    )

    expected = ["it", "en"]
    result = hep.do(create_record(snippet))

    assert expected == result['languages']


def test_multiple_languages():
    snippet = (
        '<record>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">Italian</subfield>'
        '  </datafield>'
        '  <datafield tag="041" ind1=" " ind2=" ">'
        '    <subfield code="a">English</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = ["it", "en"]
    result = hep.do(create_record(snippet))

    assert expected == result['languages']


def test_crappy_language():
    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Yadernaya Fiz.</subfield>'
        '</datafield>'
    )

    expected = []
    result = hep.do(create_record(snippet))

    assert expected == result.get('languages', [])


def test_languages_single_value():
    snippet = (
        '<datafield tag="041" ind1=" " ind2=" ">'
        '  <subfield code="a">Russian / English</subfield>'
        '</datafield>'
    )

    expected = ['ru', 'en']
    result = hep.do(create_record(snippet))

    assert expected == result['languages']



def test_external_system_numbers_from_035__a():
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

    assert expected == result['external_system_numbers']


def test_external_system_numbers_from_035__a_9():
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

    assert expected == result['external_system_numbers']


def test_external_system_numbers_from_035__a_d_h_m_9():
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

    assert expected == result['external_system_numbers']


def test_authors_from_100__a_i_u_x_y():
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

    assert expected == result['authors']


def test_authors_from_100__a_u_w_y_and_700_a_u_w_x_y():
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

    assert expected == result['authors']


def test_authors_from_100__a_i_u_x_y_z_and_double_700__a_u_w_x_y_z():
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

    assert expected == result['authors']


def test_authors_from_100__a_v_m_w_y():
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

    assert expected == result['authors']


def test_authors_from_100__a_():
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

    assert expected == result['authors']


def test_authors_from_700__a_j_v_m_w_y():
    snippet = (
        '<datafield tag="700" ind1=" " ind2=" ">'
        '  <subfield code="a">Liu, Ming</subfield>'
        '  <subfield code="j">ORCID:0000-0002-3413-183X</subfield>'
        '  <subfield code="v">School of Mathematics, South China University of Technology, Guangdong, Guangzhou, 510640, China</subfield>'
        '  <subfield code="m">ming.l1984@gmail.com</subfield>'
        '  <subfield code="w">M.Liu.16</subfield>'
        '  <subfield code="y">0</subfield>'
        '</datafield>'
    )  # record/1475380/export/xme

    expected = [
        {
            'curated_relation': False,
            'emails': ['ming.l1984@gmail.com'],
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

    assert expected == result['authors']


@mock.patch('inspirehep.dojson.hep.fields.bd1xx.logger.warning')
def test_authors_from_700__double_a_u_w_x_y_z(warning):
    snippet = (
        '<datafield tag="700" ind1=" " ind2=" ">'
        '  <subfield code="a">Gumplinger, P.</subfield>'
        '  <subfield code="a">Hadley, D.R.</subfield>'
        '  <subfield code="u">Warwick U.</subfield>'
        '  <subfield code="w">D.R.Hadley.2</subfield>'
        '  <subfield code="x">1066999</subfield>'
        '  <subfield code="y">0</subfield>'
        '  <subfield code="z">903734</subfield>'
        '</datafield>'
    )  # record/1345256/export/xme

    expected = [
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

    assert expected == result['authors']
    warning.assert_called_with(
        'Record with mashed up authors list. Taking first author: %s',
        'Gumplinger, P.',
    )


def test_authors_from_700__double_u():
    snippet = (
        '<datafield tag="700" ind1=" " ind2=" ">'
        '  <subfield code="u">Jamia Millia Islamia</subfield>'
        '  <subfield code="u">IUCAA, Pune</subfield>'
        '  <subfield code="z">904738</subfield>'
        '  <subfield code="z">905919</subfield>'
        '</datafield>'
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
        }
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_from_100__a_j_m_u_w_y_z():
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
    )

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

    assert expected == result['authors']


@pytest.mark.xfail(reason='authors added in the wrong order')
def test_authors_from_100__a_v_w_x_y_and_100_a_v_w_y():
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

    assert expected == result['authors']


def test_authors_from_100__a_j_m_u_v_w_y():
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

    assert expected == result['authors']


def test_authors_from_100__a_u_x_w_y_z_with_malformed_x():
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
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_from_100__a_double_m_double_u_w_y_z():
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
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_public_notes_from_500__a_9():
    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">5 pages</subfield>'
        '</datafield>'
    )  # record/1450044

    expected = [
        {
            'source': 'arXiv',
            'value': '5 pages',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['public_notes']


def test_public_notes_from_500__double_a_9():
    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">11 pages, 8 figures. Submitted to MNRAS</subfield>'
        '  <subfield code="a">preliminary entry</subfield>'
        '</datafield>'
    )  # record/1380257

    expected = [
        {
            'source': 'arXiv',
            'value': '11 pages, 8 figures. Submitted to MNRAS',
        },
        {
            'source': 'arXiv',
            'value': 'preliminary entry',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['public_notes']


def test_public_notes_from_500__a_and_500__a_9():
    snippet = (
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">*Brief entry*</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">11 pages, 5 figures</subfield>'
        '    <subfield code="9">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1450045

    expected = [
        {
            'value': '*Brief entry*',
        },
        {
            'source': 'arXiv',
            'value': '11 pages, 5 figures',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['public_notes']


def test_hidden_notes_from_595__a_9():
    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '  <subfield code="a">Title changed from ALLCAPS</subfield>'
        '</datafield>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['hidden_notes']


def test_hidden_notes_from_595__double_a_9():
    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '  <subfield code="a">TeXtitle from script</subfield>'
        '  <subfield code="a">no affiliation (not clear pn the fulltext)</subfield>'
        '</datafield>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['hidden_notes']


def test_hidden_notes_from_595__a_9_and_595__double_a_9():
    snippet = (
        '<record>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRES-HIDDEN</subfield>'
        '    <subfield code="a">Title changed from ALLCAPS</subfield>'
        '  </datafield>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRES-HIDDEN</subfield>'
        '    <subfield code="a">TeXtitle from script</subfield>'
        '    <subfield code="a">no affiliation (not clear pn the fulltext)</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['hidden_notes']


def test_thesis_multiple_institutions():
    snippet = (
        '<record>'
        '  <datafield tag="502" ind1=" " ind2=" ">'
        '    <subfield code="b">Thesis</subfield>'
        '    <subfield code="c">Nice U.</subfield>'
        '    <subfield code="c">Cote d\'Azur Observ., Nice</subfield>'
        '    <subfield code="d">2014</subfield>'
        '    <subfield code="z">903069</subfield>'
        '    <subfield code="z">904125</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1385648
    expected = [
        {'name': 'Nice U.', 'recid': '903069'},
        {'name': 'Cote d\'Azur Observ., Nice', 'recid': '904125'}
    ]

    result = hep.do(create_record(snippet))['thesis']['institutions']

    assert len(result) == 2
    for expected_inst, result_inst in zip(expected, result):
        assert expected_inst['name'] == result_inst['name']
        assert expected_inst['recid'] in result_inst['record']['$ref']


def test_thesis_from_502__a_c_d_z():
    snippet = (
        '<datafield tag="502" ind1=" " ind2=" ">'
        '  <subfield code="a">PhD</subfield>'
        '  <subfield code="c">IIT, Roorkee</subfield>'
        '  <subfield code="d">2011</subfield>'
        '  <subfield code="z">909554</subfield>'
        '</datafield>'
    )  # record/897773/export/xme

    expected = {
        'date': '2011',
        'defense_date': 'PhD',  # XXX: obviously wrong.
        'institutions': [
            {
                'curated_relation': True,
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/909554',
                },
                'name': 'IIT, Roorkee',
            },
        ],
    }
    result = hep.do(create_record(snippet))

    assert expected == result['thesis']


ACCELERATOR_EXPERIMENTS_DATA = [
    (
        'single_noncurated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="a">LHC</subfield>
        </datafield>
        """,
        [{
            'accelerator': 'LHC',
            'curated_relation': False,
            'experiment': 'CERN-LHC-ATLAS'
        }],
        [{'a': 'LHC', 'e': 'CERN-LHC-ATLAS'}],
    ),
    (
        'multiple_noncurated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="a">LHC</subfield>
        </datafield>
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS2</subfield>
            <subfield code="a">LHC2</subfield>
        </datafield>
        """,
        [
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS'
            },{
                'accelerator': 'LHC2',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS'},
            {'a': 'LHC2', 'e': 'CERN-LHC-ATLAS2'},
        ],
    ),
    (
        'multiple_simultaneous_noncurated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="e">CERN-LHC-ATLAS2</subfield>
            <subfield code="a">LHC</subfield>
        </datafield>
        """,
        [
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS'
            },{
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS'},
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS2'},
        ],
    ),
    (
        'single_curated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="a">LHC</subfield>
            <subfield code="0">0001</subfield>
        </datafield>
        """,
        [{
            'record': 'mocked_record_1',
            'accelerator': 'LHC',
            'curated_relation': True,
            'experiment': 'CERN-LHC-ATLAS'
        }],
        [{'a': 'LHC', 'e': 'CERN-LHC-ATLAS', '0': 1}],
    ),
    (
        'multiple_curated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="a">LHC</subfield>
            <subfield code="0">0001</subfield>
        </datafield>
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS2</subfield>
            <subfield code="a">LHC2</subfield>
            <subfield code="0">0002</subfield>
        </datafield>
        """,
        [
            {
                'record': 'mocked_record_1',
                'accelerator': 'LHC',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS'
            },{
                'record': 'mocked_record_2',
                'accelerator': 'LHC2',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS', '0': 1},
            {'a': 'LHC2', 'e': 'CERN-LHC-ATLAS2', '0': 2},
        ],
    ),
    (
        'multiple_simultaneous_curated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="e">CERN-LHC-ATLAS2</subfield>
            <subfield code="a">LHC</subfield>
            <subfield code="0">0001</subfield>
            <subfield code="0">0002</subfield>
        </datafield>
        """,
        [
            {
                'record': 'mocked_record_1',
                'accelerator': 'LHC',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS'
            },{
                'record': 'mocked_record_2',
                'accelerator': 'LHC',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS', '0': 1},
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS2', '0': 2},
        ],
    ),
    (
        'multiple_simultaneous_mixed',
        """
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">CERN-LHC-ATLAS</subfield>
            <subfield code="e">CERN-LHC-ATLAS2</subfield>
            <subfield code="a">LHC</subfield>
            <subfield code="0">0001</subfield>
        </datafield>
        """,
        [
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS'
            },{
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS'},
            {'a': 'LHC', 'e': 'CERN-LHC-ATLAS2'},
        ],
    ),
]


@pytest.mark.parametrize(
    'test_name,xml_snippet,expected_json,expected_marc',
    ACCELERATOR_EXPERIMENTS_DATA,
    ids=[acc_exp[0] for acc_exp in ACCELERATOR_EXPERIMENTS_DATA]
)
@mock.patch('inspirehep.dojson.hep.fields.bd6xx.get_recid_from_ref')
@mock.patch('inspirehep.dojson.hep.fields.bd6xx.get_record_ref')
def test_accelerator_experiments(mock_get_record_ref, mock_get_recid_from_ref,
                                 test_name, xml_snippet, expected_json,
                                 expected_marc):
    """Test if accelerator_experiment is created correctly."""
    mock_get_record_ref.side_effect = \
        lambda x, *_: x and 'mocked_record_%s' % x
    mock_get_recid_from_ref.side_effect = \
        lambda x, *_:  x and int(x.rsplit('_')[-1])


    if not xml_snippet.strip().startswith('<record>'):
        xml_snippet = '<record>%s</record>' % xml_snippet

    json_data = hep.do(create_record(xml_snippet))
    json_experiments = json_data['accelerator_experiments']
    marc_experiments = hep2marc.do(json_data)['693']

    assert marc_experiments == expected_marc
    assert json_experiments == expected_json


def test_authors_supervisors_from_701__a_u():
    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Garutti, Erika</subfield>'
        '  <subfield code="u">U. Hamburg (main)</subfield>'
        '</datafield>'
    )  # record/1462486

    expected = [
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'U. Hamburg (main)',
                }
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Garutti, Erika',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_supervisors_from_701__a_double_u():
    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Mnich, Joachim</subfield>'
        '  <subfield code="u">DESY</subfield>'
        '  <subfield code="u">U. Hamburg (main)</subfield>'
        '</datafield>'
    )  # record/1462486

    expected = [
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'DESY',
                },
                {
                    'curated_relation': False,
                    'value': 'U. Hamburg (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Mnich, Joachim',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_supervisors_from_multiple_701():
    snippet = (
        '<record>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Garutti, Erika</subfield>'
        '    <subfield code="u">U. Hamburg (main)</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Mnich, Joachim</subfield>'
        '    <subfield code="u">DESY</subfield>'
        '    <subfield code="u">U. Hamburg (main)</subfield>'
        '  </datafield>'
        '  <datafield tag="701" ind1=" " ind2=" ">'
        '    <subfield code="a">Pohl, Martin</subfield>'
        '    <subfield code="u">U. Geneva (main)</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1462486

    expected = [
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'U. Hamburg (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Garutti, Erika',
        },
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'DESY',
                },
                {
                    'curated_relation': False,
                    'value': 'U. Hamburg (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Mnich, Joachim',
        },
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'U. Geneva (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Pohl, Martin',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_supervisors_from_multiple_701_with_z():
    snippet = (
        '<record>'
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
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/924289',
                    },
                    'value': 'U. Hamburg (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Garutti, Erika',
        },
        {
            'affiliations': [
                {
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/902770',
                    },
                    'value': 'DESY',
                },
                {
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/924289',
                    },
                    'value': 'U. Hamburg (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Mnich, Joachim',
        },
        {
            'affiliations': [
                {
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/913279',
                    },
                    'value': 'U. Geneva (main)',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Pohl, Martin',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_authors_supervisors_from_701__double_a_u_z():
    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Poling, Ron</subfield>'
        '  <subfield code="a">Kubota, Yuichi</subfield>'
        '  <subfield code="u">Minnesota U.</subfield>'
        '  <subfield code="z">903010</subfield>'
        '</datafield>'
    )  # record/776962/export/xme

    expected = [
        {
            'affiliations': [
                {
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                    'value': 'Minnesota U.',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Poling, Ron',
        },
        {
            'affiliations': [
                {
                    'curated_relation': True,
                    'record': {
                        '$ref': 'http://localhost:5000/api/institutions/903010',
                    },
                    'value': 'Minnesota U.',
                },
            ],
            'contributor_roles': [
                {
                    'schema': 'CRediT',
                    'value': 'Supervision',
                },
            ],
            'full_name': 'Kubota, Yuichi',
        }
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['authors']


def test_mashed_publication_info_from_773():
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
    ) # record/820763/export/xme

    expected = {
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
    }
    result = hep.do(create_record(snippet))

    assert expected == result['publication_info'][0]
