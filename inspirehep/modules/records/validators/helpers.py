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

from __future__ import absolute_import, division, print_function

from collections import deque

from jsonschema import ValidationError

from invenio_db import db

FIELD_REQUIRE_FIELD_VALUES_TEMPLATE = "'{field}' field requires '{required}' field to have " \
                                      "at least one of the values {values}."
FIELD_REQUIRE_FIELD_TEMPLATE = "'{field}' field requires '{required}' field to exist."
FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE = "'{field}' field with value '{value}' found in more than one record."
FIELD_VALIDATION_TEMPLATE = "Field '{field}' with value '{value}' is not valid."


def check_document_type_values_in_required_values_for_record(record, required_values):
    document_type_values = record.get('document_type', [])
    return len(set(document_type_values) & set(required_values)) > 0


def check_if_field_exists_in_dict_list_x_times(field, dict_list, limit=1):
    return len([1 for item in dict_list if field in item]) == limit


def get_query_results(querystring, params={}):
    res = db.session.execute(querystring, params)
    return res


def check_if_listfield_property_values_are_valid(record, field, prop, checker, errortype='Error'):
    for i, item in enumerate(record.get(field, [])):
        if prop in item:
            for e in checker(field=field, prop=prop, value=item[prop], index=i, errortype=errortype):
                yield e


def query_db_for_duplicates_for_field_listitem_with_index(field, prop, value, index, errortype):
    queryparams = dict(field=field, prop=prop, value=value)
    querystring = "SELECT id FROM records_metadata as r, "\
                  "json_array_elements(r.json -> :field) "\
                  "as elem WHERE elem ->> :prop=:value"
    results = get_query_results(querystring, queryparams)
    if results.rowcount > 1:
        yield ValidationError(path=deque(['{field}/{index}/{prop}'.format(field=field, index=index, prop=prop)]),
                              message=FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE.format(
                                  field=field,
                                  value=value
                              ),
                              cause=errortype)
