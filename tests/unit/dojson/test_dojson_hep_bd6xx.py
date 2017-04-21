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


def test_keywords_from_084__a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="a">02.20.Sv</subfield>'
        '  <subfield code="2">PACS</subfield>'
        '</datafield>'
    )  # record/1590395

    expected = [
        {
            'schema': 'PACS',
            'value': '02.20.Sv',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'PACS',
            'a': '02.20.Sv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['084']
    assert '6531' not in result
    assert '695' not in result


def test_keywords_from_084__a_2_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="084" ind1=" " ind2=" ">'
        '  <subfield code="2">PDG</subfield>'
        '  <subfield code="9">PDG</subfield>'
        '  <subfield code="a">G033M</subfield>'
        '</datafield>'
    )  # record/1421100

    expected = [
        {
            'schema': 'PDG',
            'source': 'PDG',
            'value': 'G033M',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'PDG',
            '9': 'PDG',
            'a': 'G033M',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['084']
    assert '6531' not in result
    assert '695' not in result


def test_keywords_from_6531_a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="2">JACoW</subfield>'
        '  <subfield code="a">experiment</subfield>'
        '</datafield>'
    )  # record/1473380

    expected = [
        {
            'schema': 'JACOW',
            'value': 'experiment',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'JACoW',
            'a': 'experiment',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['6531']
    assert '084' not in result
    assert '695' not in result


def test_keywords_from_6531_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    snippet = (
        '<datafield tag="653" ind1="1" ind2=" ">'
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
    assert 'energy_ranges' not in result

    expected = [
        {
            '9': 'author',
            'a': 'Data',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['6531']
    assert '084' not in result
    assert '695' not in result


def test_keywords_from_6531_a_double_9_ignores_values_from_conference():
    snippet = (
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">submitter</subfield>'
        '  <subfield code="9">conference</subfield>'
        '  <subfield code="a">Track reconstruction</subfield>'
        '</datafield>'
    )  # record/1498175

    result = hep.do(create_record(snippet))

    assert 'energy_ranges' not in result
    assert 'keywords' not in result


def test_keywords_from_6531_9_ignores_lone_sources():
    snippet = (
        '<datafield tag="653" ind1="1" ind2=" ">'
        '  <subfield code="9">author</subfield>'
        '</datafield>'
    )  # record/1382933

    result = hep.do(create_record(snippet))

    assert 'energy_ranges' not in result
    assert 'keywords' not in result


def test_keywords2marc_does_not_export_magpie_keywords():
    record = {
        'keywords': [
            {
                'source': 'magpie',
                'value': 'cosmological model',
            },
        ],
    }

    result = hep2marc.do(record)

    assert '084' not in result
    assert '6531' not in result
    assert '695' not in result


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
    assert 'energy_ranges' not in result

    expected = [
        {
            '2': 'INSPIRE',
            'a': 'REVIEW',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


def test_energy_ranges_from_695__e_2():
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
    assert 'keywords' not in result

    expected = [
        {
            '2': 'INSPIRE',
            'e': 7,
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['695']
    assert '084' not in result
    assert '6531' not in result


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
    assert 'energy_ranges' not in result

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
    assert '084' not in result
    assert '6531' not in result
