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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.api import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_citeable_from_980__a_citeable():
    schema = load_schema('hep')
    subschema = schema['properties']['citeable']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Citeable</subfield>'
        '</datafield>'
    )  # record/1511471

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['citeable'], subschema) is None
    assert expected == result['citeable']

    expected = [
        {'a': 'Citeable'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


def test_core_from_980__a_core():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">CORE</subfield>'
        '</datafield>'
    )  # record/1509993

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'CORE'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_core_from_980__a_noncore():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">NONCORE</subfield>'
        '</datafield>'
    )  # record/1411887

    expected = False
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'NONCORE'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )  # record/1508668/export/xme

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_special_collections_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['special_collections']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HALhidden</subfield>'
        '</datafield>'
    )  # record/1505341

    expected = [
        'HALHIDDEN',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['special_collections'], subschema) is None
    assert expected == result['special_collections']

    expected = [
        {'a': 'HALHIDDEN'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_refereed_from_980__a_published():
    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Published</subfield>'
        '</datafield>'
    )  # record/1509992

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['refereed'], subschema) is None
    assert expected == result['refereed']

    expected = [
        {'a': 'Published'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_defaults_to_article():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<record></record>'
    )  # synthetic data

    expected = [
        'article',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Book</subfield>'
        '</datafield>'
    )  # record/1512050

    expected = [
        'book',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'Book'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a_handles_conference_paper():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">ConferencePaper</subfield>'
        '</datafield>'
    )  # record/1589240

    expected = [
        'conference paper',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'ConferencePaper'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_document_type_from_980__a_handles_activity_report():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">ActivityReport</subfield>'
        '</datafield>'
    )  # record/1514964

    expected = [
        'activity report',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'ActivityReport'},
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_publication_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_type']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Review</subfield>'
        '</datafield>'
    )  # record/1509993

    expected = [
        'review',
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['publication_type'], subschema) is None
    assert expected == result['publication_type']

    expected = [
        {'a': 'review'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_withdrawn_from_980__a_withdrawn():
    schema = load_schema('hep')
    subschema = schema['properties']['withdrawn']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">Withdrawn</subfield>'
        '</datafield>'
    )  # record/1486153

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['withdrawn'], subschema) is None
    assert expected == result['withdrawn']

    expected = [
        {'a': 'Withdrawn'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_references_from_999C5r_s_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="r">arXiv:1006.1289</subfield>'
        '  <subfield code="s">Prog.Part.Nucl.Phys.,65,149</subfield>'
        '  <subfield code="0">857206</subfield>'
        '</datafield>'
    )  # record/863300/export/xme

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/857206',
            },
            'reference': {
                'arxiv_eprint': '1006.1289',
                'publication_info': {
                    'artid': '149',
                    'journal_title': 'Prog.Part.Nucl.Phys.',
                    'journal_volume': '65',
                    'page_start': '149',
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 857206,
            'r': [
                'arXiv:1006.1289',
            ],
            's': 'Prog.Part.Nucl.Phys.,65,149',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_m_o_r_s_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">857215</subfield>'
        '  <subfield code="h">R. C. Myers and A. Sinha</subfield>'
        '  <subfield code="m">Seeing a c-theorem with holography ; [hep-th]</subfield>'
        '  <subfield code="o">10</subfield>'
        '  <subfield code="r">arXiv:1006.1263</subfield>'
        '  <subfield code="s">Phys.Rev.,D82,046006</subfield>'
        '  <subfield code="y">2010</subfield>'
        '</datafield>'
    )  # record/1498589/export/xme

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/857215',
            },
            'reference': {
                'arxiv_eprint': '1006.1263',
                'authors': [
                    {'full_name': u'Myers, R.C.'},
                    {'full_name': u'Sinha, A.'},
                ],
                'label': '10',
                'misc': [
                    'Seeing a c-theorem with holography ; [hep-th]',
                ],
                'publication_info': {
                    'artid': '046006',
                    'journal_title': 'Phys.Rev.',
                    'journal_volume': 'D82',
                    'year': 2010,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 857215,
            'h': [
                'Myers, R.C.',
                'Sinha, A.',
            ],
            'm': [
                'Seeing a c-theorem with holography ; [hep-th]',
            ],
            'o': '10',
            'r': [
                'arXiv:1006.1263',
            ],
            's': 'Phys.Rev.,D82,046006',
            'y': 2010,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5a_h_o_s_x_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="a">doi:10.1142/S0217751X0804055X</subfield>'
        '  <subfield code="h">G.K. Leontaris</subfield>'
        '  <subfield code="o">15</subfield>'
        '  <subfield code="s">Int.J.Mod.Phys.,A23,2055</subfield>'
        '  <subfield code="x">Int. J. Mod. Phys. A 23 (doi:10.1142/S0217751X0804055X)</subfield>'
        '  <subfield code="y">2008</subfield>'
        '  <subfield code="0">780399</subfield>'
        '</datafield>'
    )  # record/1478478/export/xme

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/780399',
            },
            'raw_refs': [
                {
                    'value': 'Int. J. Mod. Phys. A 23 (doi:10.1142/S0217751X0804055X)',
                    'schema': 'text',
                },
            ],
            'reference': {
                'dois': ['10.1142/S0217751X0804055X'],
                'authors': [
                    {'full_name': u'Leontaris, G.K.'},
                ],
                'label': '15',
                'publication_info': {
                    "artid": '2055',
                    'journal_title': 'Int.J.Mod.Phys.',
                    'journal_volume': 'A23',
                    'page_start': '2055',
                    'year': 2008,
                },
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1142/S0217751X0804055X',
            ],
            'h': [
                'Leontaris, G.K.',
            ],
            'o': '15',
            's': 'Int.J.Mod.Phys.,A23,2055',
            'x': [
                'Int. J. Mod. Phys. A 23 (doi:10.1142/S0217751X0804055X)',
            ],
            'y': 2008,
            '0': 780399,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C50_h_m_o_r_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">701721</subfield>'
        '  <subfield code="h">A. Ferrari, P.R. Sala, A. Fasso, and J. Ranft</subfield>'
        '  <subfield code="m">FLUKA: a multi-particle transport code, CERN-10 , INFN/TC_05/11</subfield>'
        '  <subfield code="o">13</subfield>'
        '  <subfield code="r">SLAC-R-773</subfield>'
        '  <subfield code="y">2005</subfield>'
        '</datafield>'
    )  # record/1478478/export/xme

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/701721',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Ferrari, A.'},
                    {'full_name': 'Sala, P.R.'},
                    {'full_name': 'Fasso, A.'},
                    {'full_name': 'Ranft, J.'},
                ],
                'label': '13',
                'misc': [
                    'FLUKA: a multi-particle transport code, CERN-10 , INFN/TC_05/11',
                ],
                'publication_info': {'year': 2005},
                'report_number': 'SLAC-R-773',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 701721,
            'h': [
                'Ferrari, A.',
                'Sala, P.R.',
                'Fasso, A.',
                'Ranft, J.',
            ],
            'm': [
                'FLUKA: a multi-particle transport code, CERN-10 , INFN/TC_05/11',
            ],
            'r': [
                'SLAC-R-773',
            ],
            'o': '13',
            'y': 2005,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


