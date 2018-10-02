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

from inspirehep.modules.records.serializers.schemas.json.literature.common import CitationItemSchemaV1


def test_returns_non_empty_fields():
    schema = CitationItemSchemaV1()
    dump = {
        'control_number': 123,
        'authors': [
            {
                'emails': ['big@chief.com'],
            },
        ],
        'publication_info': {
            'journal_title': 'Alias Investigations',
        },
        'titles': [
            {
                'title': 'Jessica Jones',
            }
        ],
        'collaborations': [
            {
                'value': 'ATLAS Team'
            },
            {
                'value': 'CMS'
            }
        ]
    }
    expected = {
        'control_number': 123,
        'authors': [
            {
                'emails': ['big@chief.com'],
            },
        ],
        'publication_info': [{
            'journal_title': 'Alias Investigations',
        }],
        'titles': [
            {
                'title': 'Jessica Jones'
            }
        ],
        'collaborations': [
            {
                'value': 'CMS'
            }
        ],
        'collaborations_with_suffix': [
            {
                'value': 'ATLAS Team'
            },
        ],
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_max_10_authors():
    schema = CitationItemSchemaV1()
    dump = {
        'control_number': 123,
        'authors': [
            {
                'emails': ['big1@chief.com'],
            },
            {
                'emails': ['big2@chief.com'],
            },
            {
                'emails': ['big3@chief.com'],
            },
            {
                'emails': ['big4@chief.com'],
            },
            {
                'emails': ['big5@chief.com'],
            },
            {
                'emails': ['big6@chief.com'],
            },
            {
                'emails': ['big7@chief.com'],
            },
            {
                'emails': ['big8@chief.com'],
            },
            {
                'emails': ['big9@chief.com'],
            },
            {
                'emails': ['big10@chief.com'],
            },
            {
                'emails': ['big11@chief.com'],
            },
        ],
    }
    expected = {
        'control_number': 123,
        'authors': [
            {
                'emails': ['big1@chief.com'],
            },
            {
                'emails': ['big2@chief.com'],
            },
            {
                'emails': ['big3@chief.com'],
            },
            {
                'emails': ['big4@chief.com'],
            },
            {
                'emails': ['big5@chief.com'],
            },
            {
                'emails': ['big6@chief.com'],
            },
            {
                'emails': ['big7@chief.com'],
            },
            {
                'emails': ['big8@chief.com'],
            },
            {
                'emails': ['big9@chief.com'],
            },
            {
                'emails': ['big10@chief.com'],
            },
        ]
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_non_empty_fields_if_some_fields_missing():
    schema = CitationItemSchemaV1()
    dump = {
        'control_number': 123,
    }
    expected = {
        'control_number': 123,
    }
    result = schema.dumps(dump).data

    assert expected == json.loads(result)
