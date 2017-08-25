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
import re
from collections import namedtuple, deque
from inspire_schemas.api import load_schema


Action = namedtuple('Action', 'keys, selected_action, value, values_to_check, regex, where_keys, where_value')


def run_user_actions(user_actions,user_query):
    """Executing user commands."""

    schema = load_schema('hep')
    with open(os.path.join(os.path.dirname(__file__),  # change to load from db
                           'assets/records.json'))\
            as data_file:
        records = json.load(data_file)
    for record in records:
        for action in user_actions:

            if action.get('updateValue'):
                values_to_check = action.get('updateValue').split(',')
            else:
                values_to_check = []

            keys = action.get('mainKey').split('/')
            where_key = action.get('whereKey')
            if where_key:
                where_keys = where_key.split('/')
            else:
                where_keys = []

            action_tuple = Action(keys, action.get('selectedAction'),
                                  action.get('value'), values_to_check, action.get('regex'),
                                  where_keys, action.get('whereValue'))
            apply_action(schema, record, action_tuple)
    return records


def run_action(schema, record, action):
    """Initial function to run the recursive one."""
    apply_action(schema, record, action)  # fixme propably delete this function :)
    return record


def apply_action(schema, record, action):
    """Recursive function to change a record object."""
    new_keys = deque(action.keys)
    key = new_keys.popleft()
    new_schema = {}
    if schema:  # fixme in a more stable version
        # the schema should always be present
        if schema['type'] == 'object':
            new_schema = schema['properties'][key]
        elif schema['type'] == 'array':
            new_schema = schema['items']['properties'][key]
    if not record.get(key):
        if action.selected_action == 'Addition':
            record.update(create_schema_record(schema, action.keys, action.value))
        return
    if action.where_keys and key != action.where_keys[0]:
        if check_value(record, action.where_keys, action.where_value) == 0:
            return
        else:
            action._replace(where_keys=[])
    if not new_keys:
        apply_action_to_field(record, key, action.regex,
                              action.selected_action, action.value, action.values_to_check)
    else:
        if len(action.where_keys) != 0:
            new_where_keys = deque(action.where_keys)
            new_where_keys.popleft()
        else:
            new_where_keys = action.where_keys
        if isinstance(record[key], list):
            for array_record in record[key]:
                action_tuple = Action(new_keys, action.selected_action,
                                      action.value, action.values_to_check, action.regex,
                                      new_where_keys, action.where_value)
                apply_action(new_schema, array_record, action_tuple)
        else:
            action_tuple = Action(new_keys, action.selected_action,
                                  action.value, action.values_to_check, action.regex,
                                  new_where_keys, action.where_value)
            apply_action(new_schema, record[key], action_tuple)
    if action.selected_action == 'Deletion':  # don't leave empty objects
        if not record[key]:
            del record[key]


def create_schema_record(schema, path, value):
    """Object creation in par with the schema."""
    record = {}
    temp_record = record
    new_schema = schema
    if new_schema['type'] == 'array':
        new_schema = new_schema['items']['properties']
    elif new_schema['type'] == 'object':
        new_schema = new_schema['properties']
    for key in path:
        new_schema = new_schema[key]
        if new_schema['type'] == 'object':
            new_schema = schema['properties']
            temp_record[key] = {}
            temp_record = temp_record[key]

        elif new_schema['type'] == 'array':
            if new_schema['items']['type'] == 'object':
                new_schema = new_schema['items']['properties']
                temp_record[key] = [{}]
                temp_record = temp_record[key][0]
    temp_record[path[-1]] = value
    return record


def check_value(record, keys, value_to_check):
    """Where continues to find the value."""
    new_keys = deque(keys)
    key = new_keys.popleft()
    if key not in record:
        return False
    temp_record = record[key]
    if isinstance(temp_record, list):
        for index, array_record in enumerate(temp_record):
            if len(new_keys) == 0:
                if array_record == value_to_check:
                    return True
            else:
                if check_value(array_record,
                               new_keys, value_to_check):
                    return True
    else:
        if len(new_keys) == 0:
            if temp_record == value_to_check:
                return True
        else:
            return check_value(temp_record,
                               new_keys, value_to_check)
    return False


def apply_action_to_field(record, key, regex,
                          action, value, value_to_check):
    """Function for applying action to object or array."""
    if isinstance(record[key], list):
        apply_to_array(record, key, regex, action, value, value_to_check)
    else:
        apply_to_object(record, key, regex, action, value, value_to_check)


def apply_to_array(record, key, regex, action, value, values_to_check):
    """Applying action to array."""
    for index, array_record in enumerate(record[key]):
        if action == 'Update':
            if regex and re.search(
                    re.escape(values_to_check[0]),
                    record[key][index]):
                record[key][index] = value
            elif array_record in values_to_check:
                record[key][index] = value
        elif action == 'Addition':
            record[key].append(value)
            return  # In that case we want to stop looping
        elif action == 'Deletion':
            if len(values_to_check) == 0 \
                    or array_record in values_to_check:
                record[key].pop(index)


def apply_to_object(record, key, regex, action, value, values_to_check):
    """Aplying action to Object."""
    if action == 'Update':
        if regex and re.search(
                re.escape(values_to_check[0]),
                record[key]):
            record[key] = value
        elif str(record[key]) in values_to_check:
            record[key] = value
    elif action == 'Addition' and not record.get(key):
        record[key] = value  # dont overwrite values
    elif action == 'Deletion':
        if len(values_to_check) == 0 \
                or record[key] in values_to_check:
            record[key] = ''  # Mark for deletion
