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
from collections import namedtuple

from inspirehep.modules.multieditor import actions

schema_1 = {
  "properties": {
      "abstracts": {
        "description": ":MARC: ``520``",
        "items": {
          "additionalProperties": 'false',
          "description": "This is used to add, besides the `value`, the `source`\
                          where this value\ncame from.",
          "properties": {
            "source": {
              "$schema": "http://json-schema.org/schema#",
              "description": "Source of the information in this field.\
                              As several records can be merged,\nthis\
                              information allows us to remember where every\
                              bit of metadata came\nfrom and make\
                              decisions based on it.\n\n:MARC:\
                              Often not present.",
              "type": "string"
            },
            "value": {
              "type": "string"
            }
          },
          "required": [
            "value"
          ],
          "type": "object"
        },
        "title": "List of abstracts",
        "type": "array",
        "uniqueItems": 'true'
      }},
  "type": "object",
}

Action = namedtuple('Action', 'keys, selected_action, value, values_to_check, regex, where_keys,where_value')


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
    actions_tuple = Action(values_to_check=["val4"], keys=['key_a', 'key_c'], where_keys=[], selected_action="Update",
                           where_value="", regex=False, value="success")

    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_update_multiple_update_array():
    """should test action for nested complex array and multiple check values"""
    record = {
      'key_a': [{'key_c': ['val5', 'val4']}, {'key_c': ['val1', 'val4']},
                {'key_c': ['val2']}, {'key_c': ['val3']}], 'key_b': {'key_c': {'key_d': 'pong'}}
    }
    expected_map = {
      'key_a': [{'key_c': ['success', 'success']}, {'key_c': ['val1', 'success']},
                {'key_c': ['val2']}, {'key_c': ['val3']}], 'key_b': {'key_c': {'key_d': 'pong'}}
    }
    actions_tuple = Action(values_to_check=["val4", "val5"], keys=['key_a', 'key_c'], where_keys=[],
                           selected_action="Update",
                           where_value="", regex=False, value="success")
    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_addition_array():
    """should test record addition for nested array"""
    record = {
      'key_a': [{'key_c': ['val5', 'val4']},
                {'key_c': ['val1', 'val6']},
                {'key_c': ['val2']},
                {'key_c': ['val3']}],
      'key_b': {'key_c': {'key_d': 'pong'}}
    }
    expected_map = {
      'key_a': [{'key_c': ['val5', 'val4', 'success']},
                {'key_c': ['val1', 'val6', 'success']},
                {'key_c': ['val2', 'success']},
                {'key_c': ['val3', 'success']}],
      'key_b': {'key_c': {'key_d': 'pong'}}
    }
    actions_tuple = Action(values_to_check=[], keys=['key_a', 'key_c'], where_keys=[], selected_action="Addition",
                           where_value="", regex=False, value="success")
    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_deletion_array():
    """should test record deletion for nested array"""
    record = {
      'key_a': [{'key_c': ['val5', 'val4']},
                {'key_c': ['val1', 'val6']},
                {'key_c': ['val4', 'val6']},
                {'key_c': ['val3']}],
      'key_b': {'key_c': {'key_d': 'pong'}}
    }
    expected_map = {
      'key_a': [{'key_c': ['val5', 'val4']},
                {'key_c': ['val4']},
                {'key_c': ['val3']}],
      'key_b': {'key_c': {'key_d': 'pong'}}
    }
    actions_tuple = Action(values_to_check=["val6", "val1"], keys=['key_a', 'key_c'], where_keys=[],
                           selected_action="Deletion",
                           where_value="", regex=False, value="")
    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_deletion_empty_rec():
    record = {
        'key1': {
            'key2': {
                'key3': 'val'
            }
        }
    }
    expected_map = {}
    actions_tuple = Action(values_to_check=[], keys=['key1', 'key2', 'key3'], where_keys=[], selected_action="Deletion",
                           where_value="", regex=False, value="")

    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_field_not_existing():
    """should test sub_record creation for missing object"""
    record = {'abstracts': [{'not_source': 'success'}]}
    expected_map = {'abstracts': [{'not_source': 'success'}]}
    actions_tuple = Action(values_to_check=[], keys=['abstracts', 'source'], where_keys=[], selected_action="Update",
                           where_value="", regex=False, value="success")
    assert actions.run_action({}, record, actions_tuple) == expected_map


def test_record_creation():
    """should test sub_record creation for missing object"""
    key = ['abstracts', 'source']
    value = 'success'
    target_object = {'abstracts': [{'source': 'success'}]}
    assert actions.create_schema_record(schema_1, key, value) == target_object


def test_record_creation_2():
    """should test sub_record creation for missing object"""
    schema_2 = {
        "properties": {
            "source": {
                "$schema": "http://json-schema.org/schema#",
                "description": "Source of the information in this field. As several\
                            records can be merged,\nthis information\
                            allows us to remember where every bit of\
                            metadata came\nfrom and make decisions based\
                            on it.\n\n:MARC: Often not present.",
                "type": "string"
            }},
        "type": "object",
    }
    key = ['source']
    value = 'success'
    target_object = {'source': 'success'}
    assert actions.create_schema_record(schema_2, key, value) == target_object


def test_record_creation_3():
    """should test sub_record handling for missing object"""
    record_1 = {
        "abstracts": [
            {
                "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
            }
        ],
    }
    target_object = {
        "abstracts": [
          {
            "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
          },
        ],
    }
    actions_tuple = Action(values_to_check=[], keys=['abstracts', 'source'], where_keys=[], selected_action="Update",
                           where_value="", regex=False, value="success")
    assert actions.run_action(schema_1, record_1, actions_tuple) == target_object


def test_record_regex_where():
    test_record = {"authors": [
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
    expected_record = {"authors": [
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
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/schema.json'))\
            as data_file:
        schema = json.load(data_file)

    actions_tuple = Action(values_to_check=['Rome'], keys=['authors', 'affiliations', 'value'],
                           where_keys=['authors', 'signature_block'], selected_action="Update",
                           where_value='BANARo', regex=True, value="Success")

    assert actions.run_action(schema, test_record, actions_tuple) == expected_record
