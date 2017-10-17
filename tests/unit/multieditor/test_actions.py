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

from __future__ import absolute_import, print_function, division

import json
import os
import pytest

from inspirehep.modules.multieditor.actions import Addition, Deletion, Update, create_schema_record


@pytest.fixture
def get_schema():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path, 'fixtures/schema.json')) \
            as data_file:
        schema = json.load(data_file)
    return schema


def test_addition_root_key(get_schema):
    """Should test adding a root primitive key"""
    record = {
    }
    expected_map = {
        "preprint_date": "2016"
    }
    add = Addition(keys=['preprint_date'], value="2016")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_missing_root_key(get_schema):
    """Should test adding an object with same condition key"""
    record = {
    }
    expected_map = {
        "_collections": ["Literature"]
    }
    add = Addition(keys=['_collections'], value="Literature",
                   conditions=[{'keys': ["_collections"], 'match_type':"missing"}])
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_missing_deeper_key(get_schema):
    """Should test adding an object with condition on a deep key"""
    record = {
    }
    expected_map = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ]
    }
    add = Addition(keys=['public_notes'], value={"value": "Preliminary results"},
                   conditions=[{'keys': ["public_notes", "value"], 'match_type':"missing"}])
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition(get_schema):
    """Should test adding an object with missing condition key"""
    record = {
        "public_notes": [
            {
                "value": "Preliminary results"
            },
            {
                "value": "test"
            }
        ],
        "core": True,
    }
    expected_map = {
        "public_notes": [
            {
                "value": "Preliminary results"
            },
            {
                "value": "test"
            }
        ],
        "core": True,
        "preprint_date": "2016"
    }
    add = Addition(keys=['preprint_date'],
                   conditions=[{'keys': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keys': ['core'], 'value': True, 'match_type': 'exact'}],
                   value="2016")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition_negative(get_schema):
    """Should test adding an object with negative condition"""
    record = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ],
        "core": True,
        "titles": [
            {
                "title": "test"
            }
        ],
    }
    expected_map = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ],
        "core": True,
        "titles": [
            {
                "title": "test"
            }
        ],
    }
    add = Addition(keys=['preprint_date'],
                   conditions=[{'keys': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keys': ['core'], 'value': False, 'match_type': 'exact'}],
                   match_type='exact',
                   value="2016")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_object_with_condition(get_schema):
    """Should test adding an object with condition"""
    record = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ],
        "core": True,
        "titles": [
            {
                "title": "test"
            }
        ],
    }
    expected_map = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ],
        "core": True,
        "titles": [
            {
                "title": "test",
            },
            {
                "title": "success"
            }
        ],
    }
    add = Addition(keys=['titles'],
                   conditions=[{'keys': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keys': ['core'], 'value': True, 'match_type': 'exact'}],
                   value={'title': "success"})
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_object():
    """should test record addition for object"""
    record = {
        'key_a': {
            'key_c': 'test'
        }
    }
    expected_map = {
        'key_a': {
            'key_b': 'success',
            'key_c': 'test'
        }
    }
    custom_schema = {
        "properties": {
            "key_a": {
                "properties": {
                    "key_b": {
                        "type": "string"
                    },
                    "key_c": {
                        "type": "string"
                    }
                },
                "required": [
                    "value"
                ],
                "type": "object"
            },
            "type": "object",
        },
        "type": "object",
    }
    add = Addition(keys=['key_a', 'key_b'], value="success")
    add.apply_action(record, custom_schema)
    assert record == expected_map


def test_addition_array_with_condition():
    """should test record addition for object using condition check"""
    record = {
        'key_a': {
            'key_b': ['Hello'],
            'key_c': 'test'
        }
    }

    expected_map = {
        'key_a': {
            'key_b': ['Hello', 'World'],
            'key_c': 'test'
        }
    }

    custom_schema = {
        "properties": {
            "key_a": {
                "properties": {
                    "key_b": {
                        "items": {
                            "type": "string"
                        },
                        "type": "array",
                    },
                    "key_c": {
                        "type": "string"
                    }
                },
                "required": [
                    "value"
                ],
                "type": "object"
            },
            "type": "object",
        },
        "type": "object",
    }
    add = Addition(keys=['key_a', 'key_b'],
                   conditions=[{'keys': ['key_a', 'key_c'],
                                'match_type': 'exact',
                                'value':'test'}],
                   value="World")
    add.apply_action(record, custom_schema)
    assert record == expected_map


def test_addition_array(get_schema):
    """should test record addition for nested array"""
    record = {
        "titles": [
            {
                "title": "test"
            },
            {
                "title": "test"
            }
        ],
        "document_type": ["book"]
    }
    expected_map = {
        "titles": [
            {
                "title": "test",
                "subtitle": "success"
            },
            {
                "title": "test",
                "subtitle": "success"
            }
        ],
        "document_type": ["book"]
    }
    add = Addition(keys=['titles', 'subtitle'], value="success")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_array_with_condition_condition(get_schema):
    """should test record addition for nested array"""
    record = {
        "titles": [
            {
                "title": "test_1"
            },
            {
                "title": "test"
            }
        ],
        "document_type": ["book"]
    }
    expected_map = {
        "titles": [
            {
                "title": "test_1",
                "subtitle": "success"
            },
            {
                "title": "test",
                "subtitle": "success"
            }
        ],
        "document_type": ["book"]
    }
    add = Addition(keys=['titles', 'subtitle'],
                   conditions=[{'keys': ['titles', 'title'],
                                'match_type': 'contains',
                                'value':'test'}],
                   value="success")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_array_with_condition_missing_record():
    """should test record addition for nested array"""
    record = {}

    expected_map = {}

    custom_schema = {
        "properties": {
            "key_a": {
                "properties": {
                    "key_b": {
                        "items": {
                            "type": "string"
                        },
                        "type": "array",
                    },
                    "key_c": {
                        "type": "string"
                    }
                },
                "required": [
                    "value"
                ],
                "type": "object"
            },
            "type": "object",
        },
        "type": "object",
    }
    add = Addition(keys=['key_a', 'key_b'],
                   conditions=[{'keys': ['key_a', 'key_c'],
                                'match_type': 'exact',
                                'value':'test'}],
                   value="World")
    add.apply_action(record, custom_schema)
    assert record == expected_map


def test_addition_object_condition(get_schema):
    record = {
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Rome"
                    }
                ],
                "signature_block": "BANARo"
            },
            {
                "affiliations": [
                    {
                        "value": "Rome U."
                    }
                ],
                "signature_block": "MANl",
            }
        ]
    }
    expected_map = {
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Rome"
                    },
                    {
                        "curated_relation": True,
                        "value": "Success"
                    }
                ],
                "signature_block": "BANARo"
            },
            {
                "affiliations": [
                    {
                        "value": "Rome U."
                    }
                ],
                "signature_block": "MANl",
            }
        ]
    }
    add = Addition(keys=['authors', 'affiliations'],
                   conditions=[{'keys': ['authors', 'signature_block'],
                                'match_type': 'exact',
                                'value':'BANARo'}],
                   value={"curated_relation": True,
                          "value": "Success"})
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_deletion_array():
    """should test record deletion for nested array"""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']},
                  {'key_c': ['val6', 'val6']},
                  {'key_c': ['val3']}],
        'key_b': {'key_c': {'key_d': 'val'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1']},
                  {'key_c': ['val3']}],
        'key_b': {'key_c': {'key_d': 'val'}}
    }

    delete = Deletion(value_to_check='val6',
                      keys=['key_a', 'key_c'],
                      match_type='exact')
    delete.apply_action(record)
    assert record == expected_map


