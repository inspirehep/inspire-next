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

from uuid import UUID

import mock

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.receivers import (
    assign_phonetic_block,
    assign_uuid,
    populate_abstract_source_suggest,
    populate_affiliation_suggest,
    populate_book_suggest,
    populate_book_series_suggest,
    populate_collaboration_suggest,
    populate_conference_suggest,
    populate_earliest_date,
    populate_experiment_suggest,
    populate_inspire_document_type,
    populate_recid_from_ref,
    populate_report_number_suggest,
    populate_title_suggest,
    populate_author_count,
    populate_authors_full_name_unicode_normalized,
)


def test_populate_book_suggest_from_authors():
    schema = load_schema('hep')
    authors_schema = schema['properties']['authors']
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Rafelski, Johann'},
        ],
        'document_type': [
            'book',
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1519486',
        },
    }
    assert validate(record['authors'], authors_schema) is None
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_book_suggest(None, record)

    expected = {
        'input': [
            'Rafelski, Johann',
        ],
        'payload': {
            'authors': [
                'Rafelski, Johann',
            ],
            'id': 'http://localhost:5000/api/literature/1519486',
            'title': [],
        },
    }
    result = record['book_suggest']

    assert expected == result


def test_populate_book_suggest_from_titles():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']
    titles_schema = schema['properties']['titles']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'book',
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1519486',
        },
        'titles': [
            {'title': 'Relativity Matters'},
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['self'], self_schema) is None
    assert validate(record['titles'], titles_schema) is None

    populate_book_suggest(None, record)

    expected = {
        'input': [
            'Relativity Matters',
        ],
        'payload': {
            'authors': [],
            'id': 'http://localhost:5000/api/literature/1519486',
            'title': [
                'Relativity Matters',
            ],
        },
    }
    result = record['book_suggest']

    assert expected == result


def test_populate_book_suggest_from_imprints_dates():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']
    imprints_schema = schema['properties']['imprints']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'book',
        ],
        'imprints': [
            {'date': '2010-07-23'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1519486',
        },
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['imprints'], imprints_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_book_suggest(None, record)

    expected = {
        'input': [
            '2010-07-23',
        ],
        'payload': {
            'authors': [],
            'id': 'http://localhost:5000/api/literature/1519486',
            'title': [],
        },
    }
    result = record['book_suggest']

    assert expected == result


def test_populate_book_suggest_from_imprints_publishers():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']
    imprints_schema = schema['properties']['imprints']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'book',
        ],
        'imprints': [
            {'publisher': 'Springer'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1519486',
        },
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['imprints'], imprints_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_book_suggest(None, record)

    expected = {
        'input': [
            'Springer',
        ],
        'payload': {
            'authors': [],
            'id': 'http://localhost:5000/api/literature/1519486',
            'title': [],
        },
    }
    result = record['book_suggest']

    assert expected == result


def test_populate_book_suggest_from_isbns_values():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']
    isbns_schema = schema['properties']['isbns']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'book',
        ],
        'isbns': [
            {'value': '0201021153'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1519486',
        },
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['isbns'], isbns_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_book_suggest(None, record)

    expected = {
        'input': [
            '0201021153',
        ],
        'payload': {
            'authors': [],
            'id': 'http://localhost:5000/api/literature/1519486',
            'title': [],
        },
    }
    result = record['book_suggest']

    assert expected == result


def test_populate_book_suggest_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_book_suggest(None, record)

    assert 'book_suggest' not in record


def test_populate_book_suggest_does_nothing_if_record_is_not_a_book():
    schema = load_schema('hep')
    authors_schema = schema['properties']['authors']
    document_type_schema = schema['properties']['document_type']
    self_schema = schema['properties']['self']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Mohayai, Tanaz Angelina'},
        ],
        'document_type': [
            'article',
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/1520027',
        }
    }
    assert validate(record['authors'], authors_schema) is None
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_book_suggest(None, record)

    assert 'book_suggest' not in record


def test_populate_book_series_suggest():
    schema = load_schema('hep')
    book_series_schema = schema['properties']['book_series']
    document_type_schema = schema['properties']['document_type']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'book',
        ],
        'book_series': [
            {
                'title': 'foo',
            },
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['book_series'], book_series_schema) is None

    populate_book_series_suggest(None, record)

    expected = [
        {
            'book_series_suggest': {
                'input': 'foo',
                'output': 'foo',
            },
            'title': 'foo',
        },
    ]
    result = record['book_series']

    assert expected == result


