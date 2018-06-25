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

from inspirehep.modules.records.serializers.schemas.json import \
    ReferencesSchemaJSONUIV1


def test_metadata_references_items_empty():
    schema = ReferencesSchemaJSONUIV1()
    dump = {'metadata': {'titles': [{'title': 'Jessica Jones'}]}}
    expected = {'metadata': {'references': []}}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_references_schema_without_record():
    schema = ReferencesSchemaJSONUIV1()
    record = {
        'metadata': {
            'references': [
                {
                    'reference': {
                        'title': {
                            'title': 'Luke Cage',
                        },
                        'authors': [
                            {
                                'full_name': 'Hahn, F.'
                            },
                        ],
                        'label': '388',
                        'misc': [
                            'NA62: Technical Design Document, Dec.',
                        ],
                        'publication_info': {
                            'year': 2010,
                        },
                        'dois': [
                            '10.1088/1361-6633/aa5514',
                        ],
                        'arxiv_eprint': '1607.06746',
                        'collaborations': [
                            'LHCb',
                        ],
                        'urls': [
                            {
                                'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
                            }
                        ],
                    },
                },
            ]
        }
    }

    expected = {
        'metadata': {
            'references': [
                {
                    'label': '388',
                    'collaborations': [
                        {
                            'value': 'LHCb'
                        }
                    ],
                    'authors': [
                        {
                            'full_name': 'Hahn, F.'
                        }
                    ],
                    'dois': [
                        {
                            'value': '10.1088/1361-6633/aa5514'
                        }
                    ],
                    'titles': [
                        {
                            'title': 'Luke Cage'
                        }
                    ],
                    'arxiv_eprints': [
                        {
                            'value': '1607.06746'
                        }
                    ],
                    'urls': [
                        {
                            'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
                        }
                    ],
                },
            ]
        }
    }

    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_references_schema_missing_data():
    schema = ReferencesSchemaJSONUIV1()
    record = {
        'metadata': {
            'references': [
                {
                    'reference': {
                        'dois': [
                            '10.1088/1361-6633/aa5514',
                        ],
                        'arxiv_eprint': '1607.06746',
                        'collaborations': [
                            'LHCb',
                        ]
                    },
                },
            ],
        },
    }
    expected = {'metadata': {'references': []}}
    result = json.loads(schema.dumps(record).data)
    assert expected == result
