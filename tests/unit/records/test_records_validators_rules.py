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

from collections import defaultdict

from inspirehep.modules.records.validators.helpers import (
    FIELD_REQUIRE_FIELD_VALUES_TEMPLATE,
    FIELD_VALIDATION_TEMPLATE,
    FIELD_REQUIRE_FIELD_TEMPLATE
)
from inspirehep.modules.records.validators.rules import (
    check_for_author_or_corporate_author_to_exist,
    check_if_isbn_is_valid,
    check_document_type_if_book_series_exist,
    check_document_type_if_isbns_exist,
    check_document_type_if_cnum_exist,
    check_document_type_if_thesis_info_exist,
    check_if_languages_are_valid_iso,
    check_languages_if_title_translations_exist
)


def format_error(_error):
    return [{
        'message': _error.message,
        'type': _error.cause or 'Error'
    }]


def json_pointer_format(path):
    path = '/' + '/'.join(str(el) for el in path)
    if path == '/':
        path = 'globalErrors'
    return path


def validate(validator_fn, record):
    result = defaultdict(list)
    for e in validator_fn(record):
        result[json_pointer_format(e.path)].extend(format_error(e))
    return result


def test_check_for_author_or_corporate_author_to_exist():
    sample_record = {
        'no_authors': {},
        'no_corporate_author': {}
    }

    expected = {
        'globalErrors': [{
            'message': 'Neither an author nor a corporate author found.',
            'type': 'Error'
        }]
    }
    result = validate(check_for_author_or_corporate_author_to_exist, sample_record)
    assert expected == result


def test_check_document_type_if_book_series_exist():
    sample_record = {
        'book_series': [{
            'key': 'value'
        }],
        'document_type': ['not_one_of_required_values']
    }
    required_values = ['book', 'proceedings', 'thesis']
    expected = {
        'globalErrors': [{
            'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                            field='book_series',
                            required='document_type',
                            values=required_values),
            'type': 'Error'
        }]
    }
    result = validate(check_document_type_if_book_series_exist, sample_record)
    assert expected == result


def test_check_document_type_if_isbns_exist():
    sample_record = {
        'isbns': [{
            'key': 'value'
        }],
        'document_type': ['not_one_of_required_values']
    }
    required_values = ['book', 'proceedings', 'thesis']
    expected = {
        'globalErrors': [{
            'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                field='isbns',
                required='document_type',
                values=required_values),
            'type': 'Error'
        }]
    }
    result = validate(check_document_type_if_isbns_exist, sample_record)
    assert expected == result


def test_check_document_type_if_cnum_exist():
    sample_record = {
        'publication_info': [{
            'cnum': 'cnum_value'
        }],
        'document_type': ['not_one_of_required_values']
    }
    required_values = ['proceedings', 'conference paper']
    expected = {
        'globalErrors': [{
            'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                field='cnum',
                required='document_type',
                values=required_values),
            'type': 'Error'
        }]
    }
    result = validate(check_document_type_if_cnum_exist, sample_record)
    assert expected == result


def test_check_document_type_if_thesis_info_exist():
    sample_record = {
        'thesis_info': {
            'key': 'value'
        },
        'document_type': ['not_one_of_required_values']
    }
    required_values = ['thesis']
    expected = {
        'globalErrors': [{
            'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
                field='thesis_info',
                required='document_type',
                values=required_values),
            'type': 'Error'
        }]
    }
    result = validate(check_document_type_if_thesis_info_exist, sample_record)
    assert expected == result


def test_check_if_isbn_is_valid():
    sample_record = {
        'isbns': [
            {
                'value': '978-3-319-15000-0'
            },
            {
                'value': '8267411'
            }
        ]
    }
    expected = {
        '/isbns/1/value': [{
            'message': FIELD_VALIDATION_TEMPLATE.format(
                field='isbns',
                value='8267411'),
            'type': 'Error'
        }]
    }
    result = validate(check_if_isbn_is_valid, sample_record)
    assert expected == result


def test_check_if_languages_are_valid_iso():
    sample_record = {
        'languages': [
            'kr',
            'z2'
        ]
    }
    expected = {
        '/languages/1': [{
            'message': FIELD_VALIDATION_TEMPLATE.format(
                field='languages',
                value='z2'
            ),
            'type': 'Error'
        }]
    }
    result = validate(check_if_languages_are_valid_iso, sample_record)
    assert expected == result


def test_check_languages_if_title_translations_exist():
    sample_record = {
        'title_translations': [
            {
                'language': 'kr'
            },
            {
                'not_langauge_field': 'value'
            }
        ]
    }
    expected = {
        '/title_translations/1': [{
            'message': FIELD_REQUIRE_FIELD_TEMPLATE.format(
                field='title_translations',
                required='language'
            ),
            'type': 'Error'
        }]
    }
    result = validate(check_languages_if_title_translations_exist, sample_record)
    assert expected == result