def test_populate_book_series_suggest_does_nothing_if_record_is_not_literature():
    schema = load_schema('hep')
    book_series_schema = schema['properties']['book_series']
    document_type_schema = schema['properties']['document_type']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'book',
        ],
        'book_series': [
            {
                'title': 'foo',
            },
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['book_series'], book_series_schema) is None

    populate_book_series_suggest(None, record)

    assert 'book_series_suggest' not in record['book_series']


def test_populate_book_series_suggest_does_nothing_if_wrong_doc_type():
    schema = load_schema('hep')
    book_series_schema = schema['properties']['book_series']
    document_type_schema = schema['properties']['document_type']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'note',
        ],
        'book_series': [
            {
                'title': 'foo',
            },
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['book_series'], book_series_schema) is None

    populate_book_series_suggest(None, record)

    expected = [
        {
            'title': 'foo',
        },
    ]
    result = record['book_series']

    assert expected == result


def test_populate_collaboration_suggest():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'collaborations': [
            {
                'value': 'foo',
            },
        ],
    }
    assert validate(record['collaborations'], subschema) is None

    populate_collaboration_suggest(None, record)

    expected = [
        {
            'collaboration_suggest': {
                'input': 'foo',
                'output': 'foo',
            },
            'value': 'foo',
        },
    ]
    result = record['collaborations']

    assert expected == result


def test_populate_collaboration_suggest_does_nothing_if_record_is_not_literature():
    schema = load_schema('hep')
    subschema = schema['properties']['collaborations']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'collaborations': [
            {
                'value': 'foo',
            },
        ],
    }
    assert validate(record['collaborations'], subschema) is None

    populate_collaboration_suggest(None, record)

    assert 'collaboration_suggest' not in record['collaborations']


def test_populate_conference_suggest():
    schema = load_schema('conferences')
    cnum_schema = schema['properties']['cnum']
    acronyms_schema = schema['properties']['acronyms']
    address_schema = schema['properties']['address']
    series_schema = schema['properties']['series']
    titles_schema = schema['properties']['titles']
    self_schema = schema['properties']['self']
    opening_date_schema = schema['properties']['opening_date']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/conferences.json',
        'cnum': 'C87-12-25',
        'acronyms': [
            'SUSY 2018',
        ],
        'address': [
            {
                'cities': ['Batavia', 'Berlin'],
                'postal_address': ['22607 Hamburg', '1293 Bern'],
            }
        ],
        'series': [
            {
                'name': 'Conf Series',
            },
        ],
        'titles': [
            {
                'source': 'A source',
                'subtitle': 'A subtitle',
                'title': 'A title',
            },
        ],
        'opening_date': '2009-03-12',
        'self': {
            '$ref': 'http://localhost:5000/api/conferences/bar'
        },
    }
    assert validate(record['cnum'], cnum_schema) is None
    assert validate(record['acronyms'], acronyms_schema) is None
    assert validate(record['address'], address_schema) is None
    assert validate(record['series'], series_schema) is None
    assert validate(record['titles'], titles_schema) is None
    assert validate(record['self'], self_schema) is None
    assert validate(record['opening_date'], opening_date_schema) is None

    populate_conference_suggest(None, record)

    expected = {
        'input': [
            'C87-12-25',
            'SUSY 2018',
            'Conf Series',
            'A source',
            'A subtitle',
            'A title',
            '2009-03-12',
            'Batavia',
            'Berlin',
            '22607 Hamburg',
            '1293 Bern',
        ],
        'output': 'C87-12-25',
        'payload': {
            '$ref': 'http://localhost:5000/api/conferences/bar',
            'city': 'Batavia',
            'opening_date': '2009-03-12',
            'title': 'A title',
        },
    }

    result = record['conference_suggest']

    assert expected == result


def test_populate_conference_suggest_does_nothing_if_record_is_not_conference():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_conference_suggest(None, record)

    assert 'conference_suggest' not in record


