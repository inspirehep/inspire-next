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

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_accelerator_experiments_from_693__a_e():
    schema = load_schema('hep')
    subschema = schema['properties']['accelerator_experiments']

    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN LHC</subfield>'
        '  <subfield code="e">CERN-LHC-CMS</subfield>'
        '  <subfield code="0">1108642</subfield>'
        '</datafield>'
    )  # record/1517829/export/xme

    expected = [
        {
            'legacy_name': 'CERN-LHC-CMS',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108642',
            },
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['accelerator_experiments'], subschema) is None
    assert expected == result['accelerator_experiments']

    expected = [
        {'e': 'CERN-LHC-CMS'},
    ]
    result = hep2marc.do(result)

    assert expected == result['693']


def test_keywords_from_695__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="695" ind1=" " ind2=" ">'
        '  <subfield code="a">REVIEW</subfield>'
        '  <subfield code="2">INSPIRE</subfield>'
        '</datafield>'
    )  # record/200123

    expected = [
        {
            'value': 'REVIEW',
            'schema': 'INSPIRE',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']

    expected = [
        {
            'a': 'REVIEW',
            '2': 'INSPIRE',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']


def test_energy_ranges_from_695__2_e():
    schema = load_schema('hep')
    subschema = schema['properties']['energy_ranges']

    snippet = (
        '<datafield tag="695" ind1=" " ind2=" ">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="e">7</subfield>'
        '</datafield>'
    )  # record/1124337

    expected = [7]
    result = hep.do(create_record(snippet))

    assert validate(result['energy_ranges'], subschema) is None
    assert expected == result['energy_ranges']

    expected = [
        {
            '2': 'INSPIRE',
            'e': 7,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']


def test_keywords_from_multiple_695__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<record>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="a">programming: Monte Carlo</subfield>'
        '    <subfield code="2">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="695" ind1=" " ind2=" ">'
        '    <subfield code="a">electron positron: annihilation</subfield>'
        '    <subfield code="2">INSPIRE</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/363605

    expected = [
        {
            'schema': 'INSPIRE',
            'value': 'programming: Monte Carlo',
        },
        {
            'schema': 'INSPIRE',
            'value': 'electron positron: annihilation',
        },
    ]

    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']

    expected = [
        {
            'a': 'programming: Monte Carlo',
            '2': 'INSPIRE',
        },
        {
            'a': 'electron positron: annihilation',
            '2': 'INSPIRE',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']


def test_keywords_from_653__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="653" ind1=" " ind2=" ">'
        '  <subfield code="9">author</subfield>'
        '  <subfield code="a">Data</subfield>'
        '</datafield>'
    )  # record/1260876

    expected = [
        {
            'source': 'author',
            'value': 'Data',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']

    expected = [
        {
            '9': 'author',
            'a': 'Data',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['653']
