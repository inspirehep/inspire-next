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
from collections import namedtuple
from abc import ABCMeta, abstractmethod

from .errors import InvalidValue, SchemaError


class ActionProcessor(object):
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
                    if condition_passes(record=record, schema=schema, keypath=condition['keypath'],
                                        update_value=condition['value'],
                                        match_type=condition['match_type'], position=position):
                        conditions_passed = conditions_passed + 1
                    else:
                        fails_any_condition = True

        return self.conditions_result(conditions_passed, key, fails_any_condition)

    def handle_record(self, record, key, schema, position, conditions_passed):
        if isinstance(record[key], list):
            for array_record in record[key]:
                self._process(array_record, schema, position + 1, conditions_passed)
        else:
            self._process(record[key], schema, position + 1, conditions_passed)

    @abstractmethod
    def process(self, **kwargs):
        return None

    def __repr__(self):
        return '%s(keypath=%s, value=%s, match_type=%s, update_value=%s, conditions=%s '\
               % (type(self), self.keypath, self.value, self.match_type, self.update_value, self.conditions)

    def __str__(self):
        return self.__repr__()

    @abstractmethod
    def _handle_exact_match(self, *args):
        """Abstract method to be implemented in subclasses"""
        return None

    @abstractmethod
    def _handle_regex_match(self, *args):
        """Abstract method to be implemented in subclasses"""
        return None

    @abstractmethod
    def _handle_contains_match(self, *args):
        """Abstract method to be implemented in subclasses"""
        return None

    def get_matching_function(self, name):
        MATCHING_ACTIONS = {
            'exact': getattr(self, '_handle_exact_match'),
            'regex': getattr(self, '_handle_regex_match'),
            'contains': getattr(self, '_handle_contains_match'),
        }
        return MATCHING_ACTIONS[name]