def test_populate_experiment_suggest_from_legacy_name():
    schema = load_schema('experiments')
    subschema = schema['properties']['legacy_name']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/experiments.json',
        'legacy_name': 'foo',
        'self': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }
    assert validate(record['legacy_name'], subschema) is None

    populate_experiment_suggest(None, record)

    expected = {
        'input': ['foo'],
        'output': 'foo',
        'payload': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }

    result = record['experiment_suggest']

    assert expected == result


def test_populate_experiment_suggest_from_legacy_name_from_long_name():
    schema = load_schema('experiments')
    subschema = schema['properties']['long_name']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/experiments.json',
        'legacy_name': 'foo',
        'long_name': 'bar',
        'self': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }
    assert validate(record['long_name'], subschema) is None

    populate_experiment_suggest(None, record)

    expected = {
        'input': ['foo', 'bar'],
        'output': 'foo',
        'payload': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }

    result = record['experiment_suggest']

    assert expected == result


def test_populate_experiment_suggest_from_legacy_name_from_name_variants():
    schema = load_schema('experiments')
    subschema = schema['properties']['name_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/experiments.json',
        'legacy_name': 'foo',
        'name_variants': [
            'bar',
            'baz',
            ],
        'self': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }
    assert validate(record['name_variants'], subschema) is None

    populate_experiment_suggest(None, record)

    expected = {
        'input': ['foo', 'bar', 'baz'],
        'output': 'foo',
        'payload': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }

    result = record['experiment_suggest']

    assert expected == result


def test_populate_experiment_suggest_does_nothing_if_record_is_not_experiment():
    schema = load_schema('experiments')
    subschema = schema['properties']['legacy_name']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/other.json',
        'legacy_name': 'foo',
        'self': {
            '$ref': 'http://localhost:5000/api/experiments/bar'
        },
    }
    assert validate(record['legacy_name'], subschema) is None

    populate_experiment_suggest(None, record)

    assert 'experiment_suggest' not in record


def test_assign_phonetic_block_handles_ascii_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Ellis, John Richard'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'signature_block': 'ELj',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_handles_unicode_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': u'Páramos, Jorge'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': u'Páramos, Jorge',
            'signature_block': 'PARANj',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetic_block_handles_jimmy():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Jimmy'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {
            'full_name': 'Jimmy',
            'signature_block': 'JANY',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_assign_phonetick_block_ignores_malformed_names():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': '** NOT A REAL NAME **'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_phonetic_block(None, record)

    expected = [
        {'full_name': '** NOT A REAL NAME **'},
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.records.receivers.uuid.uuid4')
def test_assign_uuid(mock_uuid4):
    mock_uuid4.return_value = UUID('727238f3-8ed6-40b6-97d2-dc3cd1429131')

    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {'full_name': 'Ellis, John Richard'},
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_uuid(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'uuid': '727238f3-8ed6-40b6-97d2-dc3cd1429131',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.records.receivers.uuid.uuid4')
def test_assign_uuid_does_not_touch_existing_uuids(mock_uuid4):
    mock_uuid4.return_value = UUID('727238f3-8ed6-40b6-97d2-dc3cd1429131')

    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {
                'full_name': 'Ellis, John Richard',
                'uuid': 'e14955b0-7e57-41a0-90a8-f4c64eb8f4e9',
            },
        ],
    }
    assert validate(record['authors'], subschema) is None

    assign_uuid(None, record)

    expected = [
        {
            'full_name': 'Ellis, John Richard',
            'uuid': 'e14955b0-7e57-41a0-90a8-f4c64eb8f4e9',
        },
    ]
    result = record['authors']

    assert validate(result, subschema) is None
    assert expected == result


