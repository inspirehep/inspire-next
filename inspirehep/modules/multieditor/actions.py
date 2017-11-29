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


from jsonschema import ValidationError
from inspire_schemas.api import validate

from inspirehep.utils.record import inspire_diff


class Action(object):
    def __init__(self, keypath, value=None, match_type=None, update_value=None,
                 conditions=None):
        """
        :param keypath: path to value
        :type keypath: array(string)

       :param value: value to add or update to
       :type value: string

       :param match_type: type of matching
       :type match_type: string

       :param update_value: value to replace or delete
       :type update_value: string

       :param conditions: conditions of the action
       :type conditions: array(object)
        """
        self.keypath = keypath
        self.value = value
        self.match_type = match_type
        self.update_value = update_value
        self.conditions = conditions
        self.changed = False

    def get_next_key_and_condition_check(self, record, schema, position, conditions_passed):
        """

        :param record: record to be processed
        :param position: recursion level
        :param conditions_passed: number of conditions that got checked and passed
        :return: returns the new number of conditions passed,
         the new key for this recursion and if a condition got checked and the failed the check
        """
        key = self.keypath[position]
        condition_failed = False
        if self.conditions:
            for condition in self.conditions:
                should_check = False
                if position < len(condition.get('keypath')):
                    if key != condition.get('keypath')[position] and\
                     (position == 0 or self.keypath[position - 1] == condition.get('keypath')[position - 1]):
                        should_check = True
                    elif key == condition.get('keypath')[position] and position == len(self.keypath) - 1:
                        should_check = True
                    if should_check:
                        if not check_value(record=record, schema=schema, keypath=condition.get('keypath'),
                                           update_value=condition.get('value', ''),
                                           match_type=condition.get('match_type', ''), position=position):
                            condition_failed = True
                        else:
                            conditions_passed = conditions_passed + 1  # number of conditions that passed successfully
        return conditions_passed, key, condition_failed


class Addition(Action):
    """Class that when applied adds a new primitive field or object to the selected path
    if the conditions are satisfied"""
    def apply(self, record, schema, position=0, conditions_passed=0):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, condition_failed = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or condition_failed:
            return
        if not record.get(key):
            if self.conditions and conditions_passed < len(self.conditions):
                return
            remaining_path = self.keypath[position:]
            record.update(create_schema_record(schema, remaining_path, self.value))
            self.changed = True
            return
        if position == len(self.keypath) - 1:
            if isinstance(record[key], list):
                record[key].append(self.value)
                self.changed = True
        else:
            if schema['type'] == 'object':
                new_schema = schema['properties'][key]
            elif schema['type'] == 'array':
                new_schema = schema['items']['properties'][key]
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply(array_record, new_schema, position + 1, conditions_passed)
            else:
                self.apply(record[key], new_schema, position + 1, conditions_passed)


