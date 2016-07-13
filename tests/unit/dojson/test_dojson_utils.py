# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import mock

from inspirehep.dojson.utils import (
    force_force_list,
    classify_field,
    classify_rank,
    create_profile_url,
    force_single_element,
    get_int_value,
    get_recid_from_ref,
    get_record_ref,
    legacy_export_as_marc,
    dedupe_all_lists,
)


def test_force_force_list_returns_empty_list_on_none():
    expected = []
    result = force_force_list(None)

    assert expected == result


def test_force_force_list_wraps_strings_in_a_list():
    expected = ['foo']
    result = force_force_list('foo')

    assert expected == result


def test_force_force_list_converts_tuples_to_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_force_list(('foo', 'bar', 'baz'))

    assert expected == result


def test_classify_field_returns_none_on_falsy_value():
    assert classify_field('') is None


def test_classify_field_returns_none_on_non_string_value():
    assert classify_field(0) is None


def test_classify_field_returns_category_if_found_among_keys():
    expected = 'Math and Math Physics'
    result = classify_field('alg-geom')

    assert expected == result


def test_classify_field_returns_category_if_found_among_values():
    expected = 'Astrophysics'
    result = classify_field('Astrophysics')

    assert expected == result


def test_classify_field_ignores_case():
    expected = 'Astrophysics'
    result = classify_field('ASTRO-PH.CO')

    assert expected == result


def test_classify_field_falls_back_on_other():
    expected = 'Other'
    result = classify_field('FOO')

    assert expected == result


def test_classify_rank_returns_none_on_falsy_value():
    assert classify_rank('') is None


def test_classify_rank_returns_none_on_non_string_value():
    assert classify_rank(0) is None


def test_classify_rank_returns_uppercase_value_if_found_in_rank_types():
    expected = 'STAFF'
    result = classify_rank('staff')

    assert expected == result


def test_classify_rank_ignores_periods_in_value():
    expected = 'PHD'
    result = classify_rank('Ph.D.')

    assert expected == result


def test_classify_rank_allows_alternative_names():
    expected = 'VISITOR'
    result = classify_rank('VISITING SCIENTIST')

    assert expected == result


def test_classify_rank_allows_abbreviations():
    expected = 'POSTDOC'
    result = classify_rank('PD')

    assert expected == result


def test_classify_rank_falls_back_on_other():
    expected = 'OTHER'
    result = classify_rank('FOO')

    assert expected == result


def test_create_profile_url_returns_link_when_given_an_int():
    expected = 'http://inspirehep.net/record/1010819'
    result = create_profile_url('1010819')

    assert expected == result


def test_create_profile_url_returns_empty_string_when_not_given_an_int():
    expected = ''
    result = create_profile_url('foo')

    assert expected == result


def test_force_single_element_returns_first_element_on_a_list():
    expected = 'foo'
    result = force_single_element(['foo', 'bar', 'baz'])

    assert expected == result


def test_force_single_element_returns_element_when_not_a_list():
    expected = 'foo'
    result = force_single_element('foo')

    assert expected == result


def test_force_single_element_returns_none_on_empty_list():
    assert force_single_element([]) is None


def test_get_int_value_returns_int_with_valid_input():
    assert get_int_value({'0': '1343079'}, '0') == 1343079


def test_get_int_value_returns_none_with_empty_string():
    assert get_int_value({'0': ''}, '0') is None


def test_get_int_value_returns_none_with_invalid_input():
    assert get_int_value({'0': 'p15:*'}, '0') is None


def test_get_int_value_returns_none_when_key_is_not_present():
    assert get_int_value({'y': '2015'}, 'u') is None


def test_get_int_value_returns_none_when_value_is_a_tuple():
    assert get_int_value({'y': ('2015', '2016')}, 'y') is None


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_with_empty_server_name(current_app):
    current_app.config = {}

    expected = 'http://inspirehep.net/api/record_type/123'
    result = get_record_ref(123, 'record_type')

    assert expected == result['$ref']


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_with_server_name_localhost(current_app):
    current_app.config = {'SERVER_NAME': 'localhost:5000'}

    expected = 'http://localhost:5000/api/record_type/123'
    result = get_record_ref(123, 'record_type')

    assert expected == result['$ref']


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_with_http_server_name(current_app):
    current_app.config = {'SERVER_NAME': 'http://example.com'}

    expected = 'http://example.com/api/record_type/123'
    result = get_record_ref(123, 'record_type')

    assert expected == result['$ref']


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_with_https_server_name(current_app):
    current_app.config = {'SERVER_NAME': 'https://example.com'}

    expected = 'https://example.com/api/record_type/123'
    result = get_record_ref(123, 'record_type')

    assert expected == result['$ref']


def test_get_record_ref_without_recid_returns_none():
    assert get_record_ref(None, 'record_type') is None


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_without_record_type_defaults_to_record(current_app):
    current_app.config = {}

    expected = 'http://inspirehep.net/api/record/123'
    result = get_record_ref(123)

    assert expected == result['$ref']


def test_get_recid_from_ref_returns_none_on_none():
    assert get_recid_from_ref(None) is None


def test_get_recid_from_ref_returns_none_on_simple_strings():
    assert get_recid_from_ref('a_string') is None


def test_get_recid_from_ref_returns_none_on_empty_object():
    assert get_recid_from_ref({}) is None


def test_get_recid_from_ref_returns_none_on_object_with_wrong_key():
    assert get_recid_from_ref({'bad_key': 'some_val'}) is None


def test_get_recid_from_ref_returns_none_on_ref_a_simple_string():
    assert get_recid_from_ref({'$ref': 'a_string'}) is None


def test_get_recid_from_ref_returns_none_on_ref_malformed():
    assert get_recid_from_ref({'$ref': 'http://bad_url'}) is None


def test_legacy_export_as_marc_empty_json():
    empty_json = {}

    expected = '<record>\n</record>\n'
    result = legacy_export_as_marc(empty_json)

    assert expected == result


def test_legacy_export_as_marc_falsy_value():
    falsy_value = {'001': ''}

    expected = '<record>\n</record>\n'
    result = legacy_export_as_marc(falsy_value)

    assert expected == result


def test_legacy_export_as_marc_json_with_controlfield():
    json_with_controlfield = {'001': '4328'}

    expected = (
        '<record>\n'
        '    <controlfield tag="001">4328</controlfield>\n'
        '</record>\n'
    )
    result = legacy_export_as_marc(json_with_controlfield)

    assert expected == result


def test_dedupe_all_lists():
    obj = {'l0': range(10) + range(10),
           'o1': [{'foo': 'bar'}] * 10,
           'o2': [{'foo': [1, 2]}, {'foo': [1, 1, 2]}] * 10}

    expected = {'l0': range(10),
                'o1': [{'foo': 'bar'}],
                'o2': [{'foo': [1, 2]}]}

    assert dedupe_all_lists(obj) == expected


# TODO: test legacy_export_as_marc


# TODO: test strip_empty_values