def test_populate_earliest_date_from_preprint_date():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'preprint_date': '2014-05-29',
    }
    assert validate(record['preprint_date'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2014-05-29'
    result = record['earliest_date']

    assert expected == result


def test_populate_experiment_suggest():
    schema = load_schema('experiments')
    legacy_name_schema = schema['properties']['legacy_name']
    long_name_schema = schema['properties']['long_name']
    name_variants_schema = schema['properties']['name_variants']
    collaboration_schema = schema['properties']['collaboration']
    accelerator_schema = schema['properties']['accelerator']
    experiment_schema = schema['properties']['experiment']
    institutions_schema = schema['properties']['institutions']

    record = {
        '$schema': 'http://foo/experiments.json',
        'self': {'$ref': 'https://localhost:5000/api/experiments/bar'},
        'legacy_name': 'foo',
        'long_name': 'foobarbaz',
        'name_variants': [
            'bar',
            'baz',
        ],
        'collaboration': {
            'value': 'D0',
        },
        'accelerator': {
            'value': 'LHC',
        },
        'experiment': {
            'short_name': 'SHINE',
            'value': 'NA61',
        },
        'institutions': [
            {
                'value': 'ICN',
            },
        ],
    }

    assert validate(record['legacy_name'], legacy_name_schema) is None
    assert validate(record['long_name'], long_name_schema) is None
    assert validate(record['name_variants'], name_variants_schema) is None
    assert validate(record['collaboration'], collaboration_schema) is None
    assert validate(record['accelerator'], accelerator_schema) is None
    assert validate(record['institutions'], institutions_schema) is None
    assert validate(record['experiment'], experiment_schema) is None

    populate_experiment_suggest(None, record)

    expected = {
        'input': [
            'LHC',
            'D0',
            'SHINE',
            'NA61',
            'ICN',
            'foo',
            'foobarbaz',
            'bar',
            'baz',
        ],
        'output': 'foo',
        'payload': {
            '$ref': 'https://localhost:5000/api/experiments/bar',
        }
    }

    result = record['experiment_suggest']

    assert expected == result


def test_populate_experiment_suggest_does_nothing_if_record_is_not_experiment():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_experiment_suggest(None, record)

    assert 'experiment_suggest' not in record


def test_populate_earliest_date_from_thesis_info_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'thesis_info': {
            'date': '2008',
        },
    }
    assert validate(record['thesis_info'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2008'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_thesis_info_defense_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'thesis_info': {
            'defense_date': '2012-06-01',
        },
    }
    assert validate(record['thesis_info'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2012-06-01'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_publication_info_year():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'publication_info': [
            {'year': 2014},
        ],
    }
    assert validate(record['publication_info'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2014'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_legacy_creation_date():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_creation_date']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'legacy_creation_date': '2015-11-04',
    }
    assert validate(record['legacy_creation_date'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2015-11-04'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_imprints_date():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'imprints': [
            {'date': '2014-09-26'},
        ],
    }
    assert validate(record['imprints'], subschema) is None

    populate_earliest_date(None, record)

    expected = '2014-09-26'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_earliest_date(None, record)

    assert 'earliest_date' not in record


def test_populate_inspire_document_type_from_document_type():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': ['thesis'],
    }
    assert validate(record['document_type'], subschema) is None

    populate_inspire_document_type(None, record)

    expected = [
        'thesis',
    ]
    result = record['facet_inspire_doc_type']

    assert expected == result


def test_populate_inspire_document_type_from_refereed():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    refereed_schema = schema['properties']['refereed']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'article',
        ],
        'refereed': True,
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['refereed'], refereed_schema) is None

    populate_inspire_document_type(None, record)

    expected = [
        'article',
        'peer reviewed',
    ]
    result = record['facet_inspire_doc_type']

    assert expected == result


def test_populate_inspire_document_type_from_publication_type():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    publication_type_schema = schema['properties']['publication_type']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': [
            'article',
        ],
        'publication_type': [
            'introductory',
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['publication_type'], publication_type_schema) is None

    populate_inspire_document_type(None, record)

    expected = [
        'article',
        'introductory',
    ]
    result = record['facet_inspire_doc_type']

    assert expected == result


def test_populate_inspire_document_type_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_inspire_document_type(None, record)

    assert 'facet_inspire_doc_type' not in record


def test_populate_recid_from_ref():
    json_dict = {
        'simple_key': {'$ref': 'http://x/y/1'},
        'key_with_record': {'$ref': 'http://x/y/2'},
        'record': {'$ref': 'http://x/y/3'},
        'embedded_list': [{'record': {'$ref': 'http://x/y/4'}}],
        'embedded_record': {'record': {'$ref': 'http://x/y/5'}}
    }

    populate_recid_from_ref(None, json_dict)

    assert json_dict['simple_key_recid'] == 1
    assert json_dict['key_with_recid'] == 2
    assert json_dict['recid'] == 3
    assert json_dict['embedded_list'][0]['recid'] == 4
    assert json_dict['embedded_record']['recid'] == 5


