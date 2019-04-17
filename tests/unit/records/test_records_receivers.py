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

from uuid import UUID
import pytest
import mock

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.receivers import (
    assign_phonetic_block,
    assign_uuid,
)


def test_assign_phonetic_block_handles_ascii_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Ellis, John Richard'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'signature_block': 'ELj',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_handles_unicode_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': u'Páramos, Jorge'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': u'Páramos, Jorge',
            'signature_block': 'PARANj',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_handles_jimmy():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Jimmy'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': 'Jimmy',
            'signature_block': 'JANY',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_handles_two_authors_with_the_same_name():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {
                'full_name': 'Wang, Meng',
                'uuid': '986d27a9-5890-445a-bb35-00f56bea003e',
            },
            {
                'full_name': 'Wang, Meng',
                'uuid': '9b645148-a13c-47e2-9e24-8e9b173e308b',
            },
        ],
    }  # literature/1662077
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': 'Wang, Meng',
            'signature_block': 'WANGm',
            'uuid': '986d27a9-5890-445a-bb35-00f56bea003e',
        },
        {
            'full_name': 'Wang, Meng',
            'signature_block': 'WANGm',
            'uuid': '9b645148-a13c-47e2-9e24-8e9b173e308b',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


@pytest.mark.xfail
def test_assign_phonetic_block_ignores_malformed_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': '** NOT A REAL NAME **'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {'full_name': '** NOT A REAL NAME **'},
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_discards_empty_signature_blocks():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'ae'},
        ],
    }  # record/1422285
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {'full_name': 'ae'},
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.records.receivers.uuid.uuid4')
def test_assign_uuid(mock_uuid4):
    mock_uuid4.return_value = UUID('727238f3-8ed6-40b6-97d2-dc3cd1429131')

    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Ellis, John Richard'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_uuid(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'uuid': '727238f3-8ed6-40b6-97d2-dc3cd1429131',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.records.receivers.uuid.uuid4')
def test_assign_uuid_does_not_touch_existing_uuids(mock_uuid4):
    mock_uuid4.return_value = UUID('727238f3-8ed6-40b6-97d2-dc3cd1429131')

    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {
                'full_name': 'Ellis, John Richard',
                'uuid': 'e14955b0-7e57-41a0-90a8-f4c64eb8f4e9',
            },
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_uuid(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'uuid': 'e14955b0-7e57-41a0-90a8-f4c64eb8f4e9',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result
