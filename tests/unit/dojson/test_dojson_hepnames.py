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

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hepnames import hepnames2marc, hepnames
from inspirehep.dojson.utils import validate


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
@mock.patch('inspirehep.dojson.hepnames.rules.get_recid_from_ref')
@mock.patch('inspirehep.dojson.hepnames.rules.get_record_ref')
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
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

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
    )  # record/984519

    expected = [
        {
            'schema': 'INSPIRE ID',
            'value': 'INSPIRE-00134135',
        },
        {
            'schema': 'INSPIRE BAI',
            'value': 'H.Vogel.1',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            'a': 'INSPIRE-00134135',
            '9': 'INSPIRE'
        },
        {
            'a': 'H.Vogel.1',
            '9': 'BAI'
        }
    ]
    result = hepnames2marc.do(result)

    assert sorted(expected) == sorted(result['035'])


def test_ids_from_035__a_9_with_orcid():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">ORCID</subfield>'
        '  <subfield code="a">0000-0001-6771-2174</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'schema': 'ORCID',
            'value': '0000-0001-6771-2174',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'ORCID',
            'a': '0000-0001-6771-2174',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_cern():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERN</subfield>'
        '  <subfield code="a">CERN-622961</subfield>'
        '</datafield>'
    )  # record/1064570/export/xme

    expected = [
        {
            'schema': 'CERN',
            'value': 'CERN-622961',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'CERN',
            'a': 'CERN-622961'
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_cern_malformed():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

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
            'schema': 'CERN',
            'value': 'CERN-645257',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-783683',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-724319',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-727986',
        },
        {
            'schema': 'CERN',
            'value': 'CERN-765559',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'CERN',
            'a': 'CERN-645257',
        },
        {
            '9': 'CERN',
            'a': 'CERN-783683',
        },
        {
            '9': 'CERN',
            'a': 'CERN-724319',
        },
        {
            '9': 'CERN',
            'a': 'CERN-727986',
        },
        {
            '9': 'CERN',
            'a': 'CERN-765559',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_desy():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">DESY-1001805</subfield>'
        '  <subfield code="9">DESY</subfield>'
        '</datafield>'
    )  # record/993224/export/xme

    expected = [
        {
            'schema': 'DESY',
            'value': 'DESY-1001805',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'DESY',
            'a': 'DESY-1001805',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_wikipedia():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">Wikipedia</subfield>'
        '  <subfield code="a">Guido_Tonelli</subfield>'
        '</datafield>'
    )  # record/985898/export/xme

    expected = [
        {
            'schema': 'WIKIPEDIA',
            'value': 'Guido_Tonelli',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'WIKIPEDIA',
            'a': 'Guido_Tonelli',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_slac():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-218626</subfield>'
        '</datafield>'
    )  # record/1028379/export/xme

    expected = [
        {
            'schema': 'SLAC',
            'value': 'SLAC-218626',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'SLAC',
            'a': 'SLAC-218626',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_with_bai():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">Jian.Long.Han.1</subfield>'
        '</datafield>'
    )  # record/1464894/export/xme

    expected = [
        {
            'schema': 'INSPIRE BAI',
            'value': 'Jian.Long.Han.1',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'BAI',
            'a': 'Jian.Long.Han.1',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_double_035__a_9_with_kaken():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

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
            'schema': 'INSPIRE BAI',
            'value': 'Toshio.Suzuki.2',
        },
        {
            'schema': 'KAKEN',
            'value': 'KAKEN-70139070',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'BAI',
            'a': 'Toshio.Suzuki.2',
        },
        {
            '9': 'KAKEN',
            'a': 'KAKEN-70139070',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_googlescholar():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">GoogleScholar</subfield>'
        '  <subfield code="a">Tnl-9KoAAAAJ</subfield>'
        '</datafield>'
    )  # record/1467553/export/xme

    expected = [
        {
            'schema': 'GOOGLESCHOLAR',
            'value': 'Tnl-9KoAAAAJ',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'GOOGLESCHOLAR',
            'a': 'Tnl-9KoAAAAJ',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_viaf():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">VIAF</subfield>'
        '  <subfield code="a">34517183</subfield>'
        '</datafield>'
    )  # record/1008109/export/xme

    expected = [
        {
            'schema': 'VIAF',
            'value': '34517183',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'VIAF',
            'a': '34517183',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_researcherid():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">RESEARCHERID</subfield>'
        '  <subfield code="a">B-4717-2008</subfield>'
        '</datafield>'
    )  # record/1051026/export/xme

    expected = [
        {
            'schema': 'RESEARCHERID',
            'value': 'B-4717-2008',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'RESEARCHERID',
            'a': 'B-4717-2008',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


def test_ids_from_035__a_9_with_scopus():
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SCOPUS</subfield>'
        '  <subfield code="a">7103280792</subfield>'
        '</datafield>'
    )  # record/1017182/export/xme

    expected = [
        {
            'schema': 'SCOPUS',
            'value': '7103280792',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['ids'], subschema) is None
    assert expected == result['ids']

    expected = [
        {
            '9': 'SCOPUS',
            'a': '7103280792',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['035']


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
    schema = load_schema('authors')
    subschema = schema['properties']['other_names']

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

    assert validate(result['other_names'], subschema) is None
    assert expected == result['other_names']

    expected = [
        {'a': 'Yosef Cohen, Hadar'},
        {'a': 'Josef Cohen, Hadar'},
        {'a': 'Cohen, Hadar Josef'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['400']


@pytest.mark.xfail(reason='identifiers in i and w are not handled')
def test_advisors_from_701__a_g_i():
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Rivelles, Victor O.</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">INSPIRE-00120420</subfield>'
        '  <subfield code="x">991627</subfield>'
        '  <subfield code="y">1</subfield>'
        '</datafield>'
    )  # record/1474091/export/xme

    expected = [
        {
            'name': 'Rivelles, Victor O.',
            'degree_type': 'PhD',
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00120420'
                }
            ],
            'record': {
                '$ref': 'http://localhost:5000/api/authors/991627',
            },
            'curated_relation': True
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['advisors'], subschema) is None
    assert expected == result['advisors']

    expected = [
        {
            'a': 'Rivelles, Victor O.',
            'g': 'PhD',
            'i': 'INSPIRE-00120420',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['701']


def test_old_single_email_from_371__a():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

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

    assert validate(result['positions'], subschema) is None
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
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

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

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [
        {'a': 'Aachen, Tech. Hochsch.'}
    ]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_positions_from_371__a_double_m_z():
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

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

    assert validate(result['positions'], subschema) is None
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
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

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

    assert validate(result['positions'], subschema) is None
    assert expected == result['positions']

    expected = [
        {
            'a': 'Antwerp U.',
            'm': ['pierre.vanmechelen@ua.ac.be'],
            'r': 'SENIOR',
            'z': 'Current'
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['371']


def test_arxiv_categories_from_65017a_2():
    schema = load_schema('authors')
    subschema = schema['properties']['arxiv_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">HEP-TH</subfield>'
        '</datafield>'
    )  # record/1010819

    expected = [
        'hep-th',
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['arxiv_categories'], subschema) is None
    assert expected == result['arxiv_categories']

    expected = [
        {
            '2': 'arXiv',
            'a': 'hep-th',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2():
    schema = load_schema('authors')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">Computing</subfield>'
        '</datafield>'
    )  # record/1271076

    expected = [
        {'term': 'Computing'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Computing',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_E():
    schema = load_schema('authors')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">E</subfield>'
        '</datafield>'
    )  # record/1019112

    expected = [
        {'term': 'Experiment-HEP'},
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'Experiment-HEP',
        },
    ]
    result = hepnames2marc.do(result)

    assert expected == result['65017']


def test_public_notes_from_667__a():
    schema = load_schema('authors')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<datafield tag="667" ind1=" " ind2=" ">'
        '  <subfield code="a">Do not confuse with Acharya, Bannanje Sripath</subfield>'
        '</datafield>'
    )  # record/1018999

    expected = [
        {'value': 'Do not confuse with Acharya, Bannanje Sripath'}
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {'a': 'Do not confuse with Acharya, Bannanje Sripath'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['667']


def test_private_notes_from_595__a_9():
    schema = load_schema('authors')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="a">Author prefers Alexandrov, A.S.</subfield>'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '</datafield>'
    )  # record/1050484

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Author prefers Alexandrov, A.S.',
        }
    ]
    result = hepnames.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Author prefers Alexandrov, A.S.',
        }
    ]
    result = hepnames2marc.do(result)

    assert expected == result['595']


def test_stub_from_980__a_useful():
    schema = load_schema('authors')
    subschema = schema['properties']['stub']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">USEFUL</subfield>'
        '</datafield>'
    )  # record/1222902

    expected = False
    result = hepnames.do(create_record(snippet))

    assert validate(result['stub'], subschema) is None
    assert expected == result['stub']

    expected = [
        {'a': 'USEFUL'},
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['980']


def test_stub_from_980__a_not_useful():
    schema = load_schema('authors')
    subschema = schema['properties']['stub']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HEPNAMES</subfield>'
        '</datafield>'
    )  # record/1019103

    expected = True
    result = hepnames.do(create_record(snippet))

    assert validate(result['stub'], subschema) is None
    assert expected == result['stub']

    expected = [
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('authors')
    subschema = schema['properties']['deleted']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )  # record/1511071

    expected = True
    result = hepnames.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
        {'a': 'HEPNAMES'},
    ]
    result = hepnames2marc.do(result)

    assert expected == result['980']
