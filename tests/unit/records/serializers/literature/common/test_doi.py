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

from inspirehep.modules.records.serializers.schemas.json.literature.common import DOISchemaV1

from marshmallow import Schema, fields


def test_returns_value_and_material_for_doi():
    schema = DOISchemaV1()
    dump = {
        'source': 'arXiv',
        'value': '10.1016/j.nuclphysb.2017.05.003',
        'material': 'publication',
    }
    expected = {
        'value': '10.1016/j.nuclphysb.2017.05.003',
        'material': 'publication',
    }
    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_same_doi_value_from_different_source_is_ignored():
    class TestSchema(Schema):
        dois = fields.Nested(
            DOISchemaV1, dump_only=True, many=True)
    schema = TestSchema()
    dump = {
        'dois': [
            {
                'value': '10.1016/j.nuclphysb.2017.05.003'
            },
            {
                'value': '10.1016/j.nuclphysb.2017.05.003',
            },
            {
                'value': '10.1093/mnras/sty2213',
            },
        ],
    }
    expected = {
        'dois': [
            {
                'value': '10.1016/j.nuclphysb.2017.05.003'
            },
            {
                'value': '10.1093/mnras/sty2213',
            },
        ],
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
