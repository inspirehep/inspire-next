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
    record = {
    }
    expected_map = {
        "preprint_date": "2016"
    }
    add = Addition(keys=['preprint_date'], where_keys=[], where_regex=False,
                   where_values=[], value="2016")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_where(get_schema):
    record = {
        "public_notes": [
            {
                "value": "Preliminary results"
            },
            {
                "value": "test"
            }
        ],
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
        "preprint_date": "2016"
    }
    add = Addition(keys=['preprint_date'], where_keys=['public_notes', 'value'], where_regex=False,
                   where_values=['test'], value="2016")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_where_negative(get_schema):
    record = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ],
    }
    expected_map = {
        "public_notes": [
            {
                "value": "Preliminary results"
            }
        ]
    }
    add = Addition(keys=['preprint_date'], where_keys=['public_notes', 'value'], where_regex=False,
                   where_values=['test'], value="2016")
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
    add = Addition(keys=['key_a', 'key_b'], where_keys=[], where_regex=False,
                   where_values=[], value="success")
    add.apply_action(record, custom_schema)
    assert record == expected_map


def test_addition_object_with_where():
    """should test record addition for object using where check"""
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
    add = Addition(keys=['key_a', 'key_b'], where_keys=['key_a', 'key_c'], where_regex=False,
                   where_values=['test'], value="World")
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
    add = Addition(keys=['titles', 'subtitle'], where_keys=[], where_regex=False,
                   where_values=[], value="success")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_array_with_where_regex(get_schema):
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
    add = Addition(keys=['titles', 'subtitle'], where_keys=['titles', 'title'],
                   where_regex=True,
                   where_values=['test'], value="success")
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_array_with_where_missing_record():
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
    add = Addition(keys=['key_a', 'key_b'], where_keys=['key_a', 'key_c'], where_regex=False,
                   where_values=['test'], value="World")
    add.apply_action(record, custom_schema)
    assert record == expected_map


def test_addition_object_where(get_schema):
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
    add = Addition(keys=['authors', 'affiliations'], where_keys=['authors', 'signature_block'], where_regex=False,
                   where_values=['BANARo'], value={
        "curated_relation": True,
        "value": "Success"
    })
    add.apply_action(record, get_schema)
    assert record == expected_map


def test_addition_where_missing_key(get_schema):
    record = {
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Rome"
                    },
                    {
                        "value": "Rome U."
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
    expected_map = {
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
    update = Update(values_to_check=['Rome'], keys=['authors', 'affiliations', 'value'], where_keys=['authors', 'signature_block'], where_regex=False,
                    where_values=['BANARo'], values_to_check_regex=True, value="Success")
    update.apply_action(record, get_schema)
    assert record == expected_map


def test_deletion_array():
    """should test record deletion for nested array"""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']},
                  {'key_c': ['val4', 'val6']},
                  {'key_c': ['val3']}],
        'key_b': {'key_c': {'key_d': 'val'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val4']},
                  {'key_c': ['val3']}],
        'key_b': {'key_c': {'key_d': 'val'}}
    }

    delete = Deletion(values_to_check=["val6", "val1"], keys=['key_a', 'key_c'], where_keys=[], where_regex=False,
                      where_values=[], values_to_check_regex=False, value="")
    delete.apply_action(record, {})
    assert record == expected_map


def test_deletion_array_regex():
    """should test record deletion for nested array"""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']},
                  {'key_c': ['val1', 'val6']},
                  {'key_c': ['val4', 'val6']},
                  {'key_c': ['val3']}],
        'key_b': {'key_c': {'key_d': 'val'}}
    }
    expected_map = {
        'key_b': {'key_c': {'key_d': 'val'}}
    }

    delete = Deletion(values_to_check=["val"], keys=['key_a', 'key_c'], where_keys=[], where_regex=False,
                      where_values=[], values_to_check_regex=True, value="")
    delete.apply_action(record, {})
    assert record == expected_map


def test_deletion_empty_rec():
    record = {
        'key1': {
            'key2': {
                'key3': 'val'
            }
        }
    }
    expected_map = {}
    delete = Deletion(values_to_check=['val'], keys=['key1', 'key2', 'key3'], where_keys=[], where_regex=False,
                      where_values=[], values_to_check_regex=False, value="")
    delete.apply_action(record, {})
    assert record == expected_map


def test_update_array():
    """should test record edit for nested complex array."""
    record = {
        'key_a': [{'key_c': ['val5', 'val4']}, {'key_c': ['val1', 'val6']},
                  {'key_c': ['val2']}, {'key_c': ['val3']}], 'key_b': {'key_c': {'key_d': 'pong'}}
    }
    expected_map = {
        'key_a': [{'key_c': ['val5', 'success']}, {'key_c': ['val1', 'val6']},
                  {'key_c': ['val2']}, {'key_c': ['val3']}], 'key_b': {'key_c': {'key_d': 'pong'}}
    }
    update = Update(values_to_check=["val4"], keys=['key_a', 'key_c'], where_keys=[], where_regex=False,
                    where_values=[], values_to_check_regex=False, value="success")
    update.apply_action(record, {})
    assert record == expected_map


def test_update_regex_array():
    """should test action for nested complex array and multiple check values"""
    record = {
        'key_a': [{'key_c': ['val5', 'tes4']}, {'key_c': ['val1', 'val6']},
                  {'key_c': ['tes2']}, {'key_c': ['val3']}], 'key_b': {'key_c': ['not']}
    }
    expected_map = {
        'key_a': [{'key_c': ['success', 'success']}, {'key_c': ['success', 'success']},
                  {'key_c': ['success']}, {'key_c': ['success']}], 'key_b': {'key_c': ['not']}
    }

    update = Update(values_to_check=["val", "tes"], keys=['key_a', 'key_c'], where_keys=[], where_regex=False,
                    where_values=[], values_to_check_regex=True, value="success")
    update.apply_action(record, {})
    assert record == expected_map


def test_update_where_array_regex():
    """should test action for nested complex array and multiple check values"""
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['success', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }

    update = Update(values_to_check=['val'], keys=['references', 'reference', 'collaborations'],
                    where_keys=['references', 'reference', 'title', 'title'], where_regex=False,
                    where_values=['test'], values_to_check_regex=True, value="success")
    update.apply_action(record, {})
    assert record == expected_map


def test_record_creation_field_not_existing():
    """should test sub_record creation for missing object"""
    record = {'abstracts': [{'not_source': 'success'}]}
    expected_map = {'abstracts': [{'not_source': 'success'}]}
    update = Update(values_to_check=[], keys=['abstracts', 'source'], where_keys=[], where_regex=False,
                    where_values=[], values_to_check_regex=False, value="success")
    update.apply_action(record, {})
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


def test_record_creation_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['authors']
    value = {'full_name': 'success'}
    target_object = {'authors': [{'full_name': 'success'}]}
    assert create_schema_record(get_schema, key, value) == target_object


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

    update = Update(values_to_check=[], keys=['abstracts', 'source'], where_keys=[], where_regex=False,
                    where_values=[], values_to_check_regex=False, value="success")
    update.apply_action(record, {})
    assert record == expected_map


def test_record_values_to_check_regex_where(get_schema):
    record = {
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
    update = Update(values_to_check=['Rome'], keys=['authors', 'affiliations', 'value'], where_keys=['authors', 'signature_block'], where_regex=False,
                    where_values=['BANARo'], values_to_check_regex=True, value="Success")
    update.apply_action(record, get_schema)
    assert record == expected_map
