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

import pytest
from jsonschema import ValidationError

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.upload import set_schema

from mocks import MockObj, MockEng


def test_set_schema_adds_a_schema_from_the_obj_data_type():
    schema = load_schema('hep')
    subschema = schema['properties']['$schema']

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data, data_type='hep')
    eng = MockEng()

    assert set_schema(obj, eng) is None

    expected = 'http://localhost:5000/schemas/records/hep.json'
    result = obj.data

    assert validate(result['$schema'], subschema) is None
    assert expected == result['$schema']


def test_set_schema_adds_a_schema_from_the_eng_data_type():
    schema = load_schema('hep')
    subschema = schema['properties']['$schema']

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng(data_type='hep')

    assert set_schema(obj, eng) is None

    expected = 'http://localhost:5000/schemas/records/hep.json'
    result = obj.data

    assert validate(result['$schema'], subschema) is None
    assert expected == result['$schema']


def test_set_schema_builds_a_full_url_for_the_schema():
    schema = load_schema('hep')
    subschema = schema['properties']['$schema']

    data = {'$schema': 'hep.json'}
    extra_data = {}
    # XXX: this violates the usual workflow invariant (valid in, valid out),
    # but we can't really do otherwise, as inspire-dojson does not know the
    # actual SERVER_NAME.
    with pytest.raises(ValidationError):
        validate(data['$schema'], subschema)

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_schema(obj, eng) is None

    expected = 'http://localhost:5000/schemas/records/hep.json'
    result = obj.data

    assert validate(result['$schema'], subschema) is None
    assert expected == result['$schema']


def test_set_schema_does_nothing_when_the_schema_url_is_already_full():
    schema = load_schema('hep')
    subschema = schema['properties']['$schema']

    data = {'$schema': 'http://localhost:5000/schemas/records/hep.json'}
    extra_data = {}
    assert validate(data['$schema'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_schema(obj, eng) is None

    expected = 'http://localhost:5000/schemas/records/hep.json'
    result = obj.data

    assert validate(result['$schema'], subschema) is None
    assert expected == result['$schema']