def test_deletion_array_contains():
    """should test record deletion for nested array"""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']},
                  {'key_c': ['val4', 'val6']},
                  {'key_c': ['val3']}],
        'key_b': {'key_f': {'key_d': 'val'}}
    }
    expected_map = {
        'key_b': {'key_f': {'key_d': 'val'}}
    }

    delete = Deletion(value_to_check='val',
                      keys=['key_a', 'key_c'],
                      match_type='contains')
    delete.apply_action(record)
    assert record == expected_map


def test_deletion_array_regex():
    """should test record deletion for nested array"""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']},
                  {'key_c': ['val4', 'val6']},
                  {'key_c': ['val3']}],
        'key_b': {'key_f': {'key_d': 'val'}}
    }
    expected_map = {
        'key_b': {'key_f': {'key_d': 'val'}}
    }

    delete = Deletion(value_to_check='va.*',
                      keys=['key_a', 'key_c'],
                      match_type='regex')
    delete.apply_action(record)
    assert record == expected_map


def test_deletion_exact_empty_rec():
    record = {
        'key1': {
            'key2': {
                'key3': 'val'
            }
        }
    }
    expected_map = {}
    delete = Deletion(value_to_check='val',
                      keys=['key1', 'key2', 'key3'],
                      match_type='exact')
    delete.apply_action(record)
    assert record == expected_map


