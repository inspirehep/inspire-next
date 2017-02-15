#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

'''Validator classes for Invenio Record Editor.'''

from __future__ import absolute_import, division, print_function
from .helpers import (
    check_if_field_exists_in_dict_list_x_times,
    check_field_values_not_in_required_values_for_record,
    FIELD_REQUIRE_FIELD_VALUES_TEMPLATE,
    check_if_listfield_property_values_are_valid,
    query_db_for_duplicates_for_field_listitem_with_index,
    FIELD_VALIDATION_TEMPLATE
)
from jsonschema import ValidationError
from idutils import is_isbn
import pycountry
from collections import deque


'''
Error Validator Functions
'''


def check_for_author_or_corporate_author_to_exist(record):
    if all(k not in record for k in ['authors', 'corporate_author']):
        yield ValidationError(path=deque(['']),
                              message='Neither an author nor a corporate author found.')


def check_document_type_if_book_series_exist(record):
    if 'book_series' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            yield ValidationError(path=deque(['']),
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='book_series',
                                      required='document_type',
                                      values=required_values))


def check_document_type_if_isbns_exist(record):
    if 'isbns' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            yield ValidationError(path=deque(['']),
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='isbns',
                                      required='document_type',
                                      values=required_values))


def check_document_type_if_cnum_exist(record):
    if check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
        required_values = ['proceedings', 'conference paper']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            yield ValidationError(path=deque(['']),
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='cnum',
                                      required='document_type',
                                      values=required_values))


def check_document_type_if_thesis_info_exist(record):

    if 'thesis_info' in record:
        required_values = ['thesis']
        if check_field_values_not_in_required_values_for_record(record, 'document_type', required_values):
            yield ValidationError(path=deque(['']),
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='thesis_info',
                                      required='document_type',
                                      values=required_values),
                                  cause='Error')


def check_if_isbn_is_valid(record):
    def _check_isbn_is_valid(field, value, prop, index, errortype):
        if not is_isbn(value):
            yield ValidationError(path=deque(['{field}/{index}/{prop}'.format(field=field,
                                                                               prop=prop,
                                                                               index=index)]),
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='isbns',
                                      value=value
                                  ),
                                  cause=errortype)

    for e in check_if_listfield_property_values_are_valid(record=record,
                                                          field='isbns',
                                                          prop='value',
                                                          checker=_check_isbn_is_valid):
        yield e


def check_if_isbn_exist_in_other_records(record):
    for e in check_if_listfield_property_values_are_valid(record=record,
                                                          field='isbns',
                                                          prop='value',
                                                          checker=query_db_for_duplicates_for_field_listitem_with_index):
        yield e


def check_languages_if_valid_iso(record):
    def _check_language(language, index):
        try:
            pycountry.languages.lookup(language)
        except LookupError:
            yield ValidationError(path=deque(['languages/{index}'.format(index=index)]),
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='languages',
                                      value=language
                                  ),
                                  cause='Error')
    for i, item in enumerate(record.get('languages', [])):
        for e in _check_language(item, i):
            yield e