class Deletion(Action):
    """Class that when applied deletes the appropriate field if the conditions are satisfied"""
    def apply(self, record, schema, position=0, conditions_passed=0):
        """
        :param record: record in which the field to be deleted resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, condition_failed =\
            self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or condition_failed:
            return
        if not record.get(key):
            return
        if position == len(self.keypath) - 1:
            if isinstance(record[key], list):
                list_size = len(record[key])
                if self.match_type == 'regex':
                    record[key] = [x for x in record[key] if not re.search(
                        self.update_value, x)]
                elif self.match_type == 'exact':
                    record[key] = [x for x in record[key] if not x == self.update_value]
                elif self.match_type == 'contains':
                    record[key] = [x for x in record[key] if not self.update_value.lower() in x.lower()]
                if list_size > len(record[key]):
                    self.changed = True
            else:
                if self.match_type == 'exact' and record[key] == self.update_value:
                    del record[key]
                    self.changed = True
                elif self.match_type == 'regex' and re.search(
                        self.update_value, record[key]):
                    del record[key]
                    self.changed = True
                elif self.match_type == 'contains' and self.update_value.lower() in record[key].lower():
                    del record[key]
                    self.changed = True
                return
        else:
            if schema['type'] == 'object':
                new_schema = schema['properties'][key]
            elif schema['type'] == 'array':
                new_schema = schema['items']['properties'][key]
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply(array_record, new_schema, position + 1, conditions_passed)
            else:
                self.apply(record[key], new_schema, position + 1, conditions_passed)
        if isinstance(record[key], list):
            record[key] = [item for item in record[key] if item not in [{}, '', []]]
        if record[key] in [{}, '', []]:
            del record[key]


class Update(Action):
    """Class that when applied updates the appropriate field if the conditions
     are satisfied and replaces its value with the one provided"""
    def apply(self, record, schema, position=0, conditions_passed=0):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, condition_failed = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or condition_failed:
            return
        if not record.get(key):
            return
        if schema['type'] == 'object':
            new_schema = schema['properties'][key]
        elif schema['type'] == 'array':
            new_schema = schema['items']['properties'][key]
        if position == len(self.keypath) - 1:
            self.value = serialize_value(self.value, new_schema)
            if self.value == 'error':
                return
            if isinstance(record[key], list):
                if self.match_type == 'regex':
                    for count, index in enumerate(record[key]):
                        if re.search(self.update_value, index):
                            record[key][count] = self.value
                            self.changed = True
                elif self.match_type == 'exact':
                    for count, index in enumerate(record[key]):
                        if self.update_value == index:
                            record[key][count] = self.value
                            self.changed = True
                elif self.match_type == 'contains':
                    for count, index in enumerate(record[key]):
                        if self.update_value.lower() in index.lower():
                            record[key][count] = self.value
                            self.changed = True
            else:
                if self.match_type == 'exact' and record[key] == self.update_value:
                    record[key] = self.value
                    self.changed = True
                if self.match_type == 'regex' and re.search(
                        self.update_value, record[key]):
                            record[key] = self.value
                            self.changed = True
                elif self.match_type == 'contains' and self.update_value.lower() in record[key].lower():
                    record[key] = self.value
                    self.changed = True
                return
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply(array_record, new_schema, position + 1, conditions_passed)
            else:
                self.apply(record[key], new_schema, position + 1, conditions_passed)


def create_schema_record(schema, path, value):
    """
    Function that creates an object according to the provided schema
    :param schema: Json Schema to be followed on creating the object
    :param path: Path to be followed with schema when creating the object
    :param value: value to be assigned at the final path key
    :return: returns the created object with the provided value attached at the final key
    """
    record = {}
    temp_record = record
    is_primitive_array = False
    if schema['type'] == 'array':
        schema = schema['items']['properties']
    elif schema['type'] == 'object':
        schema = schema['properties']
    for loops, key in enumerate(path):
        schema = schema[key]
        if schema['type'] == 'object':
            is_primitive_array = False
            schema = schema['properties']
            temp_record[key] = {}
            temp_record = temp_record[key]

        elif schema['type'] == 'array':
            if schema['items']['type'] == 'object':
                schema = schema['items']['properties']
            else:
                is_primitive_array = True
            if len(path) == 1:
                temp_record[key] = [value]
                return record
            else:
                if not is_primitive_array:
                    temp_record[key] = [{}]
                    temp_record = temp_record[key][0]
    if is_primitive_array:
        temp_record[path[-1]] = [value]
    else:
        temp_record[path[-1]] = value
    return record


def check_value(record, schema, match_type, keypath, update_value, position):
    """
    Function that checks the validity of the action condition
    :param record: the subrecord in which our field of interest resides
    :param match_type: type of the condition matching
    :param keypath: path in which the field should be checked
    :param update_value: value to be matched with the conditions
    :param position: current recursion level
    :return:
    """
    key = keypath[position]
    if not schema:
        return False
    if not record.get(key):
        return match_type == 'missing'
    if schema['type'] == 'object':
        new_schema = schema['properties'][key]
    elif schema['type'] == 'array':
        new_schema = schema['items']['properties'][key]
    temp_record = record[key]
    if isinstance(temp_record, list):
        update_value = serialize_value(update_value, new_schema)
        if update_value == 'error':
            return False
        for index, array_record in enumerate(temp_record):
            if position + 1 == len(keypath):
                if match_type == 'exact' and array_record == update_value:
                    return True
                elif match_type == 'contains' and update_value.lower() in array_record.lower():
                    return True
                elif match_type == 'regex'and re.search(
                        update_value, array_record):
                        return True
            else:
                if check_value(array_record, new_schema, match_type,
                               keypath, update_value, position + 1):
                    return True
    else:
        if position + 1 == len(keypath):
            update_value = serialize_value(update_value, new_schema)
            if update_value == 'error':
                return False
            if match_type == 'exact' and temp_record == update_value:
                return True
            elif match_type == 'contains' and update_value.lower() in temp_record.lower():
                return True
            elif match_type == 'regex' and re.search(
                    update_value, temp_record):
                return True
        else:
            return check_value(temp_record, new_schema, match_type,
                               keypath, update_value, position + 1)
    return False


def serialize_value(value, schema):
    if schema['type'] == 'number':
        serialized_value = int(value)
    elif schema['type'] == 'boolean':
        if value.lower() == 'true':
            serialized_value = True
        elif value.lower() == 'false':
            serialized_value = False
        else:
            return 'error'
    elif schema['type'] == 'string':
        serialized_value = value
    else:
        return 'error'
    return serialized_value


def compare_records(old_records, new_records, schema):
    """
    Compares and validates the records after the actions have been applied
    :param old_records: records before actions
    :param new_records: records after actions
    :param schema: corresponding schema of the records
    :return:
    """
    json_patches = []
    errors = []
    for index, new_record in enumerate(new_records):
        json_patches.append(inspire_diff(old_records[index], new_record))
        try:
            validate(new_record, schema)
        except (ValidationError, Exception) as e:
            errors.append(e.message)
        else:
            errors.append(None)
    return json_patches, errors