def test_deletion_contains():
    record = {'key': 'val'}
    expected_map = {}
    delete = Deletion(value_to_check='v',
                      keys=['key'],
                      match_type='contains')
    delete.apply_action(record)
    assert record == expected_map


def test_deletion_regex():
    record = {'key': 'val'}
    expected_map = {}
    delete = Deletion(value_to_check='v.*',
                      keys=['key'],
                      match_type='regex')
    delete.apply_action(record)
    assert record == expected_map


def test_record_creation_root_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['corporate_author']
    value = 'success'
    target_object = {'corporate_author': ['success']}
    assert create_schema_record(get_schema, key, value) == target_object


def test_record_creation_root_object(get_schema):
    """should test sub_record creation for missing object"""
    key = ['self', '$ref']
    value = 'success'
    target_object = {'self': {'$ref': 'success'}}
    assert create_schema_record(get_schema, key, value) == target_object


def test_record_creation():
    """should test sub_record creation for missing object"""
    schema_2 = {
        "properties": {
            "source": {
                "type": "string"
            }},
        "type": "object",
    }
    key = ['source']
    value = 'success'
    target_object = {'source': 'success'}
    assert create_schema_record(schema_2, key, value) == target_object


def test_record_creation_complex(get_schema):
    """should test sub_record creation for missing object"""
    key = ['authors', 'affiliations', 'value']
    value = 'success'
    target_object = {'authors': [{'affiliations': [{'value': 'success'}]}]}
    assert create_schema_record(get_schema, key, value) == target_object


def test_record_creation_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['authors']
    value = {'full_name': 'success'}
    target_object = {'authors': [{'full_name': 'success'}]}
    assert create_schema_record(get_schema, key, value) == target_object


def test_update_regex():
    record = {'key': 'val'}
    expected_map = {'key': 'success'}
    update = Update(value_to_check='v.*',
                    value="success",
                    keys=['key'],
                    match_type='regex')
    update.apply_action(record)
    assert record == expected_map


def test_update_contains():
    record = {'key': 'val'}
    expected_map = {'key': 'success'}
    update = Update(value_to_check='v',
                    value="success",
                    keys=['key'],
                    match_type='contains')
    update.apply_action(record)
    assert record == expected_map


def test_record_update_field_not_existing():
    """should test sub_record creation for missing object"""
    record = {'abstracts': [{'not_source': 'success'}]}
    expected_map = {'abstracts': [{'not_source': 'success'}]}
    update = Update(keys=['abstracts', 'source'],
                    value_to_check='success',
                    match_type='exact',
                    value="failure")
    update.apply_action(record)
    assert record == expected_map


def test_update_array_exact():
    """should test record edit for nested complex array."""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['val5', 'success']},
                  {'key_c': ['val1', 'val6']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    update = Update(value_to_check='val4',
                    keys=['key_a', 'key_c'],
                    match_type='exact',
                    value="success")
    update.apply_action(record)
    assert record == expected_map


def test_update_array_contains():
    """should test record edit for nested complex array."""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['success', 'success']},
                  {'key_c': ['success', 'success']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    update = Update(value_to_check='val',
                    keys=['key_a', 'key_c'],
                    match_type='contains',
                    value="success")
    update.apply_action(record)
    assert record == expected_map


def test_update_array_regex():
    """should test record edit for nested complex array."""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['success', 'success']},
                  {'key_c': ['success', 'success']}],
        'key_b': {'key_c': {'key_d': 'dummy'}}
    }
    update = Update(value_to_check='val.*',
                    keys=['key_a', 'key_c'],
                    match_type='regex',
                    value="success")
    update.apply_action(record)
    assert record == expected_map


