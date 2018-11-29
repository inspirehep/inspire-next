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

import json

from inspire_schemas.api import load_schema, validate

from inspirehep.modules.records.serializers.schemas.json import AuthorsMetadataSchemaV1


def test_authors_schema():
    schema = AuthorsMetadataSchemaV1()
    record = {
        'control_number': 123,
        'arxiv_categories': [
            'hep-ph'
        ],
        'deleted': False,
        'ids': [
            {
                'schema': 'INSPIRE BAI',
                'value': 'J.Doe.1'
            }
        ],
        'legacy_creation_date': '2013-12-21',
        'legacy_version': '20151015183913.0',
        'name': {
            'preferred_name': 'J. Doe',
            'value': 'Doe, J.'
        },
        'positions': [
            {
                'current': True,
                'institution': 'CERN',
            }
        ],
        '_collections': ['Authors'],
    }

    authors_schema = load_schema('authors')
    assert validate(record, authors_schema) is None

    expected = {
        'control_number': 123,
        'arxiv_categories': [
            'hep-ph'
        ],
        'deleted': False,
        'ids': [
            {
                'schema': 'INSPIRE BAI',
                'value': 'J.Doe.1'
            }
        ],
        'name': {
            'preferred_name': 'J. Doe',
            'value': 'Doe, J.'
        },
        'positions': [
            {
                'current': True,
                'institution': 'CERN',
            }
        ],
        'facet_author_name': 'J.Doe.1_J. Doe',
        '_collections': ['Authors'],
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result
