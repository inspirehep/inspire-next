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
import mock

from inspirehep.modules.records.serializers.schemas.json.literature.common import ThesisInfoSchemaV1


def test_degree_type_phd_becomes_PhD():
    schema = ThesisInfoSchemaV1()
    dump = {'degree_type': 'phd'}
    expected = {'degree_type': 'PhD'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_degree_type_titleized_if_not_phd():
    schema = ThesisInfoSchemaV1()
    dump = {'degree_type': 'diploma'}
    expected = {'degree_type': 'Diploma'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_none_fields():
    schema = ThesisInfoSchemaV1()
    dump = {}
    expected = {}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.common.thesis_info.format_date')
def test_formatted_date(format_date):
    format_date.return_value = '7 Jun 1993'
    schema = ThesisInfoSchemaV1()
    dump = {'date': '7-6-1993'}
    expected = {'date': '7 Jun 1993'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.common.thesis_info.format_date')
def test_formatted_defense_date(format_date):
    format_date.return_value = '7 Jun 1993'
    schema = ThesisInfoSchemaV1()
    dump = {'defense_date': '7-6-1993'}
    expected = {'defense_date': '7 Jun 1993'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
