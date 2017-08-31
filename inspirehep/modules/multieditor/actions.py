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
import re


class Addition(object):
    def __init__(self, keys, value,
                 where_regex=False, where_keys=[],
                 where_values=[]
                 ):
        self.keys = keys
        self.value = value
        self.where_regex = where_regex
        self.where_keys = where_keys
        self.where_values = where_values
        self.changed = False

    def apply_action(self, record, schema, position=0, checked=False):
        """Recursive function to change a record object."""
        key = self.keys[position]
        where_key = None
        if len(self.where_keys) > position:
            where_key = self.where_keys[position]
        new_schema = {}
        if schema:  # for testing purposes
            if schema['type'] == 'object':
                new_schema = schema['properties'][key]
            elif schema['type'] == 'array':
                new_schema = schema['items']['properties'][key]

        if where_key:
            if not checked and key != where_key:
                if not check_value(record=record, keys=self.where_keys, values_to_check=self.where_values,
                                   regex=self.where_regex, position=position):
                    return
                checked = True
        if not record.get(key):  # adding to object as well
            if self.where_keys and not checked:  # if the where key is in a deeper level and the subrecord is not there
                return
            creation_keys = self.keys[position:]
            record.update(create_schema_record(schema, creation_keys, self.value))
            self.changed = True
            return
        if position + 1 == len(self.keys):
            if isinstance(record[key], list):
                record[key].append(self.value)
                self.changed = True
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, new_schema, position + 1, checked)
            else:
                self.apply_action(record[key], new_schema, position + 1, checked)


class Deletion(object):
    def __init__(self, keys, value, values_to_check_regex=False, values_to_check=[],
                 where_regex=False, where_keys=[], where_values=[]):
        self.keys = keys
        self.value = value
        self.values_to_check_regex = values_to_check_regex
        self.values_to_check = values_to_check
        self.where_regex = where_regex
        self.where_keys = where_keys
        self.where_values = where_values
        self.changed = False

    def apply_action(self, record, schema, position=0, checked=False):
        """Recursive function to change a record object."""
        key = self.keys[position]
        where_key = None
        if len(self.where_keys) > position:
            where_key = self.where_keys[position]
        new_schema = {}
        if schema:  # for testing purposes
            if schema['type'] == 'object':
                new_schema = schema['properties'][key]
            elif schema['type'] == 'array':
                new_schema = schema['items']['properties'][key]

        if where_key:
            if not checked and key != where_key:
                if not check_value(record=record, keys=self.where_keys, values_to_check=self.where_values,
                                   regex=self.where_regex, position=position):
                    return
                checked = True
        if not record.get(key):
            return
        if position + 1 == len(self.keys):
            if isinstance(record[key], list):
                if self.values_to_check_regex:
                    for value_to_check in self.values_to_check:
                        record[key] = filter(lambda x: (not re.search(
                                re.escape(value_to_check),
                                x)), record[key])
                        self.changed = True
                else:
                    record[key] = filter(lambda x: x not in self.values_to_check, record[key])
                    self.changed = True
            else:
                if record[key] in self.values_to_check:
                    del record[key]
                    self.changed = True
                elif self.values_to_check_regex:
                    for value_to_check in self.values_to_check:
                        if re.search(
                                re.escape(value_to_check),
                                record[key]):
                                del record[key]
                                self.changed = True
                                break
                return
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, new_schema, position + 1, checked)
            else:
                self.apply_action(record[key], new_schema, position + 1, checked)
        if isinstance(record[key], list):
            record[key] = [item for item in record[key] if item not in [{}, '', []]]
        if record[key] in [{}, '', []]:
            del record[key]


