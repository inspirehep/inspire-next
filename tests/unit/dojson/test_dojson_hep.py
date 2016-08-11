# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

import os
import pkg_resources

import mock
import pytest

from dojson import utils
from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import clean_record, get_recid_from_ref


@pytest.fixture
def marcxml_record():
    marcxml = pkg_resources.resource_string(__name__,
                                            os.path.join(
                                                'fixtures',
                                                'test_hep_record.xml')
                                            )
    return create_record(marcxml)


@pytest.fixture
def marcxml_to_json(marcxml_record):
    return hep.do(marcxml_record)


@pytest.fixture
def marcxml_to_json_book():
    marcxml = pkg_resources.resource_string(__name__,
                                            os.path.join(
                                                'fixtures',
                                                'test_hep_book.xml')
                                            )
    record = create_record(marcxml)
    return hep.do(record)


@pytest.fixture
def json_to_marc(marcxml_to_json):
    return hep2marc.do(marcxml_to_json)


def test_schema_present(marcxml_to_json):
    """Test if $schema is created correctly."""
    assert marcxml_to_json['$schema']


def test_control_number(marcxml_to_json_book):
    """"Test if control number and self present."""
    assert marcxml_to_json_book['control_number']
    assert marcxml_to_json_book['self']


def test_isbns(marcxml_to_json, json_to_marc):
    """Test if isbns is created correctly."""
    assert marcxml_to_json['isbns'][0]['value'] == json_to_marc['020'][0]['a']
    assert marcxml_to_json['isbns'][0]['medium'] == json_to_marc['020'][0]['b']


def test_dois(marcxml_to_json, json_to_marc):
    """Test if dois is created correctly."""
    assert (marcxml_to_json['dois'][0]['value'] in
            [p.get('a') for p in json_to_marc['024'] if 'a' in p])


def test_deleted_records(marcxml_to_json, json_to_marc):
    """Test if deleted_recids is created correctly."""
    assert (get_recid_from_ref(marcxml_to_json['deleted_records'][0]) in
            [p.get('a') for p in json_to_marc['981'] if 'a' in p])


def test_new_record(marcxml_to_json, json_to_marc):
    """Test if new_record is created correctly."""
    assert (get_recid_from_ref(marcxml_to_json['new_record']) in
            [p.get('d') for p in json_to_marc['970'] if 'd' in p])


def test_persistent_identifiers(marcxml_to_json, json_to_marc):
    """Test if persistent_identifiers is created correctly."""
    assert (marcxml_to_json['persistent_identifiers'][0]['value'] in
            [p.get('a') for p in json_to_marc['024'] if 'a' in p])


def test_external_system_numbers(marcxml_to_json, json_to_marc):
    """Test if system control number is created correctly."""
    assert (marcxml_to_json['external_system_numbers'][0]['institute'] ==
            json_to_marc['035'][0]['9'])
    assert (marcxml_to_json['external_system_numbers'][0]['value'] ==
            json_to_marc['035'][0]['a'])
    assert (marcxml_to_json['external_system_numbers'][0]['obsolete'] ==
            json_to_marc['035'][0]['z'])


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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['external_system_numbers']


def test_report_numbers(marcxml_to_json, json_to_marc):
    """Test if report number is created correctly."""
    assert (marcxml_to_json['report_numbers'][0]['source'] in
            [a.get('9') for a in json_to_marc['037'] if '9' in a])
    assert (marcxml_to_json['report_numbers'][0]['value'] in
            [a.get('a') for a in json_to_marc['037'] if 'a' in a])


def test_arxiv_eprints(marcxml_to_json, json_to_marc):
    """Test if arxiv eprints is created correctly."""
    assert (marcxml_to_json['arxiv_eprints'][0]['categories'][0] in
            [c.get('c')[0] for c in json_to_marc['037'] if 'c' in c])
    assert (marcxml_to_json['arxiv_eprints'][0]['value'] in
            [a.get('a') for a in json_to_marc['037'] if 'a' in a])


