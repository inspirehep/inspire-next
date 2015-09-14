# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Contains INSPIRE specific filtering tasks"""

import re


def inspire_filter_custom(fields, custom_accepted=(), custom_refused=(),
                          custom_widgeted=(), action=None):
    """Allow you to filter for any type of key.

    This function allow you to filter for any type of key in a dictionary
    stored in object data.

    :param fields: list representing field to go into for filtering
                   ['a', 'b'] means that we will first look into 'a'
                   key in the dict then from 'a' key the 'b' key inside.
    :type fields: list

    :param custom_accepted: list of values that can be accepted
    :type custom_accepted: list
    :param custom_refused: list of value that must be refused
    :type custom_refused: list
    :param custom_widgeted: list of value that trigger a widget
    :type custom_widgeted: list
    :param widget: widget triggered if a value in custom_widgeted is found.
    :return: function to be intepreted by the workflow engine
    """
    def _inspire_filter_custom(obj, eng):
        custom_to_process_current = []
        custom_to_process_next = []
        action_to_take = [0, 0, 0]

        fields_to_process = fields
        if not isinstance(fields_to_process, list):
            fields_to_process = [fields_to_process]

        for field in fields_to_process:
            if len(custom_to_process_current) == 0:
                if len(fields_to_process) == 1:
                    custom_to_process_next.append(obj.data[field])
                custom_to_process_current.append(obj.data[field])
            else:
                while len(custom_to_process_current) > 0:
                    one_custom = custom_to_process_current.pop()
                    if isinstance(one_custom, list):
                        for i in one_custom:
                            custom_to_process_current.append(i)
                    else:
                        try:
                            custom_to_process_next.append(one_custom[field])
                        except KeyError:
                            eng.log.error(
                                "no " + str(field) + " in " + str(one_custom))
                custom_to_process_current = custom_to_process_next[:]
        if not custom_to_process_next:
            eng.log.error(
                "%s not found in the record.",
                fields_to_process)
            eng.halt(str(fields_to_process) +
                     " not found in the record.",
                     action=action)

        for i in custom_widgeted:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in custom_to_process_next:
                    if i.match(y):
                        action_to_take[0] += 1

        for i in custom_accepted:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in custom_to_process_next:
                    if i.match(y):
                        action_to_take[1] += 1

        for i in custom_refused:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in custom_to_process_next:
                    if i.match(y):
                        action_to_take[2] += 1

        sum_action = action_to_take[0] + action_to_take[1] + action_to_take[2]

        if sum_action == 0:
            # We allow the * option which means at final case
            if '*' in custom_widgeted:
                msg = ("Insert record?")
                eng.halt(msg, action=action)
            elif '*' in custom_refused:
                obj.extra_data["approved"] = False
            elif '*' in custom_accepted:
                obj.extra_data["approved"] = True
            else:
                # We don't know what we should do, in doubt query human...
                # they are nice!
                msg = ("Category out of task definition. "
                       "Human intervention needed")
                eng.halt(msg, action=action)
        else:
            if sum_action == action_to_take[0]:
                eng.halt("The %s of this record is %s, "
                         "this field is under filtering. "
                         "Should we accept this record ? "
                         % (fields[len(fields) - 1], custom_to_process_next),
                         action=action)
            elif sum_action == action_to_take[1]:
                obj.extra_data["approved"] = False
            elif sum_action == action_to_take[2]:
                obj.extra_data["approved"] = True
            else:
                eng.halt("Category filtering needs human intervention, "
                         "rules are incoherent !!!",
                         action=action)

    return _inspire_filter_custom


def inspire_filter_category(category_accepted_param=(),
                            category_refused_param=(),
                            category_widgeted_param=(), action_param=None):
    """Allow filtering over category of the record."""
    def _inspire_filter_category(obj, eng):
        try:
            category_accepted = \
                obj.extra_data["_repository"]["arguments"]["filtering"][
                    'category_accepted']
        except KeyError:
            category_accepted = category_accepted_param
        try:
            category_refused = \
                obj.extra_data["_repository"]["arguments"]["filtering"][
                    'category_refused']
        except KeyError:
            category_refused = category_refused_param
        try:
            category_widgeted = \
                obj.extra_data["_repository"]["arguments"]["filtering"][
                    'category_widgeted']
        except KeyError:
            category_widgeted = category_widgeted_param
        try:
            action = obj.extra_data["_repository"]["arguments"]
            action = action["filtering"]['action']
        except KeyError:
            action = action_param

        category_to_process = []
        action_to_take = [0, 0, 0]
        try:
            category = obj.data["report_number"]
            if isinstance(category, list):
                for i in category:
                    category_to_process.append(i["arxiv_category"])
            else:
                category_to_process.append(category["arxiv_category"])
            obj.add_task_result("Category filter", category_to_process)
        except KeyError:
            msg = "Category not found in the record. Human intervention needed"
            eng.log.error(msg)
            eng.halt(msg, action=action)

        for i in category_widgeted:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in category_to_process:
                    if i.match(y):
                        action_to_take[0] += 1

        for i in category_accepted:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in category_to_process:
                    if i.match(y):
                        action_to_take[1] += 1

        for i in category_refused:
            if i != '*':
                i = re.compile('^' + re.escape(i) + '.*')
                for y in category_to_process:
                    if i.match(y):
                        action_to_take[2] += 1

        sum_action = action_to_take[0] + action_to_take[1] + action_to_take[2]

        if sum_action == 0:
            # We allow the * option which means at final case
            if '*' in category_accepted:
                obj.extra_data["approved"] = True
            elif '*' in category_refused:
                obj.extra_data["approved"] = False
            else:
                # We don't know what we should do, in doubt query human...
                # they are nice!
                msg = ("Category out of task definition. "
                       "Human intervention needed")
                eng.halt(msg, action=action)
        else:
            if sum_action == action_to_take[0]:
                eng.halt("The category of this record is %s,"
                         "this category is under filtering."
                         "Should we accept this record ?" % category,
                         action=action)
            elif sum_action == action_to_take[1]:
                obj.extra_data["approved"] = True
            elif sum_action == action_to_take[2]:
                obj.extra_data["approved"] = False
            else:
                eng.halt(
                    "Category filtering needs human intervention, "
                    "rules are incoherent !!!",
                    action=action)
    return _inspire_filter_category
