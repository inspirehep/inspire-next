#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Helpers for validators module."""

from invenio_db import db
from jsonschema import ValidationError
from collections import deque

FIELD_REQUIRE_FIELD_VALUES_TEMPLATE = "'{field}' field requires '{required}' field to have " \
                                      "at least one of the values {values}."
FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE = "'{field}' field with value '{value}' found in more than one record."
GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE = "SELECT id FROM records_metadata as r, " \
                                                      "json_array_elements(r.json -> '{field}') " \
                                                      "as elem WHERE elem ->> '{prop}'='{value}'"
FIELD_VALIDATION_TEMPLATE = "Field '{field}' with value '{value}' is not valid."


def check_field_values_not_in_required_values_for_record(record, field, required_values):
    document_type_values = record.get(field, [])
    common_list = [x for x in document_type_values if x in required_values]
    return not common_list


def check_if_field_exists_in_dict_list_x_times(field, dict_list, limit=1):
    return len([1 for item in dict_list if field in item]) == limit


def execute_query(querystring):
    return db.session.execute(querystring)


def get_query_results_if_exceed_limit(querystring, limit):
    res = execute_query(querystring)
    if res.rowcount > limit:
        return res
    return []


def check_if_listfield_property_values_are_valid(record, field, prop, checker, errortype='Error'):
    for i, item in enumerate(record.get(field, [])):
        if prop in item:
            for e in checker(field=field, prop=prop, value=item[prop], index=i, errortype=errortype):
                yield e


def query_db_for_duplicates_for_field_listitem_with_index(field, prop, value, index, errortype):
    querystring = GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE.format(field=field, prop=prop, value=value)
    results = get_query_results_if_exceed_limit(querystring, 1)
    if results:
        yield ValidationError(path=deque(['{field}/{index}/value'.format(field=field, index=index)]),
                              message=FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE.format(
                                  field=field,
                                  value=value
                              ),
                              cause=errortype)

