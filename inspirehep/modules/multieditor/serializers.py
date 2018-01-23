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

from .exceptions import InvalidActions
from .actions import AddProcessor, DeleteProcessor, UpdateProcessor

UI_TO_MATCHTYPE = {
    'contains': 'contains',
    'is equal to': 'exact',
    'does not exist': 'missing',
    'matches regular expression': 'regex'
}

ACTIONS_MAP = {
    'Addition': AddProcessor,
    'Deletion': DeleteProcessor,
    'Update': UpdateProcessor
}

AVAILABLE_ACTIONS = ['Addition', 'Deletion', 'Update']
AVAILABLE_ACTION_MATCHTYPES = ['contains', 'is equal to', 'matches regular expression']
AVAILABLE_CONDITION_MATCHTYPES = ['contains', 'is equal to', 'matches regular expression', 'does not exist']


def get_action_kwargs(schema, action, conditions=None):
    """
    Sanitizes the user action and serializes it in the class format
    :param action:  use action as received from the frontend
    :param conditions: conditions of action
    :return: returns the serialized action
    """
    action_kwargs = {}
    if not conditions:
        conditions = []
    keypath = action.get('mainKey', '').split('.')
    is_valid_key_path(keypath, schema)
    if action.get('matchType', '') not in AVAILABLE_ACTION_MATCHTYPES:
        raise InvalidActions('Matchtype "%s" is not a valid action matchtype,'
                             ' valid action matchtypes are %s' % (action.get('matchType', ''),
                                                                  AVAILABLE_ACTION_MATCHTYPES))
    if keypath:
        action_kwargs['keypath'] = keypath
        action_kwargs['value'] = action.get('value')
        action_kwargs['match_type'] = UI_TO_MATCHTYPE[action.get('matchType')]
        action_kwargs['conditions'] = conditions
        if action.get('updateValue'):
            action_kwargs['update_value'] = action.get('updateValue')
    return action_kwargs


def sanitize_user_conditions(user_conditions, schema):
    """
    Sanitizes the user conditions and serializes them in the class format
    :param user_conditions: user conditions as received from the frontend
    :return: returns the serialized conditions
    """
    conditions = []
    for condition in user_conditions:
        if not condition.get('key'):
            continue
        keypath = condition['key'].split('.')
        is_valid_key_path(keypath, schema)
        if condition.get('matchType', '') not in AVAILABLE_CONDITION_MATCHTYPES:
            raise InvalidActions('Matchtype "%s" is not a valid condition matchtype,'
                                 ' valid condition matchtypes are %s' % (condition.get('matchType', ''),
                                                                         AVAILABLE_CONDITION_MATCHTYPES))
        user_condition = {'value': condition.get('value', ''),
                          'keypath': keypath,
                          'match_type': UI_TO_MATCHTYPE[condition['matchType']]}
        conditions.append(user_condition)
    return conditions


def get_actions(user_actions, schema):
    """
    Serializes the user actions
    :param user_actions: actions and conditions as they were received from the frontend
    :return: returns the serialized actions
    """
    conditions = user_actions.get('conditions', [])
    if conditions:
        conditions = sanitize_user_conditions(conditions, schema)
    else:
        conditions = []
    actions = []

    for action in user_actions.get('actions', []):
        action_kwargs = get_action_kwargs(schema, action, conditions)
        if not action_kwargs:
            raise InvalidActions('No action arguments were provided')
        action_name = action.get('actionName', '')
        if action_name not in ACTIONS_MAP:
            raise InvalidActions('Action "%s" is not a valid action,'
                                 ' valid actions are %s' % (action.get('matchType', ''),
                                                            AVAILABLE_ACTIONS))
        action_cls = ACTIONS_MAP[action_name]
        new_action = action_cls(**action_kwargs)
        actions.append(new_action)
    return actions


def is_valid_key_path(keypath, schema):
    """
    Checks the validity of the keypath provided in accordance with the schema
    :param keypath: array of keys
    :param schema: schema record
    """
    for key in keypath:
        if schema['type'] == 'object':
            if schema['properties'].get(key):
                schema = schema['properties'][key]
            else:
                raise InvalidActions('The key and the schema that were provided do not match')
        elif schema['type'] == 'array':
            if schema['items']['properties'].get(key):
                schema = schema['items']['properties'][key]
            else:
                raise InvalidActions('The key and the schema that were provided do not match')
