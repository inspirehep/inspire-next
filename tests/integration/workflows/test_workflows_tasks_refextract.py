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

from mock import patch

from inspire_schemas.api import load_schema, validate
from inspire_utils.record import get_value
from inspirehep.modules.workflows.tasks.refextract import (
    match_references,
    match_reference
)

from factories.db.invenio_records import TestRecordMetadata


def test_match_reference_for_jcap_and_jhep_config():
    """Test reference matcher for the JCAP and JHEP configuration"""

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '045',
                'journal_title': 'JHEP',
                'journal_volume': '06',
                'page_start': '045',
                'year': 2007
            }
        ],
        'titles': [
            {
                'title': 'The Strongly-Interacting Light Higgs'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    reference = {
        'reference': {
            'publication_info': {
                'artid': '045',
                'journal_title': 'JHEP',
                'journal_volume': '06',
                'page_start': '045',
                'year': 2007
            }
        }
    }

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate([reference], subschema) is None
    reference = match_reference(reference)

    assert reference['record']['$ref'] == 'http://localhost:5000/api/literature/1'
    assert validate([reference], subschema) is None


def test_match_reference_for_data_config():
    """Test reference matcher for the JCAP and JHEP configuration"""

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/data.json',
        '_collections': ['Data'],
        'control_number': 1,
        'dois': [
            {
                'value': '10.5281/zenodo.11020'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-data', pid_type='dat')

    reference = {
        'reference': {
            'dois': [
                '10.5281/zenodo.11020'
            ],
            'publication_info': {
                'year': 2007
            }
        }
    }

    reference = match_reference(reference)

    assert reference['record']['$ref'] == 'http://localhost:5000/api/data/1'


def test_match_references_matches_when_multiple_match_if_same_as_previous():
    """Test reference matcher for when inspire-matcher returns multiple matches
    where the matched record id is one of the previous matched record id as well"""

    original_cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '159',
                'journal_title': 'JHEP',
                'journal_volume': '03',
                'page_start': '159',
                'year': 2016
            },
            {
                'artid': '074',
                'journal_title': 'JHEP',
                'journal_volume': '05',
                'material': 'erratum',
                'page_start': '074',
                'year': 2017
            }
        ]
    }

    errata_cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 2,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '074',
                'journal_title': 'JHEP',
                'journal_volume': '05',
                'material': 'erratum',
                'page_start': '074',
                'year': 2017
            }
        ]
    }

    TestRecordMetadata.create_from_kwargs(
        json=original_cited_record_json, index_name='records-hep')

    TestRecordMetadata.create_from_kwargs(
        json=errata_cited_record_json, index_name='records-hep')

    references = [
        {
            'reference': {
                'publication_info': {
                    'artid': '159',
                    'journal_title': 'JHEP',
                    'journal_volume': '03',
                    'page_start': '159',
                    'year': 2016
                }
            }
        },
        {
            'reference': {
                'publication_info': {
                    'artid': '074',
                    'journal_title': 'JHEP',
                    'journal_volume': '05',
                    'page_start': '074',
                    'year': 2017
                }
            }
        }
    ]

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate(references, subschema) is None

    matched_references = match_references(references)

    assert matched_references[1]['record']['$ref'] == 'http://localhost:5000/api/literature/1'
    assert validate(matched_references, subschema) is None


def test_match_references_no_match_when_multiple_match_different_from_previous():
    """Test reference matcher for when inspire-matcher returns multiple matches
    where the matched record id is not the same as the previous matched record id"""

    original_cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '159',
                'journal_title': 'JHEP',
                'journal_volume': '03',
                'page_start': '159',
                'year': 2016
            },
            {
                'artid': '074',
                'journal_title': 'JHEP',
                'journal_volume': '05',
                'material': 'erratum',
                'page_start': '074',
                'year': 2017
            }
        ]
    }

    errata_cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 2,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '074',
                'journal_title': 'JHEP',
                'journal_volume': '05',
                'material': 'erratum',
                'page_start': '074',
                'year': 2017
            }
        ]
    }

    TestRecordMetadata.create_from_kwargs(
        json=original_cited_record_json, index_name='records-hep')

    TestRecordMetadata.create_from_kwargs(
        json=errata_cited_record_json, index_name='records-hep')

    references = [
        {
            'reference': {
                'publication_info': {
                    'artid': '074',
                    'journal_title': 'JHEP',
                    'journal_volume': '05',
                    'page_start': '074',
                    'year': 2017
                }
            }
        }
    ]

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate(references, subschema) is None

    references = match_references(references)

    assert get_value(references[0], 'record') is None
    assert validate(references, subschema) is None


def test_match_reference_on_texkey():
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'texkeys': [
            'Giudice:2007fh',
        ],
        'titles': [
            {
                'title': 'The Strongly-Interacting Light Higgs'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    reference = {
        'reference': {
            'texkey': 'Giudice:2007fh',
        }
    }

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate([reference], subschema) is None
    reference = match_reference(reference)

    assert reference['record']['$ref'] == 'http://localhost:5000/api/literature/1'
    assert validate([reference], subschema) is None


def test_match_reference_ignores_hidden_collections():
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['HAL Hidden'],
        'control_number': 1,
        'document_type': ['article'],
        'dois': [{
            'value': '10.1371/journal.pone.0188398',
        }],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    reference = {
        'reference': {
            'dois': ['10.1371/journal.pone.0188398'],
        }
    }

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate([reference], subschema) is None
    reference = match_reference(reference)

    assert 'record' not in reference


def test_match_reference_ignores_deleted():
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'deleted': True,
        'dois': [{
            'value': '10.1371/journal.pone.0188398',
        }],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    reference = {
        'reference': {
            'dois': ['10.1371/journal.pone.0188398'],
        }
    }

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate([reference], subschema) is None
    reference = match_reference(reference)

    assert 'record' not in reference


@patch(
    'inspirehep.modules.workflows.tasks.refextract.match',
    return_value=[
        {
            u'_score': 1.6650109,
            u'_type': u'hep',
            u'_id': u'AWRuwf9plgR0Y_yvhtt4',
            u'_source': {u'control_number': 1},
            u'_index': u'records-hep'
        },
        {
            u'_score': 3.2345618,
            u'_type': u'hep',
            u'_id': u'AWRuwf9plgR0Y_yvhtt4',
            u'_source': {u'control_number': 1},
            u'_index': u'records-hep'
        }
    ],
)
def test_match_references_finds_match_when_repeated_record_with_different_scores(
    mocked_inspire_matcher_match
):
    references = [
        {
            'reference': {
                'publication_info': {
                    'artid': '045',
                    'journal_title': 'JHEP',
                    'journal_volume': '06',
                    'page_start': '045',
                    'year': 2007
                }
            }
        }
    ]

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate(references, subschema) is None
    references = match_references(references)

    assert len(references) == 1
    assert references[0]['record']['$ref'] == 'http://localhost:5000/api/literature/1'
    assert validate(references, subschema) is None