def test_languages(marcxml_to_json, json_to_marc):
    """Test if languages is created correctly."""
    assert marcxml_to_json['languages'][0] == json_to_marc['041'][0]['a']


def test_classification_number(marcxml_to_json, json_to_marc):
    """Test if classification_number is created correctly."""
    for index, val in enumerate(
            marcxml_to_json['classification_number']):
        assert (val['classification_number'] ==
                json_to_marc['084'][index]['a'])
        assert (val['source'] ==
                json_to_marc['084'][index]['9'])
        assert (val['standard'] ==
                json_to_marc['084'][index]['2'])


def test_authors(marcxml_to_json, json_to_marc):
    """Test if authors are created correctly."""
    assert (marcxml_to_json['authors'][0]['full_name'] ==
            json_to_marc['100']['a'])
    assert (marcxml_to_json['authors'][0]['role'] ==
            json_to_marc['100']['e'])
    assert (marcxml_to_json['authors'][0]['alternative_name'] ==
            json_to_marc['100']['q'])
    assert (marcxml_to_json['authors'][0]['email'] ==
            json_to_marc['100']['m'])
    assert (marcxml_to_json['authors'][0]['affiliations'][0]['value'] ==
            json_to_marc['100']['u'][0])
    assert (get_recid_from_ref(marcxml_to_json['authors'][0]['record']) ==
            json_to_marc['100']['x'])
    assert (marcxml_to_json['authors'][0]['curated_relation'] ==
            json_to_marc['100']['y'])


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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
            'email': 'gausyu@gmail.com',
            'full_name': 'Gao, Xu',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'X.Gao.11',
                },
            ],
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

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
            'email': 'ming.l1984@gmail.com',
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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['authors']


