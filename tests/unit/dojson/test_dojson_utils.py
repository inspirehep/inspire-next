# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import mock

from inspirehep.dojson import utils


@mock.patch('inspirehep.dojson.utils.current_app')
def test_get_record_ref_server_name(current_app):
    # Test empty SERVER_NAME.
    current_app.config = {}
    ref = utils.get_record_ref(123, 'record_type')
    assert ref['$ref'].startswith('http://inspirehep.net')

    # Test dev SERVER_NAME.
    current_app.config = {'SERVER_NAME': 'localhost:5000'}
    ref = utils.get_record_ref(123, 'record_type')
    assert ref['$ref'].startswith('http://localhost:5000')

    # Test http prod SERVER_NAME.
    current_app.config = {'SERVER_NAME': 'http://inspirehep.net'}
    ref = utils.get_record_ref(123, 'record_type')
    assert ref['$ref'].startswith('http://inspirehep.net')

    # Test https prod SERVER_NAME.
    current_app.config = {'SERVER_NAME': 'https://inspirehep.net'}
    ref = utils.get_record_ref(123, 'record_type')
    assert ref['$ref'].startswith('https://inspirehep.net')


def test_get_record_ref_with_record_type():
    ref = utils.get_record_ref(123, 'record_type')
    assert ref['$ref'].endswith('/api/record_type/123')
    assert utils.get_record_ref(None, 'record_type') == None


def test_get_record_ref_default():
    ref = utils.get_record_ref(123)

    assert ref['$ref'].endswith('/api/record/123')


def test_get_recid_from_ref():
    assert utils.get_recid_from_ref(None) == None
    assert utils.get_recid_from_ref('a_string') == None
    assert utils.get_recid_from_ref({}) == None
    assert utils.get_recid_from_ref({'bad_key': 'some_val'}) == None
    assert utils.get_recid_from_ref({'$ref': 'a_string'}) == None
    assert utils.get_recid_from_ref({'$ref': 'http://bad_url'}) == None


def test_remove_duplicates_from_list_preserving_order():
    """Remove duplicates from a list preserving the order."""
    list_with_duplicates = ['foo', 'bar', 'foo']

    expected = ['foo', 'bar']
    result = utils.remove_duplicates_from_list(list_with_duplicates)

    assert expected == result

def test_remove_duplicates_from_list_of_dicts_preserving_order():
    """Remove duplicates from a list of dictionaries preserving the order."""
    list_of_dicts_with_duplicates = [
        {'a': 123, 'b': 1234},
        {'a': 3222, 'b': 1234},
        {'a': 123, 'b': 1234}
    ]

    expected = [{'a': 123, 'b': 1234}, {'a': 3222, 'b': 1234}]
    result = utils.remove_duplicates_from_list_of_dicts(list_of_dicts_with_duplicates)

    assert expected == result
