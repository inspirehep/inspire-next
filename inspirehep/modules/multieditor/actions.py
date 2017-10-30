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


class Action(object):
    def __init__(self, keys, value=None, match_type=None, value_to_check=None,
                 conditions=None):
        """
        :param keys: path to value
        :type keys: array(string)

       :param value: value to add or update to
       :type value: string

       :param match_type: type of matching
       :type match_type: string

       :param value_to_check: value to replace or delete
       :type value_to_check: string

       :param conditions: conditions of the action
       :type conditions: array(object)
        """
        self.keys = keys
        self.value = value
        self.match_type = match_type
        self.value_to_check = value_to_check
        self.conditions = conditions
        self.changed = False

    def process_keys(self, record, position, conditions_passed):
        key = self.keys[position]
        condition_failed = False
        if self.conditions:
            for condition in self.conditions:
                if position < len(condition.get('keys')) and\
                        (key != condition.get('keys')[position] and
                            (position == 0 or self.keys[position - 1] == condition.get('keys')[position - 1]) or
                            (key == condition.get('keys')[position] and position == len(self.keys) - 1)):
                    # Condition and action key should differ for the first time to be checked
                    # Or action key is the last on action's path and condition path is the same or extends deeper
                    if not check_value(record=record, keys=condition.get('keys'),
                                       value_to_check=condition.get('value', ''),
                                       match_type=condition.get('match_type', ''), position=position):
                        condition_failed = True
                    conditions_passed = conditions_passed + 1  # number of conditions that passed successfully
        return conditions_passed, key, condition_failed


class Addition(Action):

    def apply_action(self, record, schema, position=0, conditions_passed=0):
        """Recursive function to add a record object."""
        conditions_passed, key, condition_failed = self.process_keys(record, position, conditions_passed)
        if not schema:
            return
        if schema['type'] == 'object':
            new_schema = schema['properties'][key]
        elif schema['type'] == 'array':
            new_schema = schema['items']['properties'][key]
        if condition_failed:  # if the condition check was negative stop the action
            return
        if not record.get(key):
            if self.conditions and conditions_passed < len(self.conditions):
                return  # if the conditions that passed are less
                #  than the total ones the subrecord of the condition is missing and the action wont be applied
            creation_keys = self.keys[position:]
            record.update(create_schema_record(schema, creation_keys, self.value))
            self.changed = True
            return
        if position == len(self.keys) - 1:
            if isinstance(record[key], list):
                record[key].append(self.value)
                self.changed = True
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, new_schema, position + 1, conditions_passed)
            else:
                self.apply_action(record[key], new_schema, position + 1, conditions_passed)


class Deletion(Action):

    def apply_action(self, record, schema=None, position=0, conditions_passed=0):
        """Recursive function to delete a record primitive key."""
        conditions_passed, key, condition_failed = self.process_keys(record, position, conditions_passed)
        if condition_failed:
            return
        if not record.get(key):
            return
        if position == len(self.keys) - 1:
            if isinstance(record[key], list):
                if self.match_type == 'regex':
                        record[key] = filter(lambda x: (not re.search(
                            self.value_to_check, x)), record[key])
                elif self.match_type == 'exact':
                    record[key] = filter(lambda x: not x == self.value_to_check, record[key])
                elif self.match_type == 'contains':
                    record[key] = filter(lambda x: self.value_to_check not in x, record[key])
            else:
                if self.match_type == 'exact' and record[key] == self.value_to_check:
                    del record[key]

                elif self.match_type == 'regex' and re.search(
                        self.value_to_check, record[key]):
                            del record[key]
                elif self.match_type == 'contains' and self.value_to_check in record[key]:
                    del record[key]
                self.changed = True
                return
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, schema, position + 1, conditions_passed)
            else:
                self.apply_action(record[key], schema, position + 1, conditions_passed)
        if isinstance(record[key], list):
            record[key] = [item for item in record[key] if item not in [{}, '', []]]
        if record[key] in [{}, '', []]:
            del record[key]