class Update(object):
    def __init__(self, keys, value, values_to_check_regex, values_to_check,
                 where_regex, where_keys, where_values):
        self.keys = keys
        self.value = value
        self.values_to_check_regex = values_to_check_regex
        self.values_to_check = values_to_check
        self.where_regex = where_regex
        self.where_keys = where_keys
        self.where_values = where_values
        self.changed = False

    def apply_action(self, record, schema, position=0, checked=False):
        """Recursive function to change a record object."""
        key = self.keys[position]
        where_key = None
        if len(self.where_keys) > position:
            where_key = self.where_keys[position]
        new_schema = {}
        if schema:  # for testing purposes
            if schema['type'] == 'object':
                new_schema = schema['properties'][key]
            elif schema['type'] == 'array':
                new_schema = schema['items']['properties'][key]
        if where_key:
            if not checked and key != where_key:
                if not check_value(record=record, keys=self.where_keys, values_to_check=self.where_values,
                                   regex=self.where_regex, position=position):
                    return
                checked = True
        if not record.get(key):
            return
        if position + 1 == len(self.keys):
            if isinstance(record[key], list):
                if not self.values_to_check:
                    record[key] = [self.value if True else x for x in record[key]]
                if self.values_to_check_regex:
                    for value_to_check in self.values_to_check:
                        record[key] = [self.value if re.search(
                                re.escape(value_to_check),
                                x) else x for x in record[key]]
                else:
                    record[key] = [self.value if x in self.values_to_check else x for x in record[key]]
                self.changed = True
            else:
                if not self.values_to_check\
                        or record[key] in self.values_to_check:
                    record[key] = self.value
                if self.values_to_check_regex:
                    for value_to_check in self.values_to_check:
                        if re.search(
                                re.escape(value_to_check),
                                record[key]):
                                record[key] = self.value
                self.changed = True
                return
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, new_schema, position + 1, checked)
            else:
                self.apply_action(record[key], new_schema, position + 1, checked)


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
            new_schema = new_schema['properties']
            temp_record[key] = {}
            temp_record = temp_record[key]

        elif new_schema['type'] == 'array':
            if new_schema['items']['type'] == 'object':
                new_schema = new_schema['items']['properties']
            if len(path) == 1:
                temp_record[key] = [value]
                return record
            else:
                temp_record[key] = [{}]
                temp_record = temp_record[key][0]
    temp_record[path[-1]] = value
    return record


def check_value(record, regex, keys, values_to_check, position):
    """Where continues to find the value."""
    key = keys[position]
    if not record.get(key):
        return False
    temp_record = record[key]
    if isinstance(temp_record, list):
        for index, array_record in enumerate(temp_record):
            if position + 1 == len(keys):
                if array_record in values_to_check:
                    return True
                if regex:
                    for value_to_check in values_to_check:
                        if re.search(
                                re.escape(value_to_check),
                                array_record):
                            return True
            else:
                if check_value(array_record, regex,
                               keys, values_to_check, position + 1):
                    return True
    else:
        if position + 1 == len(keys):
            if temp_record in values_to_check:
                return True
            if regex:
                for value_to_check in values_to_check:
                    if re.search(
                            re.escape(value_to_check),
                            temp_record):
                        return True
        else:
            return check_value(temp_record, regex,
                               keys, values_to_check, position + 1)
    return False


def get_actions(user_actions):
    class_actions = []
    for user_action in user_actions:
        keys = user_action.get('mainKey').split('/')
        if not keys:
            return
        if user_action.get('whereKey'):
            where_keys = user_action.get('whereKey').split('/')
        else:
            where_keys = []
        if user_action.get('selectedAction') == 'Addition':
            class_actions.append(Addition(keys=keys, value=user_action.get('value'),
                                          where_regex=user_action.get('whereRegex'),
                                          where_keys=where_keys,
                                          where_values=user_action.get('whereValues')))
        elif user_action.get('selectedAction') == 'Deletion':
            class_actions.append(Deletion(keys=keys, value=user_action.get('value'),
                                          values_to_check_regex=user_action.get('updateRegex'),
                                          values_to_check=user_action.get('updateValues'),
                                          where_regex=user_action.get('whereRegex'),
                                          where_keys=where_keys,
                                          where_values=user_action.get('whereValues')))
        elif user_action.get('selectedAction') == 'Update':
            class_actions.append(Update(keys=keys, value=user_action.get('value'),
                                        values_to_check_regex=user_action.get('updateRegex'),
                                        values_to_check=user_action.get('updateValues'),
                                        where_regex=user_action.get('whereRegex'),
                                        where_keys=where_keys,
                                        where_values=user_action.get('whereValues')))
    return class_actions


def process_records_no_db(user_actions, records, schema): #  fixme name convention
    class_acions = get_actions(user_actions)
    for record in records:
        for class_action in class_acions:
            class_action.apply_action(record, schema)
    return records