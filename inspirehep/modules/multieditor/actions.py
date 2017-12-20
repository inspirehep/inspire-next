# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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
from collections import namedtuple
from abc import ABCMeta, abstractmethod
from jsonschema import ValidationError
from inspire_schemas.api import validate
from inspirehep.utils.record import inspire_diff


class Action(object):
    __metaclass__ = ABCMeta

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
        self.conditions_result = namedtuple('conditions_result', ['conditions_passed', 'key', 'fails_any_condition'])

    def get_next_key_and_condition_check(self, record, schema, position, conditions_passed):
        """
        :param record: record to be processed
        :param position: recursion level
        :param conditions_passed: number of conditions that got checked and passed
        :return: returns the new number of conditions passed,
         the new key for this recursion and if a condition got checked and the failed the check
        """

        key = self.keypath[position]
        fails_any_condition = False
        if not self.conditions:
            return self.conditions_result(conditions_passed, key, fails_any_condition)
        else:
            for condition in self.conditions:
                if should_run_condition(self, key, condition, position):
                    if condition_passses(record=record, schema=schema, keypath=condition['keypath'],
                                         update_value=condition['value'],
                                         match_type=condition['match_type'], position=position):
                        conditions_passed = conditions_passed + 1
                    else:
                        fails_any_condition = True

        return self.conditions_result(conditions_passed, key, fails_any_condition)

    @abstractmethod
    def apply(self, **kwargs):
        return None

    def __repr__(self):
        return '%s(keypath=%s, value=%s, match_type=%s, update_value=%s, conditions=%s '\
               % (type(self), self.keypath, self.value, self.match_type, self.update_value, self.conditions)

    def __str__(self):
        return self.__repr__()