def test_populate_recid_from_ref_handles_deleted_records():
    json_dict = {
        'deleted_records': [
            {'$ref': 'http://x/y/1'},
            {'$ref': 'http://x/y/2'},
        ],
    }

    populate_recid_from_ref(None, json_dict)

    assert json_dict['deleted_recids'] == [1, 2]


def test_populate_report_number_suggest():
    schema = load_schema('hep')
    report_numbers_schema = schema['properties']['report_numbers']
    self_schema = schema['properties']['self']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'report_numbers': [
            {
                'value': 'foo',
            },
            {
                'value': 'bar',
            },
            {
                'value': 'baz',
            },
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/bar',
        },
    }
    assert validate(record['report_numbers'], report_numbers_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_report_number_suggest(None, record)

    expected = {
        'input': ['foo', 'bar', 'baz'],
        'output': 'foo',
        'payload': {
           '$ref': 'http://localhost:5000/api/literature/bar'
        },
    }
    result = record['report_number_suggest']

    assert expected == result


def test_populate_report_number_suggest_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_report_number_suggest(None, record)

    assert 'report_number_suggest' not in record


def test_populate_abstract_source_suggest():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'abstracts': [
            {
                'source': 'foo',
                'value': 'bar',
            },
        ],
    }
    assert validate(record['abstracts'], subschema) is None

    populate_abstract_source_suggest(None, record)

    expected = [
        {
            'abstract_source_suggest': {
                'input': 'foo',
                'output': 'foo',
            },
            'source': 'foo',
            'value': 'bar',
        },
    ]
    result = record['abstracts']

    assert expected == result


def test_populate_abstract_source_suggest_does_nothing_if_record_is_not_literature():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/other.json',
        'abstracts': [
            {
                'source': 'foo',
                'value': 'bar',
            },
        ],
    }
    assert validate(record['abstracts'], subschema) is None

    populate_abstract_source_suggest(None, record)

    expected = [
        {
            'source': 'foo',
            'value': 'bar',
        },
    ]
    result = record['abstracts']

    assert expected == result


def test_populate_title_suggest():
    schema = load_schema('journals')
    journal_title_schema = schema['properties']['journal_title']
    short_title_schema = schema['properties']['short_title']
    title_variants_schema = schema['properties']['title_variants']
    self_schema = schema['properties']['self']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {'title': 'The Journal of High Energy Physics (JHEP)'},
        'short_title': 'JHEP',
        'title_variants': ['JOURNAL OF HIGH ENERGY PHYSICS'],
        'self': {
            '$ref': 'https://localhost:5000/api/journals/bar',
        },
    }
    assert validate(record['journal_title'], journal_title_schema) is None
    assert validate(record['short_title'], short_title_schema) is None
    assert validate(record['title_variants'], title_variants_schema) is None
    assert validate(record['self'], self_schema) is None

    populate_title_suggest(None, record)

    expected = {
        'input': [
            'The Journal of High Energy Physics (JHEP)',
            'JHEP',
            'JOURNAL OF HIGH ENERGY PHYSICS',
        ],
        'output': 'JHEP',
        'payload': {
            'full_title': 'The Journal of High Energy Physics (JHEP)',
            '$ref': 'https://localhost:5000/api/journals/bar',
        }
    }

    result = record['title_suggest']

    assert expected == result


def test_populate_title_suggest_does_nothing_if_record_is_not_journal():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_title_suggest(None, record)

    assert 'title_suggest' not in record


