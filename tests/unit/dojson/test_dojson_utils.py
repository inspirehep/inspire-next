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
    create_profile_url,
    get_recid_from_ref,
    get_record_ref,
    legacy_export_as_marc,
    strip_empty_values,
)


def test_create_profile_url_returns_link_when_given_an_int():
    expected = 'http://inspirehep.net/record/1010819'
    result = create_profile_url('1010819')

    assert expected == result


def test_create_profile_url_returns_empty_string_when_not_given_an_int():
    expected = ''
    result = create_profile_url('foo')

    assert expected == result


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


# TODO: test legacy_export_as_marc


# TODO: test strip_empty_values