@pytest.mark.xfail(reason='multiple report numbers are not supported')
def test_references_from_999C59_h_m_o_double_r_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="h">Bennett, J</subfield>'
        '  <subfield code="m">Roger J. et al.</subfield>'
        '  <subfield code="o">9</subfield>'
        '  <subfield code="r">CERN-INTC-2004-016</subfield>'
        '  <subfield code="r">CERN-INTCP-186</subfield>'
        '  <subfield code="y">2004</subfield>'
        '</datafield>'
    )  # record/1449990

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'J, Bennett,'},
                ],
                'label': '9',
                'misc': [
                    'Roger J. et al.',
                ],
                'publication_info': {'year': 2004},
                'report_number': [
                    'CERN-INTCP-186',
                    'CERN-INTC-2004-016',
                ],
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'h': [
                'Bennett, J',
            ],
            'r': [
                'CERN-INTCP-186',
                'CERN-INTC-2004-016',
            ],
            'm': 'Roger J.et al.',
            'o': '9',
            'y': 2005,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C50_9_r_u_h_m_o():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="0">1511470</subfield>'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="r">urn:nbn:de:hebis:77-diss-1000009520</subfield>'
        '  <subfield code="u">http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316</subfield>'
        '  <subfield code="h">K. Wiebe</subfield>'
        '  <subfield code="m">Ph.D. thesis, University of Mainz, in preparation</subfield>'
        '  <subfield code="o">51</subfield>'
        '</datafield>'
    )  # record/1504897

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1511470',
            },
            'reference': {
                'authors': [
                    {'full_name': 'Wiebe, K.'},
                ],
                'label': '51',
                'misc': [
                    'Ph.D. thesis, University of Mainz, in preparation',
                ],
                'report_number': 'urn:nbn:de:hebis:77-diss-1000009520',
                'urls': [
                    {'value': 'http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316'},
                ],
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 1511470,
            'h': [
                'Wiebe, K.',
            ],
            'r': [
                'urn:nbn:de:hebis:77-diss-1000009520',
            ],
            'm': [
                'Ph.D. thesis, University of Mainz, in preparation',
            ],
            'o': '51',
            'u': [
                'http://www.diss.fu-berlin.de/diss/receive/FUDISS_thesis_000000094316',
            ],
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_reference_from_999C5t_p_y_e_o():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="t">Higher Transcendetal Functions Vol. I, Bateman Manuscript Project</subfield>'
        '  <subfield code="p">New York: McGraw-Hill Book Company, Inc.</subfield>'
        '  <subfield code="y">1953</subfield>'
        '  <subfield code="e">Erdélyi,A.</subfield>'
        '  <subfield code="o">16</subfield>'
        '</datafield>'
    )  # record/1590099

    expected = [
        {
            'reference': {
                'authors': [
                    {
                        'full_name': u'Erdélyi,A.',
                        'inspire_role': 'editor',
                    },
                ],
                'imprint': {'publisher': 'New York: McGraw-Hill Book Company, Inc.'},
                'label': '16',
                'publication_info': {'year': 1953},
                'title': {'title': 'Higher Transcendetal Functions Vol. I, Bateman Manuscript Project'},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'e': [
                u'Erdélyi,A.',
            ],
            'o': '16',
            'p': 'New York: McGraw-Hill Book Company, Inc.',
            't': 'Higher Transcendetal Functions Vol. I, Bateman Manuscript Project',
            'y': 1953,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_reference_from_999C5o_h_c_t_s_r_y_0():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="o">36</subfield>'
        '  <subfield code="h">S. Chatrchyan et al.</subfield>'
        '  <subfield code="c">CMS Collaboration</subfield>'
        '  <subfield code="t">Angular analysis and branching fraction measurement of the decay B0 → K∗0 µ+ µ-</subfield>'
        '  <subfield code="s">Phys.Lett.,B727,77</subfield>'
        '  <subfield code="r">arXiv:1308.3409 [hep-ex]</subfield>'
        '  <subfield code="y">2013</subfield>'
        '  <subfield code="0">1247976</subfield>'
        '</datafield>'
    )  # record/1591975

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1247976'
            },
            'reference': {
                'arxiv_eprint': '1308.3409',
                'authors': [
                    {'full_name': u'Chatrchyan, S.'}
                ],
                'collaborations': [
                    'CMS Collaboration'
                ],
                'label': '36',
                'publication_info': {
                    'artid': '77',
                    'journal_title': 'Phys.Lett.',
                    'journal_volume': 'B727',
                    'page_start': '77',
                    'year': 2013,
                },
                'title': {'title': u'Angular analysis and branching fraction measurement of the decay B0 → K∗0 µ+ µ-'},
            }
        }
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            '0': 1247976,
            'c': [
                'CMS Collaboration',
            ],
            'h': [
                'Chatrchyan, S.',
            ],
            'o': '36',
            'r': [
                'arXiv:1308.3409',
            ],
            's': 'Phys.Lett.,B727,77',
            't': u'Angular analysis and branching fraction measurement of the decay B0 → K∗0 µ+ µ-',
            'y': 2013,
        }
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5b_h_m_o_p_t_y_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="9">CURATOR</subfield>'
        '  <subfield code="b">C93-06-08</subfield>'
        '  <subfield code="h">C. Gaspar</subfield>'
        '  <subfield code="m">Real Time Conference,, Vancouver, Canada</subfield>'
        '  <subfield code="o">7</subfield>'
        '  <subfield code="p">IEEE</subfield>'
        '  <subfield code="t">DIM - A Distributed Information Management System for the Delphi experiment at CERN</subfield>'
        '  <subfield code="y">1993</subfield>'
        '</datafield>'
    )  # record/1481519

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Gaspar, C.'},
                ],
                'imprint': {'publisher': 'IEEE'},
                'label': '7',
                'misc': [
                    'Real Time Conference,, Vancouver, Canada',
                ],
                'publication_info': {
                    'cnum': 'C93-06-08',
                    'year': 1993,
                },
                'title': {'title': 'DIM - A Distributed Information Management System for the Delphi experiment at CERN'},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'b': 'C93-06-08',
            'h': [
                'Gaspar, C.',
            ],
            'm': [
                'Real Time Conference,, Vancouver, Canada',
            ],
            'o': '7',
            'p': 'IEEE',
            't': 'DIM - A Distributed Information Management System for the Delphi experiment at CERN',
            'y': 1993,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5a_h_i_m_o_p_y_9():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="o">16</subfield>'
        '  <subfield code="h">A. Del Guerra</subfield>'
        '  <subfield code="m">Ionizing Radiation Detectors for Medical Imaging Crossref:</subfield>'
        '  <subfield code="p">World Scientific</subfield>'
        '  <subfield code="i">9812562621</subfield>'
        '  <subfield code="a">doi:10.1142/5408</subfield>'
        '  <subfield code="y">2004</subfield>'
        '  <subfield code="9">refextract</subfield>'
        '</datafield>'
    )  # record/1593684

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Guerra, A.Del'},  # XXX: wrong.
                ],
                'dois': [
                    '10.1142/5408',
                ],
                'imprint': {'publisher': 'World Scientific'},
                'isbn': '9789812562623',
                'label': '16',
                'misc': [
                    'Ionizing Radiation Detectors for Medical Imaging Crossref:',
                ],
                'publication_info': {'year': 2004},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'a': [
                'doi:10.1142/5408',
            ],
            'h': [
                'Guerra, A.Del',  # XXX: wrong
            ],
            'i': '9789812562623',
            'm': [
                'Ionizing Radiation Detectors for Medical Imaging Crossref:',
            ],
            'o': '16',
            'p': 'World Scientific',
            'y': 2004,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']


def test_references_from_999C5h_o_q_t_y():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    snippet = (
        '<datafield tag="999" ind1="C" ind2="5">'
        '  <subfield code="h">Gromov, M.</subfield>'
        '  <subfield code="t">Spaces and questions</subfield>'
        '  <subfield code="y">2000</subfield>'
        '  <subfield code="q">Geom. Funct. Anal., GAFA 2000</subfield>'
        '  <subfield code="o">16</subfield>'
        '</datafield>'
    )  # record/1592189

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'M., Gromov,'},  # XXX: wrong
                ],
                'label': '16',
                'publication_info': {
                    'parent_title': 'Geom. Funct. Anal., GAFA 2000',
                    'year': 2000,
                },
                'title': {'title': 'Spaces and questions'},
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['references'], subschema) is None
    assert expected == result['references']

    expected = [
        {
            'h': [
                'M., Gromov,',  # XXX: wrong
            ],
            'o': '16',
            'q': 'Geom. Funct. Anal., GAFA 2000',
            't': 'Spaces and questions',
            'y': 2000,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['999C5']