def test_update_condition_array_regex():
    """should test action for nested complex array and multiple check values"""
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['success', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }

    update = Update(value_to_check='val5',
                    keys=['references', 'reference', 'collaborations'],
                    conditions=[{'keys': ['references', 'reference', 'title', 'title'],
                                'match_type': 'regex',
                                 'value':'tes.*'}],
                    match_type='exact',
                    value="success")
    update.apply_action(record)
    assert record == expected_map


def test_update_with_missing_keys():
    """should test sub_record update handling for missing object"""
    record = {
        "abstracts": [
            {
                "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
            }
        ],
    }
    expected_map = {
        "abstracts": [
            {
                "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
            },
        ],
    }

    update = Update(value_to_check='test',
                    keys=['abstracts', 'source'],
                    value="success",
                    match_type='exact')
    update.apply_action(record)
    assert record == expected_map


def test_update_check_regex_condition():
    record = {
        "document_type": ["book chapter"],
        "texkeys": [
            "Braendas:1972ts"
        ],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "INFN, Rome"
                    },
                    {
                        "value": "Rome"
                    },
                    {
                        "value": "INFN"
                    }
                ],
                "signature_block": "BANARo"
            },
            {"affiliations": [
                {
                    "value": "Rome U."
                },
                {
                    "value": "Not INF"
                }
            ],
                "signature_block": "MANl",
            }
        ]
    }
    expected_map = {
        "document_type": ["book chapter"],
        "texkeys": [
            "Braendas:1972ts"
        ],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Success"
                    },
                    {
                        "value": "Success"
                    },
                    {
                        "value": "INFN"
                    }
                ],
                "signature_block": "BANARo"
            },
            {
                "affiliations": [
                    {
                        "value": "Rome U."
                    },
                    {
                        "value": "Not INF"
                    }
                ],
                "signature_block": "MANl",
            }
        ]
    }
    update = Update(value_to_check='Rome.*',
                    keys=['authors', 'affiliations', 'value'],
                    conditions=[{'keys': ['authors', 'signature_block'],
                                'match_type':'exact',
                                 'value':'BANARo'},
                                {'keys': ['document_type'],
                                 'match_type': 'contains',
                                 'value': 'book'},
                                {'keys': ['texkeys'],
                                 'match_type': 'exact',
                                 'value': 'Braendas:1972ts'}
                                ],
                    match_type='regex',
                    value="Success")
    update.apply_action(record)
    assert record == expected_map


def test_update_for_missing_key():
    record = {
        "document_type": ["book chapter"],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "INFN, Rome"
                    },
                    {
                        "value": "Rome"
                    },
                    {
                        "value": "INFN"
                    }
                ],
                "signature_block": "BANARo"
            },
            {"affiliations": [
                {
                    "value": "Rome U."
                },
                {
                    "value": "Not INF"
                }
            ]
            }
        ]
    }
    expected_map = {
        "document_type": ["book chapter"],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "INFN, Rome"
                    },
                    {
                        "value": "Rome"
                    },
                    {
                        "value": "INFN"
                    }
                ],
                "signature_block": "BANARo"
            },
            {
                "affiliations": [
                    {
                        "value": "Success"
                    },
                    {
                        "value": "Not INF"
                    }
                ]
            }
        ]
    }
    update = Update(value_to_check='Rome U.',
                    keys=['authors', 'affiliations', 'value'],
                    conditions=[{'keys': ['authors', 'signature_block'],
                                'match_type':'missing',
                                 'value':None},
                                {'keys': ['document_type'],
                                 'match_type': 'regex',
                                 'value': 'book.*'},
                                ],
                    match_type='exact',
                    value="Success")
    update.apply_action(record)
    assert record == expected_map
