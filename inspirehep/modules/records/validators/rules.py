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

from idutils import is_isbn
from jsonschema import ValidationError
import pycountry

from .helpers import (
    check_if_field_exists_in_dict_list_x_times,
    check_document_type_values_in_required_values_for_record,
    check_if_listfield_property_values_are_valid,
    query_db_for_duplicates_for_field_listitem_with_index,
    FIELD_REQUIRE_FIELD_VALUES_TEMPLATE,
    FIELD_VALIDATION_TEMPLATE,
    FIELD_REQUIRE_FIELD_TEMPLATE
)


def check_for_author_or_corporate_author_to_exist(record):
    if all(k not in record for k in ['authors', 'corporate_author']):
        yield ValidationError(path=[''],
                              message='Neither an author nor a corporate author found.',
                              cause='Error')


def check_document_type_if_book_series_exist(record):
    if 'book_series' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if not check_document_type_values_in_required_values_for_record(record, required_values):
            yield ValidationError(path=[''],
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='book_series',
                                      required='document_type',
                                      values=required_values),
                                  cause='Error')


def check_document_type_if_isbns_exist(record):
    if 'isbns' in record:
        required_values = ['book', 'proceedings', 'thesis']
        if not check_document_type_values_in_required_values_for_record(record, required_values):
            yield ValidationError(path=[''],
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='isbns',
                                      required='document_type',
                                      values=required_values),
                                  cause='Error')


def check_document_type_if_cnum_exist(record):
    if check_if_field_exists_in_dict_list_x_times('cnum', record.get('publication_info', [])):
        required_values = ['proceedings', 'conference paper']
        if not check_document_type_values_in_required_values_for_record(record, required_values):
            yield ValidationError(path=[''],
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='cnum',
                                      required='document_type',
                                      values=required_values),
                                  cause='Error')


def check_document_type_if_thesis_info_exist(record):
    if 'thesis_info' in record:
        required_values = ['thesis']
        if not check_document_type_values_in_required_values_for_record(record, required_values):
            yield ValidationError(path=[''],
                                  message=FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                                      field='thesis_info',
                                      required='document_type',
                                      values=required_values),
                                  cause='Error')


def check_if_isbn_is_valid(record):
    def _check_isbn_is_valid(field, value, prop, index, errortype):
        if not is_isbn(value):
            yield ValidationError(path=['{field}/{index}/{prop}'.format(field=field,
                                                                        prop=prop,
                                                                        index=index)],
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='isbns',
                                      value=value
                                  ),
                                  cause=errortype)

    for error in check_if_listfield_property_values_are_valid(record=record,
                                                          field='isbns',
                                                          prop='value',
                                                          checker=_check_isbn_is_valid):
        yield error


def check_if_isbn_exist_in_other_records(record):
    for error in check_if_listfield_property_values_are_valid(record=record,
                                                          field='isbns',
                                                          prop='value',
                                                          checker=query_db_for_duplicates_for_field_listitem_with_index):
        yield error


def check_if_languages_are_valid_iso(record):
    def _check_language(language, index):
        try:
            pycountry.languages.lookup(language)
        except LookupError:
            yield ValidationError(path=['languages/{index}'.format(index=index)],
                                  message=FIELD_VALIDATION_TEMPLATE.format(
                                      field='languages',
                                      value=language
                                  ),
                                  cause='Error')
    for i, item in enumerate(record.get('languages', [])):
        for error in _check_language(item, i):
            yield error


def check_languages_if_title_translations_exist(record):
    def _check_if_language_exist(translated_title, index):
        if 'language' not in translated_title:
            yield ValidationError(path=['title_translations/{index}'.format(index=index)],
                                  message=FIELD_REQUIRE_FIELD_TEMPLATE.format(
                                      field='title_translations',
                                      required='language'
                                  ),
                                  cause='Error')

    for i, item in enumerate(record.get('title_translations', [])):
        for error in _check_if_language_exist(item, i):
            yield error