class Update(Action):

    def apply_action(self, record, schema=None, position=0, conditions_passed=0):
        """Recursive function to update a record primitive key."""
        conditions_passed, key, condition_failed = self.process_keys(record, position, conditions_passed)
        if condition_failed:
            return
        if not record.get(key):
            return
        if position == len(self.keys) - 1:
            if isinstance(record[key], list):
                if self.match_type == 'regex':
                    record[key] = [self.value if re.search(
                        self.value_to_check, x) else x for x in record[key]]

                elif self.match_type == 'exact':
                    record[key] = [self.value if x == self.value_to_check else x for x in record[key]]

                elif self.match_type == 'contains':
                    record[key] = [self.value if self.value_to_check in x else x for x in record[key]]
                self.changed = True
            else:
                if self.match_type == 'exact' and record[key] == self.value_to_check:
                    record[key] = self.value
                if self.match_type == 'regex' and re.search(
                        self.value_to_check, record[key]):
                            record[key] = self.value
                elif self.match_type == 'contains' and self.value_to_check in record[key]:
                    record[key] = self.value
                self.changed = True
                return
        else:
            if isinstance(record[key], list):
                for array_record in record[key]:
                    self.apply_action(array_record, schema, position + 1, conditions_passed)
            else:
                self.apply_action(record[key], schema, position + 1, conditions_passed)


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


def check_value(record, match_type, keys, value_to_check, position):
    """Function that checks the validity of the condition."""
    key = keys[position]
    if not record.get(key):
        return match_type == 'missing'
    temp_record = record[key]
    if isinstance(temp_record, list):
        for index, array_record in enumerate(temp_record):
            if position + 1 == len(keys):
                if match_type == 'exact' and array_record == value_to_check:
                    return True
                elif match_type == 'contains' and value_to_check in array_record:
                    return True
                elif match_type == 'regex'and re.search(
                        value_to_check, array_record):
                        return True
            else:
                if check_value(array_record, match_type,
                               keys, value_to_check, position + 1):
                    return True
    else:
        if position + 1 == len(keys):
            if match_type == 'exact' and temp_record == value_to_check:
                return True
            elif match_type == 'contains' and value_to_check in temp_record:
                return True
            elif match_type == 'regex' and re.search(
                    value_to_check, temp_record):
                return True
        else:
            return check_value(temp_record, match_type,
                               keys, value_to_check, position + 1)
    return False


def get_actions(user_actions):
    class_actions = []
    conditions = []
    match_type_map = {
        'contains': 'contains',
        'is equal to': 'exact',
        'does not exist': 'missing',
        'matches regular expression': 'regex'
    }
    if not user_actions:
        return

    for action in user_actions.get('conditions', []):
        if not action.get('key'):
            continue
        keys = action['key'].split('/')
        condition = {'value': action['value'],
                     'keys': keys,
                     'match_type': match_type_map[action['matchType']]}
        conditions.append(condition)

    for user_action in user_actions.get('actions', []):
        if not user_action.get('mainKey'):
            continue
        keys = user_action.get('mainKey').split('/')
        if not keys:
            return
        if user_action.get('actionName') == 'Addition':
            class_actions.append(Addition(keys=keys, value=user_action.get('value'),
                                          match_type=match_type_map[user_action.get('matchType')],
                                          conditions=conditions))
        elif user_action.get('actionName') == 'Deletion':
            class_actions.append(Deletion(keys=keys, value=user_action.get('value'),
                                          value_to_check=user_action.get('updateValue'),
                                          match_type=match_type_map[user_action.get('matchType')],
                                          conditions=conditions))
        elif user_action.get('actionName') == 'Update':
            class_actions.append(Update(keys=keys, value=user_action.get('value'),
                                        match_type=match_type_map[user_action.get('matchType')],
                                        value_to_check=user_action.get('updateValue'),
                                        conditions=conditions))
    return class_actions


def process_records_no_db(user_actions, records, schema):  # fixme name convention
    class_actions = get_actions(user_actions)
    for record in records:
        for class_action in class_actions:
            class_action.apply_action(record, schema)
    return records
