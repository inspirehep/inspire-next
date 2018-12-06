# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import json

from inspire_schemas.api import load_schema, validate

from inspirehep.modules.records.serializers.schemas.json.authors.common import PositionSchemaV1


def test_returns_display_date_if_start_and_end_date_present():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'start_date': '2000',
        'end_date': '2015',
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'display_date': '2000-2015',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_display_date_if_start_date_present_and_current_set():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'start_date': '2000',
        'current': True,
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'current': True,
        'display_date': '2000-present',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_display_date_if_only_current_set():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'current': True,
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'current': True,
        'display_date': 'present',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_display_date_if_start_date_present():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'start_date': '2000',
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'display_date': '2000',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_display_date_if_end_date_present():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'end_date': '2000',
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'display_date': '2000',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_display_date_rank_institution_and_current():
    schema = PositionSchemaV1()
    dump = {
        'institution': 'CERN',
        'current': False,
        'end_date': '2000',
        'rank': 'PHD',
    }

    position_schema = load_schema(
        'authors')['properties']['positions']['items']
    assert validate(dump, position_schema) is None

    expected = {
        'institution': 'CERN',
        'display_date': '2000',
        'rank': 'PHD',
        'current': False,
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
