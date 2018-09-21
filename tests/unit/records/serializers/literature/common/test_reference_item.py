# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
from inspire_schemas.api import load_schema, validate

import json
import mock

from inspirehep.modules.records.serializers.schemas.json.literature.common import ReferenceItemSchemaV1


def test_returns_non_empty_fields():
    schema = ReferenceItemSchemaV1()
    dump = {
        'reference': {
            'label': '123',
            'authors': [
                {
                    'full_name': 'Jessica, Jones',
                },
            ],
            'publication_info': {
                'journal_title': 'Alias Investigations',
            },
            'title': {
                'title': 'Jessica Jones',
            },
            'arxiv_eprint': '1207.7214',
            'dois': [
                '10.1016/j.physletb.2012.08.020',
            ],
            'urls': [
                {
                    'value': 'http://www.claymath.org/prize-problems',
                },
                {
                    'value': 'http://www.arthurjaffe.com',
                },
            ],
        }
    }
    expected = {
        'label': '123',
        'authors': [
            {
                'first_name': 'Jones',
                'full_name': 'Jessica, Jones',
                'last_name': 'Jessica'
            }
        ],
        'publication_info': [{
            'journal_title': 'Alias Investigations',
        }],
        'titles': [
            {
                'title': 'Jessica Jones'
            }
        ],
        'arxiv_eprint': [
            {
                'value': '1207.7214',
            }
        ],
        'dois': [
            {
                'value': '10.1016/j.physletb.2012.08.020',
            },
        ],
        'urls': [
            {
                'value': 'http://www.claymath.org/prize-problems',
            },
            {
                'value': 'http://www.arthurjaffe.com',
            },
        ],
    }

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_returns_empty_if_no_reference_or_record_field():
    schema = ReferenceItemSchemaV1()
    dump = {}
    expected = {}

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_returns_empty_if_empty_reference_or_record_field():
    schema = ReferenceItemSchemaV1()
    dump = {
        'record': {},
        'reference': {}
    }
    expected = {}

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_returns_non_empty_fields_if_some_fields_missing():
    schema = ReferenceItemSchemaV1()
    dump = {
        'reference': {
            'label': '123',
            'control_number': 123,
        },
    }
    expected = {
        'label': '123',
        'control_number': 123,
    }

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_returns_no_misc_if_title_persent():
    hep_schema = load_schema('hep')
    subschema = hep_schema['properties']['references']
    schema = ReferenceItemSchemaV1()
    dump = {
        'reference': {
            'title': {
                'title': 'Jessica Jones',
            },
            'misc': [
                'A Misc',
            ]
        }
    }
    expected = {
        'titles': [
            {
                'title': 'Jessica Jones'
            }
        ]
    }

    assert validate([dump], subschema) is None

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.common.reference_item.get_linked_records_in_field')
def test_returns_no_misc_if_titles_persent_in_the_resolved_record(record):
    record.return_value = [{
        'control_number': 123,
        'titles': [
            {
                'source': 'arXiv',
                'title': 'Theoretical limit of residual amplitude modulation in electro-optic modulators'
            },
            {
                'source': 'arXiv',
                'title': 'Fundamental level of residual amplitude modulation in phase modulation processes'
            },
        ],
    }]

    hep_schema = load_schema('hep')
    subschema = hep_schema['properties']['references']
    schema = ReferenceItemSchemaV1()
    dump = {
        'record': {
            '$ref': 'http://localhost:5000/api/literature/123',
        },
        'reference': {
            'label': '123',
            'misc': [
                'A misc',
            ]
        }
    }
    assert validate([dump], subschema) is None

    result = schema.dumps(dump).data
    assert 'misc' not in json.loads(result)


def test_returns_only_first_misc():
    hep_schema = load_schema('hep')
    subschema = hep_schema['properties']['references']
    schema = ReferenceItemSchemaV1()

    dump = {
        'reference': {
            'label': '123',
            'misc': [
                'A Misc',
                'Another Misc',
            ]
        }
    }

    expected = {
        'label': '123',
        'misc': 'A Misc',
    }
    assert validate([dump], subschema) is None

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.common.reference_item.get_linked_records_in_field')
def test_returns_dois_from_the_resolved_record(record):
    record.return_value = [{
        'control_number': 123,
        'dois': [
            {
                'value': '10.1103/PhysRevD.94.054021',
            },
        ],
    }]

    hep_schema = load_schema('hep')
    subschema = hep_schema['properties']['references']
    schema = ReferenceItemSchemaV1()
    dump = {
        'record': {
            '$ref': 'http://localhost:5000/api/literature/123',
        }
    }
    assert validate([dump], subschema) is None

    expected = {
        'control_number': 123,
        'dois': [
            {
                'value': '10.1103/PhysRevD.94.054021',
            },
        ],
    }
    result = schema.dumps(dump).data
    assert expected == json.loads(result)


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.common.reference_item.get_linked_records_in_field')
def test_returns_arxiv_eprints_from_the_resolved_record(record):
    record.return_value = [{
        'control_number': 123,
        'arxiv_eprints': [
            {
                'value': '1606.09129',
                'categories': 'hep',
            },
        ]
    }]

    hep_schema = load_schema('hep')
    subschema = hep_schema['properties']['references']
    schema = ReferenceItemSchemaV1()
    dump = {
        'record': {
            '$ref': 'http://localhost:5000/api/literature/123',
        }
    }
    assert validate([dump], subschema) is None

    expected = {
        'control_number': 123,
        'arxiv_eprint': [
            {
                'value': '1606.09129'
            }
        ]
    }
    result = schema.dumps(dump).data
    assert expected == json.loads(result)
