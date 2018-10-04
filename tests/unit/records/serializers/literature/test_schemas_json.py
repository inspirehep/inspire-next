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
import mock

from inspirehep.modules.records.serializers.schemas.json import \
    RecordMetadataSchemaV1, LiteratureAuthorsSchemaJSONUIV1, LiteratureReferencesSchemaJSONUIV1


def test_record_metadata_schema_returns_number_of_authors():
    schema = RecordMetadataSchemaV1()
    dump = {'authors': [
        {'full_name': 'author 1'},
        {'full_name': 'author 2'}
    ]}
    expected = 2

    result = schema.dumps(dump).data
    number_of_authors = json.loads(result)['number_of_authors']
    assert expected == number_of_authors


def test_record_metadata_schema_returns_number_of_references():
    schema = RecordMetadataSchemaV1()
    dump = {'references': [
        {'reference': {'label': '1'}},
        {'reference': {'label': '2'}},
    ]}
    expected = 2

    result = schema.dumps(dump).data
    number_of_references = json.loads(result)['number_of_references']
    assert expected == number_of_references


@mock.patch('inspirehep.modules.records.serializers.schemas.json.literature.format_date')
def test_record_metadata_schema_returns_formatted_date(format_date):
    schema = RecordMetadataSchemaV1()
    dump = {'earliest_date': '11/11/2011'}
    formatted_date = 'Nov, 11, 20111'
    format_date.return_value = formatted_date
    expected = {'date': formatted_date}

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_record_metadata_schema_empty_fields():
    schema = RecordMetadataSchemaV1()
    dump = {}
    expected = {}

    result = schema.dumps(dump).data
    assert expected == json.loads(result)


def test_metadata_references_items_empty():
    schema = LiteratureReferencesSchemaJSONUIV1()
    dump = {'metadata': {'titles': [{'title': 'Jessica Jones'}]}}
    expected = {'metadata': {'references': []}}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_references_schema_without_record():
    schema = LiteratureReferencesSchemaJSONUIV1()
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
                            {
                                'full_name': 'Smith, J.',
                                'inspire_roles': ['supervisor'],
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
                        'collaborations': ['LHCb'],
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
                    'titles': [
                        {
                            'title': 'Luke Cage',
                        },
                    ],
                    'authors': [
                        {
                            'full_name': 'Hahn, F.',
                            'first_name': 'F.',
                            'last_name': 'Hahn',
                        },
                    ],
                    'urls': [
                        {
                            'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
                        }
                    ],
                    'arxiv_eprint': [
                        {
                            'value': '1607.06746'
                        }
                    ],
                    'collaborations': [
                        {
                            'value': 'LHCb'
                        }
                    ],
                    'dois': [
                        {
                            'value': '10.1088/1361-6633/aa5514'
                        }
                    ],
                },
            ]
        }
    }

    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_references_schema_missing_data():
    schema = LiteratureReferencesSchemaJSONUIV1()
    record = {
        'metadata': {
            'references': [
                {
                    'reference': {
                        'book_series': [
                            {'title': 'Cool Book Serie'},
                        ]
                    },
                },
            ],
        },
    }
    expected = {'metadata': {'references': []}}
    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_references_schema_without_references():
    schema = LiteratureReferencesSchemaJSONUIV1()
    record = {
        'metadata': {
            'titles': [
                {
                    'title': 'Jessica Jones',
                },
            ],
        },
    }
    expected = {'metadata': {'references': []}}
    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_authors_schema():
    schema = LiteratureAuthorsSchemaJSONUIV1()
    record = {
        'metadata': {
            'control_number': 123,
            'titles': [
                {
                    'title': 'Jessica Jones',
                },
            ],
            'authors': [
                {
                    'full_name': 'Frank Castle',
                },
                {
                    'full_name': 'Smith, John',
                    'inspire_roles': ['author'],
                },
                {
                    'full_name': 'Black, Joe Jr.',
                    'inspire_roles': ['editor'],
                },
                {
                    'full_name': 'Jimmy',
                    'inspire_roles': ['supervisor'],
                },
            ],
            'collaborations': [{
                'value': 'LHCb',
            }],
            'dois': [
                {
                    'value': '10.1088/1361-6633/aa5514',
                },
            ],
            'arxiv_eprints': [
                {
                    'value': '1607.06746',
                },
            ],
            'urls': [
                {
                    'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
                }
            ],
        },
    }
    expected = {
        'metadata': {
            'authors': [
                {
                    'full_name': 'Frank Castle',
                    'first_name': 'Frank Castle',
                },
                {
                    'full_name': 'Smith, John',
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'inspire_roles': ['author'],
                },
                {
                    'full_name': 'Black, Joe Jr.',
                    'first_name': 'Joe Jr.',
                    'last_name': 'Black',
                    'inspire_roles': ['editor'],
                },
            ],
            'collaborations': [
                {
                    'value': 'LHCb'
                }
            ],
            'supervisors': [
                {
                    'full_name': 'Jimmy',
                    'first_name': 'Jimmy',
                    'inspire_roles': ['supervisor'],
                },
            ],
        }
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_authors_schema_without_authors():
    schema = LiteratureAuthorsSchemaJSONUIV1()
    record = {
        'metadata': {
            'control_number': 123,
            'titles': [
                {
                    'title': 'Jessica Jones',
                },
            ],
            'collaborations': [{
                'value': 'LHCb',
            }],
        },
    }
    expected = {
        'metadata': {
            'authors': [],
            'collaborations': [
                {
                    'value': 'LHCb'
                }
            ],
            'supervisors': [],
        }
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_authors_schema_without_authors_and_collaborations():
    schema = LiteratureAuthorsSchemaJSONUIV1()
    record = {
        'metadata': {
            'control_number': 123,
            'titles': [
                {
                    'title': 'Jessica Jones',
                },
            ],
        },
    }
    expected = {
        'metadata': {
            'authors': [],
            'collaborations': [],
            'supervisors': [],
        }
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result
