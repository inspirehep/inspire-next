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

import mock
import pytest

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hepnames import hepnames2marc, hepnames


EXPERIMENTS_DATA = [
    [
        'current_curated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2020</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">00001</subfield>
            <subfield code="s">2014</subfield>
            <subfield code="z">current</subfield>
        </datafield>
        ''',
        [{
            'curated_relation': True,
            'current': True,
            'end_year': 2020,
            'name': 'CERN-ALPHA',
            'record': 'mocked_recid_00001',
            'start_year': 2014,
        }],
        [{
            '0': 1,
            'd': 2020,
            'e': 'CERN-ALPHA',
            's': 2014,
            'z': 'current',
        }],
    ],
    [
        'notcurrent_curated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">SDSS</subfield>
            <subfield code="0">00003</subfield>
        </datafield>
        ''',
        [{
            'curated_relation': True,
            'current': False,
            'name': 'SDSS',
            'record': 'mocked_recid_00003',
        }],
        [{
            '0': 3,
            'e': 'SDSS',
        }],
    ],
    [
        'notcurrent_notcurated',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="e">NOTCURATED</subfield>
        </datafield>
        ''',
        [{
            'name': 'NOTCURATED',
            'curated_relation': False,
            'current': False,
        }],
        [{
            'e': 'NOTCURATED',
        }],
    ],
    [
        'repeated_experiment',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2020</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">00001</subfield>
            <subfield code="s">2014</subfield>
            <subfield code="z">current</subfield>
        </datafield>
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2012</subfield>
            <subfield code="e">CERN-ALPHA</subfield>
            <subfield code="0">00001</subfield>
            <subfield code="s">2010</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': True,
                'end_year': 2020,
                'name': 'CERN-ALPHA',
                'record': 'mocked_recid_00001',
                'start_year': 2014,
            },
            {
                'curated_relation': True,
                'current': False,
                'end_year': 2012,
                'name': 'CERN-ALPHA',
                'record': 'mocked_recid_00001',
                'start_year': 2010,
            },
        ],
        [
            {
                '0': 1,
                'd': 2020,
                'e': 'CERN-ALPHA',
                's': 2014,
                'z': 'current',
            },
            {
                '0': 1,
                'd': 2012,
                'e': 'CERN-ALPHA',
                's': 2010,
            },
        ],
    ],
    [
        'simultaneous_experiments',
        '''
        <datafield tag="693" ind1=" " ind2=" ">
            <subfield code="d">2013</subfield>
            <subfield code="e">FIRST-SIMULTANEOUS</subfield>
            <subfield code="e">SECOND-SIMULTANEOUS</subfield>
            <subfield code="0">00001</subfield>
            <subfield code="0">00002</subfield>
            <subfield code="s">2015</subfield>
        </datafield>
        ''',
        [
            {
                'curated_relation': True,
                'current': False,
                'end_year': 2013,
                'name': 'FIRST-SIMULTANEOUS',
                'record': 'mocked_recid_00001',
                'start_year': 2015,
            },
            {
                'curated_relation': True,
                'current': False,
                'end_year': 2013,
                'name': 'SECOND-SIMULTANEOUS',
                'record': 'mocked_recid_00002',
                'start_year': 2015
            },
        ],
        [
            {
                '0': 1,
                'd': 2013,
                'e': 'FIRST-SIMULTANEOUS',
                's': 2015,
            },
            {
                '0': 2,
                'd': 2013,
                'e': 'SECOND-SIMULTANEOUS',
                's': 2015,
            },
        ],
    ],
]


@pytest.mark.parametrize(
    'test_name,xml_snippet,expected_json,expected_marc',
    EXPERIMENTS_DATA,
    ids=[test_data[0] for test_data in EXPERIMENTS_DATA],
)
@mock.patch('inspirehep.dojson.hepnames.fields.bd1xx.get_recid_from_ref')
@mock.patch('inspirehep.dojson.hepnames.fields.bd1xx.get_record_ref')
def test_experiments(mock_get_record_ref, mock_get_recid_from_ref, test_name,
                     xml_snippet, expected_json, expected_marc):
    mock_get_record_ref.side_effect = \
        lambda x, *_: x and 'mocked_recid_%s' % x
    mock_get_recid_from_ref.side_effect = \
        lambda x, *_: x and int(x.rsplit('_')[-1])

    if not xml_snippet.strip().startswith('<record>'):
        xml_snippet = '<record>%s</record>' % xml_snippet

    json_data = hepnames.do(create_record(xml_snippet))
    json_experiments = json_data['experiments']
    marc_experiments = hepnames2marc.do(json_data)['693']

    assert marc_experiments == expected_marc
    assert json_experiments == expected_json


def test_ids_from_double_035__a_9():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">INSPIRE-00134135</subfield>'
        '    <subfield code="9">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">H.Vogel.1</subfield>'
        '    <subfield code="9">BAI</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'type': 'INSPIRE ID',
            'value': 'INSPIRE-00134135',
        },
        {
            'type': 'INSPIRE BAI',
            'value': 'H.Vogel.1',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_orcid():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">ORCID</subfield>'
        '  <subfield code="a">0000-0001-6771-2174</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'type': 'ORCID',
            'value': '0000-0001-6771-2174',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_cern():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERN</subfield>'
        '  <subfield code="a">CERN-622961</subfield>'
        '</datafield>'
    )  # record/1064570/export/xme

    expected = [
        {
            'type': 'CERN',
            'value': 'CERN-622961',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_cern_malformed():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERN-CERN-645257</subfield>'
        '  </datafield>'  # record/1030771/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">cern-783683</subfield>'
        '  </datafield>'  # record/1408145/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERM-724319</subfield>'
        '  </datafield>'  # record/1244430/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CNER-727986</subfield>'
        '  </datafield>'  # record/1068077/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CVERN-765559</subfield>'
        '  </datafield>'  # record/1340631/export/xme
        '</record>'
    )

    expected = [
        {
            'type': 'CERN',
            'value': 'CERN-645257',
        },
        {
            'type': 'CERN',
            'value': 'CERN-783683',
        },
        {
            'type': 'CERN',
            'value': 'CERN-724319',
        },
        {
            'type': 'CERN',
            'value': 'CERN-727986',
        },
        {
            'type': 'CERN',
            'value': 'CERN-765559',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_desy():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">DESY-1001805</subfield>'
        '  <subfield code="9">DESY</subfield>'
        '</datafield>'
    )  # record/993224/export/xme

    expected = [
        {
            'type': 'DESY',
            'value': 'DESY-1001805',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_wikipedia():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">Wikipedia</subfield>'
        '  <subfield code="a">Guido_Tonelli</subfield>'
        '</datafield>'
    )  # record/985898/export/xme

    expected = [
        {
            'type': 'WIKIPEDIA',
            'value': 'Guido_Tonelli',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_slac():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-218626</subfield>'
        '</datafield>'
    )  # record/1028379/export/xme

    expected = [
        {
            'type': 'SLAC',
            'value': 'SLAC-218626',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_with_bai():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">Jian.Long.Han.1</subfield>'
        '</datafield>'
    )  # record/1464894/export/xme

    expected = [
        {
            'type': 'INSPIRE BAI',
            'value': 'Jian.Long.Han.1',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_double_035__a_9_with_kaken():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">BAI</subfield>'
        '    <subfield code="a">Toshio.Suzuki.2</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">KAKEN</subfield>'
        '    <subfield code="a">70139070</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1474271/export/xme

    expected = [
        {
            'type': 'INSPIRE BAI',
            'value': 'Toshio.Suzuki.2',
        },
        {
            'type': 'KAKEN',
            'value': 'KAKEN-70139070',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_googlescholar():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">GoogleScholar</subfield>'
        '  <subfield code="a">Tnl-9KoAAAAJ</subfield>'
        '</datafield>'
    )  # record/1467553/export/xme

    expected = [
        {
            'type': 'GOOGLESCHOLAR',
            'value': 'Tnl-9KoAAAAJ',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_viaf():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">VIAF</subfield>'
        '  <subfield code="a">34517183</subfield>'
        '</datafield>'
    )  # record/1008109/export/xme

    expected = [
        {
            'type': 'VIAF',
            'value': '34517183',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_researcherid():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">RESEARCHERID</subfield>'
        '  <subfield code="a">B-4717-2008</subfield>'
        '</datafield>'
    )  # record/1051026/export/xme

    expected = [
        {
            'type': 'RESEARCHERID',
            'value': 'B-4717-2008',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_scopus():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SCOPUS</subfield>'
        '  <subfield code="a">7103280792</subfield>'
        '</datafield>'
    )  # record/1017182/export/xme

    expected = [
        {
            'type': 'SCOPUS',
            'value': '7103280792',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['ids']


def test_ids_from_035__9():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">INSPIRE</subfield>'
        '  </datafield>'  # record/edit/?ln=en#state=edit&recid=1474355&recrev=20160707223728
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '  </datafield>'  # record/1364570/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">KAKEN</subfield>'
        '  </datafield>'  # record/1480252/export/xme
        '</record>'
    )

    result = hepnames.do(create_record(snippet))

    assert 'ids' not in result


def test_other_names_from_400__triple_a():
    snippet = (
        '<datafield tag="400" ind1=" " ind2=" ">'
        '  <subfield code="a">Yosef Cohen, Hadar</subfield>'
        '  <subfield code="a">Josef Cohen, Hadar</subfield>'
        '  <subfield code="a">Cohen, Hadar Josef</subfield>'
        '</datafield>'
    )  # record/1292399/export/xme

    expected = [
        'Yosef Cohen, Hadar',
        'Josef Cohen, Hadar',
        'Cohen, Hadar Josef',
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['other_names']


def test_advisors_from_701__a_g_i():
    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Rivelles, Victor O.</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">INSPIRE-00120420</subfield>'
        '  <subfield code="x">991627</subfield>'
        '  <subfield code="y">1</subfield>'
        '</datafield>'
    )  # record/1474091

    expected = [
        {
            'name': 'Rivelles, Victor O.',
            'degree_type': 'PhD',
            '_degree_type': 'PhD',
            'record': {
                '$ref': 'http://localhost:5000/api/authors/991627',
            },
            'curated_relation': True
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['advisors']


def test_old_single_email_from_371__a():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '   <subfield code="a">IMSc, Chennai</subfield>'
        '   <subfield code="o">test@imsc.res.in</subfield>'
        '   <subfield code="r">PD</subfield>'
        '   <subfield code="s">2012</subfield>'
        '   <subfield code="t">2013</subfield>'
        '</datafield>'
    )  # record/1060782

    expected = [
        {
          "current": False,
          "old_emails": [
            "test@imsc.res.in"
          ],
          "end_date": "2013",
          "rank": "POSTDOC",
          "institution": {
            "name": "IMSc, Chennai",
            "curated_relation": False
          },
          "_rank": "PD",
          "start_date": "2012"
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['positions']

    expected = [
        {
          "a": "IMSc, Chennai",
          "o": [
            "test@imsc.res.in"
          ],
          "s": "2012",
          "r": "PD",
          "t": "2013"
        }
    ]

    marc = hepnames2marc.do(result)

    assert expected == marc['371']


def test_positions_from_371__a():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Aachen, Tech. Hochsch.</subfield>'
        '</datafield>'
    )  # record/997958

    expected = [
        {
            'current': False,
            'institution': {
                'curated_relation': False,
                'name': 'Aachen, Tech. Hochsch.',
            },
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['positions']


def test_positions_from_371__a_double_m_z():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Argonne</subfield>'
        '  <subfield code="m">rcyoung@anl.gov</subfield>'
        '  <subfield code="m">rcyoung@hep.anl.gov</subfield>'
        '  <subfield code="z">current</subfield>'
        '</datafield>'
    )  # record/1408378

    expected = [
        {
            'current': True,
            'emails': [
                'rcyoung@anl.gov',
                'rcyoung@hep.anl.gov',
            ],
            'institution': {
                'curated_relation': False,
                'name': 'Argonne',
            },
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['positions']

    expected = [
        {
            'a': 'Argonne',
            'm': ['rcyoung@anl.gov', 'rcyoung@hep.anl.gov'],
            'z': 'Current'
        }
    ]

    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_m_r_z():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Antwerp U.</subfield>'
        '  <subfield code="m">pierre.vanmechelen@ua.ac.be</subfield>'
        '  <subfield code="r">SENIOR</subfield>'
        '  <subfield code="z">Current</subfield>'
        '</datafield>'
    )  # record/997958

    expected = [
        {
            'current': True,
            'emails': [
                'pierre.vanmechelen@ua.ac.be',
            ],
            'institution': {
                'curated_relation': False,
                'name': 'Antwerp U.',
            },
            'rank': 'SENIOR',
            '_rank': 'SENIOR',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['positions']
