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

from __future__ import absolute_import, division, print_function

import json

from jsonschema import validate


def test_api_v1_institutions_citesummary(app):
    schema = {
        'items': {
            'additionalProperties': False,
            'properties': {
                'citations': {
                    'items': {
                        'additionalProperties': False,
                        'properties': {
                            'collaboration': {'type': 'boolean'},
                            'core': {'type': 'boolean'},
                            'date': {
                                'format': 'date',
                                'type': 'string',
                            },
                            'document_type': {'type': 'string'},
                            'id': {'type': 'integer'},
                            'selfcite': {'type': 'boolean'},
                            'subject': {'type': 'string'},
                            'title': {'type': 'string'},
                        },
                        'required': [
                            'collaboration',
                            'core',
                            'date',
                            'document_type',
                            'id',
                            'selfcite',
                            'subject',
                            'title',
                        ],
                        'type': 'object',
                    },
                    'type': 'array',
                },
                'collaboration': {'type': 'boolean'},
                'core': {'type': 'boolean'},
                'date': {
                    'format': 'date',
                    'type': 'string',
                },
                'document_type': {'type': 'string'},
                'id': {'type': 'integer'},
                'subject': {'type': 'string'},
                'title': {'type': 'string'},
            },
            'required': [
                'citations',
                'collaboration',
                'core',
                'date',
                'document_type',
                'id',
                'subject',
                'title',
            ],
            'type': 'object',
        },
        'type': 'array',
    }

    with app.test_client() as client:
        response = client.get('/api/institutions/902725/citesummary')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert validate(response_json, schema) is None

        assert len(response_json) == 96
