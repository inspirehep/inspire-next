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

from inspirehep.dojson.hep import hep, hep2marc


ACCELERATOR_EXPERIMENTS_DATA = [
    (
        'single_noncurated',
        """
        <datafield tag="693" ind1=" " ind2=" ">
          <subfield code="e">CERN-LHC-ATLAS</subfield>
          <subfield code="a">LHC</subfield>
        </datafield>
        """,
        [
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS',
            }
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
            },
        ],
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
                'experiment': 'CERN-LHC-ATLAS',
            },
            {
                'accelerator': 'LHC2',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2',
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
            },
            {
                'a': 'LHC2',
                'e': 'CERN-LHC-ATLAS2',
            },
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
                'experiment': 'CERN-LHC-ATLAS',
            },
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2',
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
            },
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS2',
            },
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
        [
            {
                'record': 'mocked_record_1',
                'accelerator': 'LHC',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS',
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
                '0': 1,
            },
        ],
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
                'experiment': 'CERN-LHC-ATLAS',
            },
            {
                'record': 'mocked_record_2',
                'accelerator': 'LHC2',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS2',
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
                '0': 1,
            },
            {
                'a': 'LHC2',
                'e': 'CERN-LHC-ATLAS2',
                '0': 2,
            },
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
                'experiment': 'CERN-LHC-ATLAS',
            },
            {
                'record': 'mocked_record_2',
                'accelerator': 'LHC',
                'curated_relation': True,
                'experiment': 'CERN-LHC-ATLAS2',
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
                '0': 1,
            },
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS2',
                '0': 2,
            },
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
            },
            {
                'accelerator': 'LHC',
                'curated_relation': False,
                'experiment': 'CERN-LHC-ATLAS2'
            },
        ],
        [
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS',
            },
            {
                'a': 'LHC',
                'e': 'CERN-LHC-ATLAS2',
            },
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
    mock_get_record_ref.side_effect = lambda x, *_: x and 'mocked_record_%s' % x
    mock_get_recid_from_ref.side_effect = lambda x, *_:  x and int(x.rsplit('_')[-1])

    if not xml_snippet.strip().startswith('<record>'):
        xml_snippet = '<record>%s</record>' % xml_snippet

    json_data = hep.do(create_record(xml_snippet))
    json_experiments = json_data['accelerator_experiments']
    marc_experiments = hep2marc.do(json_data)['693']

    assert marc_experiments == expected_marc
    assert json_experiments == expected_json