@mock.patch('inspirehep.dojson.hep.fields.bd1xx.current_app.logger.error')
def test_authors_from_700__double_a_u_w_x_y_z(error):
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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['authors']
    error.assert_called_with(
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
    result = clean_record(hep.do(create_record(snippet)))

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
            'email': 'ricardomartins@iftm.edu.b',
            'full_name': 'Martins, Ricardo S.',
            'ids': [
                {
                    'type': 'INSPIRE BAI',
                    'value': 'R.S.Martins.1',
                },
            ],
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['authors']


def test_corporate_author(marcxml_to_json, json_to_marc):
    """Test if corporate_author is created correctly."""
    assert (marcxml_to_json['corporate_author'][0] ==
            json_to_marc['110'][0]['a'])


def test_titles(marcxml_to_json, json_to_marc):
    """Test if titles is created correctly."""
    assert (marcxml_to_json['titles'][0]['title'] ==
            json_to_marc['245'][0]['a'])


def test_title_variations(marcxml_to_json, json_to_marc):
    """Test if title_variations is created correctly."""
    assert (marcxml_to_json['title_variations'][0]['title'] ==
            json_to_marc['210'][0]['a'])


def test_title_translations(marcxml_to_json, json_to_marc):
    """Test if title_translations is created correctly."""
    assert (marcxml_to_json['title_translations'][0]['title'] ==
            json_to_marc['242'][0]['a'])
    assert (marcxml_to_json['title_translations'][0]['subtitle'] ==
            json_to_marc['242'][0]['b'])


def test_title_arxiv(marcxml_to_json, json_to_marc):
    """Test if title arxiv is created correctly."""
    def get(key):
        return [d.get(key) for d in marcxml_to_json['titles']]

    assert (json_to_marc['246']['9'] in get('source'))
    assert (json_to_marc['246']['b'] in get('subtitle'))
    assert (json_to_marc['246']['a'] in get('title'))


def test_titles_old(marcxml_to_json, json_to_marc):
    """Test if titles_old is created correctly."""
    assert (marcxml_to_json['titles_old'][0]['source'] ==
            json_to_marc['247'][0]['9'])
    assert (marcxml_to_json['titles_old'][0]['subtitle'] ==
            json_to_marc['247'][0]['b'])
    assert (marcxml_to_json['titles_old'][0]['title'] ==
            json_to_marc['247'][0]['a'])


def test_imprints(marcxml_to_json, json_to_marc):
    """Test if imprints is created correctly."""
    assert (marcxml_to_json['imprints'][0]['place'] ==
            json_to_marc['260'][0]['a'])
    assert (marcxml_to_json['imprints'][0]['publisher'] ==
            json_to_marc['260'][0]['b'])
    assert (marcxml_to_json['imprints'][0]['date'] ==
            json_to_marc['260'][0]['c'])


def test_preprint_date(marcxml_to_json, json_to_marc):
    """Test if preprint_date is created correctly."""
    assert (marcxml_to_json['preprint_date'] ==
            json_to_marc['269'][0]['c'])


def test_page_nr(marcxml_to_json, json_to_marc):
    """Test if page_nr is created correctly."""
    assert (marcxml_to_json['page_nr'][0] ==
            json_to_marc['300'][0]['a'])


def test_book_series(marcxml_to_json, json_to_marc):
    """Test if book_series is created correctly."""
    assert (marcxml_to_json['book_series'][0]['value'] ==
            json_to_marc['490'][0]['a'])
    assert (marcxml_to_json['book_series'][0]['volume'] ==
            json_to_marc['490'][0]['v'])


def test_public_notes(marcxml_to_json, json_to_marc):
    """Test if public_notes is created correctly."""
    assert (marcxml_to_json['public_notes'][0]['value'] ==
            json_to_marc['500'][0]['a'])
    assert (marcxml_to_json['public_notes'][0]['source'] ==
            json_to_marc['500'][0]['9'])


def test_hidden_notes(marcxml_to_json, json_to_marc):
    """Test if hidden_notes is created correctly."""
    assert marcxml_to_json['hidden_notes'][0]['source'] == "CDS"
    assert (marcxml_to_json['hidden_notes'][0]['value'] ==
            json_to_marc['595'][0]['a'])
    assert (marcxml_to_json['hidden_notes'][0]['source'] ==
            json_to_marc['595'][0]['9'])


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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['hidden_notes']


def test_thesis_roundtrip(marcxml_to_json, json_to_marc):
    """Test if thesis is created correctly."""
    assert (marcxml_to_json['thesis']['degree_type'] ==
            json_to_marc['502']['b'])
    assert (marcxml_to_json['thesis']['institutions'][0]['name'] ==
            json_to_marc['502']['c'][0])
    assert (marcxml_to_json['thesis']['date'] ==
            json_to_marc['502']['d'])


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


def test_abstract(marcxml_to_json, json_to_marc):
    """Test if abstract is created correctly."""
    assert (marcxml_to_json['abstracts'][0]['value'] ==
            json_to_marc['520'][0]['a'])
    assert (marcxml_to_json['abstracts'][0]['source'] ==
            json_to_marc['520'][0]['9'])


def test_funding_info(marcxml_to_json, json_to_marc):
    """Test if funding_info is created correctly."""
    assert (marcxml_to_json['funding_info'][0]['agency'] ==
            json_to_marc['536'][0]['a'])
    assert (marcxml_to_json['funding_info'][0]['grant_number'] ==
            json_to_marc['536'][0]['c'])
    assert (marcxml_to_json['funding_info'][0]['project_number'] ==
            json_to_marc['536'][0]['f'])


def test_licence(marcxml_to_json, json_to_marc):
    """Test if license is created correctly."""
    assert (marcxml_to_json['license'][0]['license'] ==
            json_to_marc['540'][0]['a'])
    assert (marcxml_to_json['license'][0]['imposing'] ==
            json_to_marc['540'][0]['b'])
    assert (marcxml_to_json['license'][0]['url'] ==
            json_to_marc['540'][0]['u'])
    assert (marcxml_to_json['license'][0]['material'] ==
            json_to_marc['540'][0]['3'])


def test_copyright(marcxml_to_json, json_to_marc):
    """Test if copyright is created correctly."""
    assert (marcxml_to_json['copyright'][0]['material'] ==
            json_to_marc['542'][0]['3'])
    assert (marcxml_to_json['copyright'][0]['holder'] ==
            json_to_marc['542'][0]['d'])
    assert (marcxml_to_json['copyright'][0]['statement'] ==
            json_to_marc['542'][0]['f'])
    assert (marcxml_to_json['copyright'][0]['url'] ==
            json_to_marc['542'][0]['u'])


def test_field_categories(marcxml_to_json, json_to_marc):
    """Test if field_categories is created correctly."""
    assert (marcxml_to_json['field_categories'][0]['scheme'] ==
            json_to_marc['65017'][0]['2'])
    assert (marcxml_to_json['field_categories'][0]['term'] ==
            json_to_marc['65017'][0]['a'])
    assert (marcxml_to_json['field_categories'][0]['source'] ==
            json_to_marc['65017'][0]['9'])


def test_free_keywords(marcxml_to_json, json_to_marc):
    """Test if free_keywords is created correctly."""
    assert (marcxml_to_json['free_keywords'][0]['value'] ==
            json_to_marc['653'][0]['a'])
    assert (marcxml_to_json['free_keywords'][0]['source'] ==
            json_to_marc['653'][0]['9'])


def test_accelerator_experiments(marcxml_to_json, json_to_marc):
    """Test if accelerator_experiment is created correctly."""
    assert (marcxml_to_json['accelerator_experiments'][0]['accelerator'] ==
            json_to_marc['693'][0]['a'])
    assert (marcxml_to_json['accelerator_experiments'][0]['experiment'] ==
            json_to_marc['693'][0]['e'])


def test_thesaurus_terms(marcxml_to_json, json_to_marc):
    """Test if thesaurus_terms is created correctly."""
    assert (marcxml_to_json['thesaurus_terms'][0]['classification_scheme'] ==
            json_to_marc['695'][0]['2'])
    assert (marcxml_to_json['thesaurus_terms'][0]['energy_range'] ==
            json_to_marc['695'][0]['e'])
    assert (marcxml_to_json['thesaurus_terms'][0]['keyword'] ==
            json_to_marc['695'][0]['a'])


def test_thesis_supervisors_from_701__a_u():
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
            'full_name': 'Garutti, Erika',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['thesis_supervisors']


def test_thesis_supervisors_from_701__a_double_u():
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
            'full_name': 'Mnich, Joachim',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['thesis_supervisors']


def test_thesis_supervisors_from_multiple_701():
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
            'full_name': 'Mnich, Joachim',
        },
        {
            'affiliations': [
                {
                    'curated_relation': False,
                    'value': 'U. Geneva (main)',
                },
            ],
            'full_name': 'Pohl, Martin',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['thesis_supervisors']


def test_thesis_supervisors_from_multiple_701_with_z():
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
            'full_name': 'Pohl, Martin',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['thesis_supervisors']



def test_collaboration(marcxml_to_json, json_to_marc):
    """Test if collaboration is created correctly."""
    assert (marcxml_to_json['collaboration'][0] ==
            json_to_marc['710'][0]['g'])


def test_publication_info(marcxml_to_json, json_to_marc):
    """Test if publication info is created correctly."""
    assert marcxml_to_json['publication_info'][0]['artid'] == '026802'
    assert marcxml_to_json['publication_info'][0]['page_start'] == '123'
    assert marcxml_to_json['publication_info'][0]['page_end'] == '456'
    assert '026802' in json_to_marc['773'][0]['c']
    assert '123-456' in json_to_marc['773'][0]['c']
    assert (marcxml_to_json['publication_info'][0]['journal_issue'] ==
            json_to_marc['773'][0]['n'])
    assert (marcxml_to_json['publication_info'][0]['journal_title'] ==
            json_to_marc['773'][0]['p'])
    assert (marcxml_to_json['publication_info'][0]['journal_volume'] ==
            json_to_marc['773'][0]['v'])
    assert (get_recid_from_ref(marcxml_to_json['publication_info']
            [0]['parent_record']) ==
            json_to_marc['773'][0]['0'])
    assert (marcxml_to_json['publication_info'][0]['year'] ==
            json_to_marc['773'][0]['y'])
    assert (marcxml_to_json['publication_info'][0]['conf_acronym'] ==
            json_to_marc['773'][0]['o'])
    assert (marcxml_to_json['publication_info'][0]['reportnumber'] ==
            json_to_marc['773'][0]['r'])
    assert (marcxml_to_json['publication_info'][0]['confpaper_info'] ==
            json_to_marc['773'][0]['t'])
    assert (marcxml_to_json['publication_info'][0]['cnum'] ==
            json_to_marc['773'][0]['w'])
    assert (marcxml_to_json['publication_info'][0]['pubinfo_freetext'] ==
            json_to_marc['773'][0]['x'])
    assert (marcxml_to_json['publication_info'][0]['isbn'] ==
            json_to_marc['773'][0]['z'])
    assert (marcxml_to_json['publication_info'][0]['note'] ==
            json_to_marc['773'][0]['m'])


def test_succeeding_entry(marcxml_to_json, json_to_marc):
    """Test if succeeding_entry is created correctly."""
    assert (marcxml_to_json['succeeding_entry']
            ['relationship_code'] ==
            json_to_marc['785']['r'])
    assert (get_recid_from_ref(
            marcxml_to_json['succeeding_entry']['record']) ==
            json_to_marc['785']['w'])
    assert (marcxml_to_json['succeeding_entry']['isbn'] ==
            json_to_marc['785']['z'])


def test_url(marcxml_to_json, json_to_marc):
    """Test if url is created correctly."""
    assert (marcxml_to_json['urls'][0]['value'] ==
            json_to_marc['8564'][0]['u'])
    assert (marcxml_to_json['urls'][0]['description'] ==
            json_to_marc['8564'][0]['y'])


def test_collections(marcxml_to_json, json_to_marc):
    """Test if collections is created correctly."""
    for index, val in enumerate(marcxml_to_json['collections']):
        if 'primary' in val:
            assert (val['primary'] ==
                    json_to_marc['980'][index]['a'])


def test_references(marcxml_to_json, json_to_marc, marcxml_record):
    """Test if references are created correctly."""
    def _force_set(obj):
        return set(utils.force_list(obj) or [])

    assert len(marcxml_record['999C5']) == len(marcxml_to_json['references'])
    assert len(json_to_marc['999C5']) == len(marcxml_to_json['references'])

    for index, json_val in enumerate(marcxml_to_json['references']):
        marc_val = json_to_marc['999C5'][index]
        marc_init = marcxml_record['999C5'][index]
        json_val_pub = json_val.get('publication_info', {})
        if '0' in marc_init:
            assert 'record' in json_val and '0' in marc_val
            assert get_recid_from_ref(json_val['record']) == marc_val['0']
        if '1' in marc_init:
            assert 'texkey' in json_val and '1' in marc_val
            assert json_val['texkey'] == marc_val['1']
        if 'a' in marc_init:
            assert 'dois' in json_val and 'a' in marc_val
            assert json_val['dois'][0] == marc_val['a']
        if 'c' in marc_init:
            assert 'collaboration' in json_val and 'c' in marc_val
            assert json_val['collaboration'] == marc_val['c']
        if 'e' in marc_init:
            assert _force_set(marc_val['e']) == _force_set(marc_init['e'])
        if 'h' in marc_init:
            assert 'authors' in json_val and 'h' in marc_val
            json_names = _force_set([a['full_name']
                                     for a in json_val['authors']])
            roundtrip_names = _force_set(marc_val['h'])
            roundtrip_editors = _force_set(marc_val.get('e', []))
            assert json_names and roundtrip_names
            assert json_names.difference(roundtrip_editors) == roundtrip_names
        if 'm' in marc_init:
            assert 'misc' in json_val and 'm' in marc_val
            assert _force_set(json_val['misc']) == _force_set(marc_val['m'])
            assert _force_set(json_val['misc']) == _force_set(marc_init['m'])
        if 'o' in marc_init:
            assert 'number' in json_val and 'o' in marc_val
            assert json_val['number'] == marc_val['o']
        if 'i' in marc_init:
            assert 'isbn' in json_val_pub and 'i' in marc_val
            assert json_val_pub['isbn'] == marc_val['i']
        if 'p' in marc_init:
            assert 'publisher' in json_val.get('imprint', {})
            assert 'p' in marc_val
            assert marc_init['p'] == marc_val['p']
            assert json_val['imprint']['publisher'] == marc_val['p']
        if 'r' in marc_init:
            initial_repnos = _force_set(marc_init['r'])
            json_repnos = _force_set(json_val_pub.get('reportnumber', []))
            json_repnos.union(_force_set(json_val.get('arxiv_eprints', [])))
            roundtrip_repnos = _force_set(marc_val['r'])
            assert roundtrip_repnos  == json_repnos
            # We should have at least one in the end.
            assert roundtrip_repnos
            # But we can not be sure that we ported all of them.
            assert json_repnos.issubset(initial_repnos)
        if 't' in marc_init:
            initial_titles = _force_set(marc_init['t'])
            json_titles = _force_set([t['title'] for t in json_val['titles']])
            roundtrip_titles = _force_set(marc_val['t'])
            assert initial_titles == json_titles
            assert initial_titles == roundtrip_titles
        if 'u' in marc_init:
            initial_urls = _force_set(marc_init['u'])
            json_urls = _force_set([u['value'] for u in json_val['urls']])
            roundtrip_urls = _force_set(marc_val['u'])
            assert initial_urls == json_urls
            assert initial_urls == roundtrip_urls
        if 's' in marc_init:
            assert marc_init['s'] == marc_val['s']
        if 'x' in marc_init:
            initial_raw = _force_set(marc_init['x'])
            json_raw = _force_set([r['value']
                                   for r in json_val['raw_reference']])
            roundtrip_raw = _force_set(marc_val['x'])
            assert initial_raw == json_raw
            assert initial_raw == roundtrip_raw
        if 'y' in marc_init:
            assert 'year' in json_val_pub and 'y' in marc_val
            assert str(json_val_pub['year']) == str(marc_init['y'])
            assert str(marc_val['y']) == str(marc_init['y'])


def test_book_link(marcxml_to_json_book):
    """Test if the link to the book recid is generated correctly."""
    assert (get_recid_from_ref(marcxml_to_json_book['book']['record']) ==
            1409249)


def test_acquisition_source_field():
    """Test acquisition_source."""
    snippet = (
        '<record>'
        '   <datafield tag="541" ind1=" " ind2=" ">'
        '       <subfield code="a">inspire:uid:50000</subfield>'
        '       <subfield code="b">example@gmail.com</subfield>'
        '       <subfield code="c">submission</subfield>'
        '       <subfield code="d">2015-12-10</subfield>'
        '       <subfield code="e">339830</subfield>'
        '   </datafield>'
        '</record>'
    )

    expected = {
        'source': "inspire:uid:50000",
        'email': "example@gmail.com",
        'method': "submission",
        'date': "2015-12-10",
        'submission_number': "339830",
    }
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['acquisition_source']


def test_acquisition_source_field_marcxml():
    """Test acquisition_source MARC output."""
    expected = {
        'a': 'inspire:uid:50000',
        'c': 'submission',
        'b': 'example@gmail.com',
        'e': '339830',
        'd': '2015-12-10'
    }

    record = {"acquisition_source": {
        'source': "inspire:uid:50000",
        'email': "example@gmail.com",
        'method': "submission",
        'date': "2015-12-10",
        'submission_number': "339830",
    }}
    result = hep2marc.do(record)
    assert expected == result['541']