def test_populate_affiliation_suggest_from_icn():
    schema = load_schema('institutions')
    subschema = schema['properties']['ICN']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'ICN': [
            'CERN, Geneva',
        ],
        'legacy_ICN': 'CERN',
    }
    assert validate(record['ICN'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN, Geneva',
            'CERN',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [
                'CERN, Geneva',
            ],
            'institution_acronyms': [],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_institution_hierarchy_acronym():
    schema = load_schema('institutions')
    subschema = schema['properties']['institution_hierarchy']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'institution_hierarchy': [
            {'acronym': 'CERN'},
        ],
        'legacy_ICN': 'CERN',
    }
    assert validate(record['institution_hierarchy'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN',
            'CERN',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [],
            'institution_acronyms': [
                'CERN',
            ],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_institution_hierarchy_name():
    schema = load_schema('institutions')
    subschema = schema['properties']['legacy_ICN']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'institution_hierarchy': [
            {'name': 'European Organization for Nuclear Research'},
        ],
        'legacy_ICN': 'CERN',
    }
    assert validate(record['legacy_ICN'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'European Organization for Nuclear Research',
            'CERN',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [],
            'institution_acronyms': [],
            'institution_names': [
                'European Organization for Nuclear Research',
            ],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_legacy_icn():
    schema = load_schema('institutions')
    subschema = schema['properties']['legacy_ICN']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'legacy_ICN': 'CERN',
    }
    assert validate(record['legacy_ICN'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [],
            'institution_acronyms': [],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_name_variants():
    schema = load_schema('institutions')
    subschema = schema['properties']['name_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'legacy_ICN': 'CERN',
        'name_variants': [
            {'value': u'Centre Européen de Recherches Nucléaires'},
        ],
    }
    assert validate(record['name_variants'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN',
            u'Centre Européen de Recherches Nucléaires',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [],
            'institution_acronyms': [],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_postal_code():
    schema = load_schema('institutions')
    subschema = schema['properties']['addresses']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'addresses': [
            {'postal_code': '1211'},
        ],
        'legacy_ICN': 'CERN',
    }
    assert validate(record['addresses'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN',
            '1211',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': None,
            'ICN': [],
            'institution_acronyms': [],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_to_ref():
    schema = load_schema('institutions')
    subschema = schema['properties']['self']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'legacy_ICN': 'CERN',
        'self': {
            '$ref': 'http://localhost:5000/api/institutions/902725',
        },
    }
    assert validate(record['self'], subschema) is None

    populate_affiliation_suggest(None, record)

    expected = {
        'input': [
            'CERN',
        ],
        'output': 'CERN',
        'payload': {
            '$ref': 'http://localhost:5000/api/institutions/902725',
            'ICN': [],
            'institution_acronyms': [],
            'institution_names': [],
            'legacy_ICN': 'CERN',
        },
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_does_nothing_if_record_is_not_institution():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_affiliation_suggest(None, record)

    assert 'affiliation_suggest' not in record


def test_populate_author_count():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {
                'full_name': 'Smith, John',
                'inspire_roles': [
                    'author',
                ],
            },
            {
                'full_name': 'Rafelski, Johann',
                'inspire_roles': [
                    'author',
                    'editor',
                ],
            },
            {
                'full_name': 'Rohan, George',
                'inspire_roles': [
                    'author',
                    'supervisor',
                ],
            },
        ],
    }
    assert validate(record['authors'], subschema) is None

    populate_author_count(None, record)

    assert record['author_count'] == 2


def test_populate_author_count_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_author_count(None, record)

    assert 'author_count' not in record


def test_populate_authors_full_name_unicode_normalized():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'authors': [
            {
                'full_name': u'Müller, J.',
            },
            {
                'full_name': u'Muller, J.',
            },
        ],
    }
    assert validate(record['authors'], subschema) is None

    populate_authors_full_name_unicode_normalized(None, record)

    expected = [
        {
            'full_name': u'Müller, J.',
            'full_name_unicode_normalized': u'müller, j.',
        },
        {
            'full_name': u'Muller, J.',
            'full_name_unicode_normalized': u'muller, j.',
        },
    ]
    result = record['authors']

    assert expected == result


def test_populate_authors_full_name_unicode_normalized_does_nothing_if_record_is_not_literature():
    record = {
        '$schema': 'http://localhost:5000/schemas/records/other.json',
        'authors': [
            {
                'full_name': u'Müller, J.',
            },
            {
                'full_name': u'Muller, J.',
            },
        ],
    }

    populate_authors_full_name_unicode_normalized(None, record)

    expected = [
        {
            'full_name': u'Müller, J.',
        },
        {
            'full_name': u'Muller, J.',
        },
    ]
    result = record['authors']

    assert expected == result