class AddProcessor(ActionProcessor):
    """Class that when applied adds a new primitive field or object to the selected path
    if the conditions are satisfied"""

    def _handle_exact_match(self, *args):
        """Method is not needed here but since its abstract it needs to be implemented"""
        return None

    def _handle_regex_match(self, *args):
        """Method is not needed here but since its abstract it needs to be implemented"""
        return None

    def _handle_contains_match(self, *args):
        """Method is not needed here but since its abstract it needs to be implemented"""
        return None

    def process(self, record, schema):
        self._process(record=record, schema=schema, position=0, conditions_passed=0)

    def _process(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema:
            raise SchemaError
        elif fails_any_condition:
            return
        if not record.get(key):
            if self.conditions and conditions_passed < len(self.conditions):
                return
            remaining_path = self.keypath[position:]
            record.update(create_object_from_path(schema, remaining_path, self.value))
            self.changed = True
            return
        elif is_last_key(position, self.keypath):
            if isinstance(record[key], list):
                record[key].append(self.value)
                self.changed = True
            return
        new_schema = get_subschema(schema, key)
        self.handle_record(record, key, new_schema, position, conditions_passed)


class DeleteProcessor(ActionProcessor):
    """Class that when applied deletes the appropriate field if the conditions are satisfied"""

    def _handle_exact_match(self, record, key, serialized_update_value):
        """
        Handles the exact match case and deletes the provided value from the record
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            list_size = len(record[key])
            record[key] = [x for x in record[key] if x != serialized_update_value]
            if list_size > len(record[key]):
                self.changed = True
        else:
            if record[key] == serialized_update_value:
                del record[key]
                self.changed = True

    def _handle_regex_match(self, record, key, serialized_update_value):
        """
        Handles the regex match case and deletes the provided value from the record
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            list_size = len(record[key])
            record[key] = [x for x in record[key] if not re.search(
                serialized_update_value, x)]
            if list_size > len(record[key]):
                self.changed = True
        else:
            if re.search(serialized_update_value, record[key]):
                del record[key]
                self.changed = True

    def _handle_contains_match(self, record, key, serialized_update_value):
        """
        Handles the contains match case and deletes the provided value from the record
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            list_size = len(record[key])
            record[key] = [x for x in record[key] if serialized_update_value.lower() not in x.lower()]
            if list_size > len(record[key]):
                self.changed = True
        else:
            if serialized_update_value.lower() in record[key].lower():
                del record[key]
                self.changed = True

    def process(self, record, schema):
        self._process(record=record, schema=schema, position=0, conditions_passed=0)

    def _process(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be deleted resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema:
            raise SchemaError
        elif fails_any_condition or not record.get(key):
            return
        new_schema = get_subschema(schema, key)
        if is_last_key(position, self.keypath):
            self.handle_deletion_process(record, key, new_schema)
            if record.get(key) is None:
                return
        else:
            self.handle_record(record, key, new_schema, position, conditions_passed)
        self.clean_empty(record, key)

    def handle_deletion_process(self, record, key, schema):
        serialized_update_value = serialize_value(self.update_value, schema)
        self.get_matching_function(self.match_type)(record, key, serialized_update_value)

    def clean_empty(self, record, key):
        """
        :param record: record to be cleaned
        :param key: key inside which the deletion took place
        :return:
        """
        if isinstance(record[key], list):
            record[key] = [item for item in record[key] if item not in [{}, '', []]]
        if record[key] in [{}, '', []]:
            del record[key]
        return record


class UpdateProcessor(ActionProcessor):
    """Class that when applied updates the appropriate field if the conditions
     are satisfied and replaces its value with the one provided"""

    def _handle_exact_match(self, record, key, serialized_update_value):
        """
        Handles the exact match case and updates the targeted value from the record to the provided one
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            for count, index in enumerate(record[key]):
                if serialized_update_value == index:
                    record[key][count] = self.value
                    self.changed = True
        else:
            if record[key] == serialized_update_value:
                record[key] = self.value
                self.changed = True

    def _handle_regex_match(self, record, key, serialized_update_value):
        """
        Handles the regex match case and updates the targeted value from the record to the provided one
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            for count, index in enumerate(record[key]):
                if re.search(serialized_update_value, index):
                    record[key][count] = self.value
                    self.changed = True
        else:
            if re.search(serialized_update_value, record[key]):
                record[key] = self.value
                self.changed = True

    def _handle_contains_match(self, record, key, serialized_update_value):
        """
        Handles the contains match case and updates the targeted value from the record to the provided one
        :param record: record to be checked
        :param key: key of the record to be checked
        :param serialized_update_value: value to be checked if it resides in the record[key]
        :return:
        """
        if isinstance(record[key], list):
            for count, index in enumerate(record[key]):
                if serialized_update_value.lower() in index.lower():
                    record[key][count] = self.value
                    self.changed = True
        else:
            if serialized_update_value.lower() in record[key].lower():
                record[key] = self.value
                self.changed = True

    def process(self, record, schema):
        self._process(record=record, schema=schema, position=0, conditions_passed=0)

    def _process(self, record, schema, position, conditions_passed):
        """
        :param record: record in which the field to be updated resides
        :param schema: schema on which our record is based
        :param position: level of recursion
        :param conditions_passed: number of conditions that run and passed
        :return:
        """
        conditions_passed, key, fails_any_condition = self.get_next_key_and_condition_check(record, schema, position, conditions_passed)
        if not schema:
            raise SchemaError
        elif fails_any_condition or not record.get(key):
            return
        new_schema = get_subschema(schema, key)
        if is_last_key(position, self.keypath):
            self.handle_update_process(record, key, new_schema)
            return
        else:
            self.handle_record(record, key, new_schema, position, conditions_passed)

    def handle_update_process(self, record, key, schema):
        self.value = serialize_value(self.value, schema)
        serialized_update_value = serialize_value(self.update_value, schema)
        self.get_matching_function(self.match_type)(record, key, serialized_update_value)


def create_object_from_path(schema, path, value):
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
    for key in path:
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


def condition_passes(record, schema, match_type, keypath, update_value, position):
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
        raise SchemaError
    if not record.get(key):
        return match_type == 'missing'
    new_schema = get_subschema(schema, key)
    sub_record = record[key]
    if is_last_key(position, keypath):
        return handle_condition_matching(sub_record, update_value, match_type, new_schema)
    else:
        return handle_condition_progression(sub_record, new_schema, match_type,
                                            keypath, update_value, position)


def handle_condition_matching(record, update_value, match_type, schema):
    """
    Checks if the condition is valid or not
    :param record: record in which the condition is checked
    :param update_value: value to be checked
    :param match_type: match type of condition
    :param schema: schema to serialize the value to
    :return: boolean depending on the success of the matching
    """
    update_value = serialize_value(update_value, schema)
    if isinstance(record, list):
        for index, array_record in enumerate(record):
                if match_type == 'exact' and array_record == update_value:
                    return True
                elif match_type == 'contains' and update_value.lower() in array_record.lower():
                    return True
                elif match_type == 'regex'and re.search(
                        update_value, array_record):
                        return True
    else:
        if match_type == 'exact' and record == update_value:
            return True
        elif match_type == 'contains' and update_value.lower() in record.lower():
            return True
        elif match_type == 'regex' and re.search(
                update_value, record):
            return True
    return False


def handle_condition_progression(record, schema, match_type,
                                 keypath, update_value, position):
    if isinstance(record, list):
        for index in record:
            if condition_passes(index, schema, match_type,
                                 keypath, update_value, position + 1):
                return True
    else:
        return condition_passes(record, schema, match_type,
                                 keypath, update_value, position + 1)
    return False


def serialize_value(value, schema):
    """
    Serializes value according to the schema.
    :param value: value to be serialized
    :param schema: schema for the value to be serialized to
    :return: the serialized value
    """
    if schema['type'] == 'array':
        schema = schema['items']
    if schema['type'] == 'integer':
        try:
            serialized_value = int(value)
        except ValueError:
            raise InvalidValue(value)
    elif schema['type'] == 'boolean':
        if value.lower() == 'true':
            serialized_value = True
        elif value.lower() == 'false':
            serialized_value = False
        else:
            raise InvalidValue
    elif schema['type'] == 'string':
        serialized_value = value
    else:
        raise InvalidValue
    return serialized_value


def get_subschema(schema, key):
    if schema['type'] == 'object':
        return schema['properties'][key]
    elif schema['type'] == 'array':
        return schema['items']['properties'][key]


def should_run_condition(self, key, condition, position):
    """
    Checks if the condition check should run.
    :param self: 
    :param key: current key of action
    :param condition: condition that should be checked
    :param position: depth of recursion
    :return: 
    """
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


def is_last_key(position, keypath):
    return position + 1 == len(keypath)