class Addition(Action):
    """Class that when applied adds a new primitive field or object to the selected path
    if the conditions are satisfied"""
    def apply(self, record, schema):
        self._apply(record=record, schema=schema, position=0, conditions_passed=0)

    def _apply(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or fails_any_condition:
            return
        if not record.get(key):
            if self.conditions and conditions_passed < len(self.conditions):
                return
            remaining_path = self.keypath[position:]
            record.update(create_schema_record(schema, remaining_path, self.value))
            self.changed = True
            return
        elif is_last_key(position, self.keypath):
            if isinstance(record[key], list):
                record[key].append(self.value)
                self.changed = True
            return
        new_schema = schema_progression(schema, key)
        handle_record(self, record, key, new_schema, position, conditions_passed)


class Deletion(Action):
    """Class that when applied deletes the appropriate field if the conditions are satisfied"""
    def apply(self, record, schema):
        self._apply(record=record, schema=schema, position=0, conditions_passed=0)

    def _apply(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be deleted resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or fails_any_condition or not record.get(key):
            return
        new_schema = schema_progression(schema, key)
        if is_last_key(position, self.keypath):
            handle_deletion_process(self, record, key, new_schema)
            if record.get(key) is None:
                return
        else:
            handle_record(self, record, key, new_schema, position, conditions_passed)
        clean_empty(record, key)


class Update(Action):
    """Class that when applied updates the appropriate field if the conditions
     are satisfied and replaces its value with the one provided"""
    def apply(self, record, schema):
        self._apply(record=record, schema=schema, position=0, conditions_passed=0)

    def _apply(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema or fails_any_condition or not record.get(key):
            return
        new_schema = schema_progression(schema, key)
        if is_last_key(position, self.keypath):
            handle_update_process(self, record, key, new_schema)
            return
        else:
            handle_record(self, record, key, new_schema, position, conditions_passed)


def handle_record(self, record, key, schema, position, conditions_passed):
        if isinstance(record[key], list):
            for array_record in record[key]:
                self._apply(array_record, schema, position + 1, conditions_passed)
        else:
            self._apply(record[key], schema, position + 1, conditions_passed)


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


def condition_passses(record, schema, match_type, keypath, update_value, position):
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
    new_schema = schema_progression(schema, key)
    temp_record = record[key]
    if isinstance(temp_record, list):
        for index, array_record in enumerate(temp_record):
            if is_last_key(position, keypath):
                update_value = serialize_value(update_value, new_schema)
                if update_value == 'error':
                    return False
                if match_type == 'exact' and array_record == update_value:
                    return True
                elif match_type == 'contains' and update_value.lower() in array_record.lower():
                    return True
                elif match_type == 'regex'and re.search(
                        update_value, array_record):
                        return True
            else:
                if condition_passses(array_record, new_schema, match_type,
                               keypath, update_value, position + 1):
                    return True
    else:
        if is_last_key(position, keypath):
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
            return condition_passses(temp_record, new_schema, match_type,
                               keypath, update_value, position + 1)
    return False


def serialize_value(value, schema):
    if schema['type'] == 'array':
        schema = schema['items']
    if schema['type'] == 'integer':
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


def schema_progression(schema, key):
    if schema['type'] == 'object':
        return schema['properties'][key]
    elif schema['type'] == 'array':
        return schema['items']['properties'][key]


def should_run_condition(self, key, condition, position):
    if position < len(condition['keypath']):
        if key != condition['keypath'][position] and \
                (position == 0 or
                 self.keypath[position - 1] == condition['keypath'][position - 1]):
            return True
        elif key == condition['keypath'][position] and\
                position == len(self.keypath) - 1:
            return True
    else:
        return False


def handle_update_process(self, record, key, schema):
    self.value = serialize_value(self.value, schema)
    serialized_update_value = serialize_value(self.update_value, schema)
    if serialized_update_value == 'error':
        return
    if isinstance(record[key], list):
        if self.match_type == 'regex':
            for count, index in enumerate(record[key]):
                if re.search(serialized_update_value, index):
                    record[key][count] = self.value
                    self.changed = True
        elif self.match_type == 'exact':
            for count, index in enumerate(record[key]):
                if serialized_update_value == index:
                    record[key][count] = self.value
                    self.changed = True
        elif self.match_type == 'contains':
            for count, index in enumerate(record[key]):
                if serialized_update_value.lower() in index.lower():
                    record[key][count] = self.value
                    self.changed = True
    else:
        if self.match_type == 'exact' and record[key] == serialized_update_value:
            record[key] = self.value
            self.changed = True
        if self.match_type == 'regex' and re.search(
                serialized_update_value, record[key]):
            record[key] = self.value
            self.changed = True
        elif self.match_type == 'contains' and serialized_update_value.lower() in record[key].lower():
            record[key] = self.value
            self.changed = True


def handle_deletion_process(self, record, key, schema):
    serialized_update_value = serialize_value(self.update_value, schema)
    if serialized_update_value == 'error':
        return
    if isinstance(record[key], list):
        list_size = len(record[key])
        if self.match_type == 'regex':
            record[key] = [x for x in record[key] if not re.search(
                serialized_update_value, x)]
        elif self.match_type == 'exact':
            record[key] = [x for x in record[key] if not x == serialized_update_value]
        elif self.match_type == 'contains':
            record[key] = [x for x in record[key] if not serialized_update_value.lower() in x.lower()]
        if list_size > len(record[key]):
            self.changed = True
    else:
        if self.match_type == 'exact' and record[key] == serialized_update_value:
            del record[key]
            self.changed = True
        elif self.match_type == 'regex' and re.search(
                serialized_update_value, record[key]):
            del record[key]
            self.changed = True
        elif self.match_type == 'contains' and serialized_update_value.lower() in record[key].lower():
            del record[key]
            self.changed = True


def clean_empty(record, key):
    if isinstance(record[key], list):
        record[key] = [item for item in record[key] if item not in [{}, '', []]]
    if record[key] in [{}, '', []]:
        del record[key]


def is_last_key(position, keypath):
    return position + 1 == len(keypath)
