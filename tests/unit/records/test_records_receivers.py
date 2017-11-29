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
    populate_bookautocomplete,
    populate_earliest_date,
    populate_inspire_document_type,
    populate_recid_from_ref,
    populate_title_suggest,
    populate_author_count,
)


def test_populate_bookautocomplete_from_authors():
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

    populate_bookautocomplete(None, record)

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
    result = record['bookautocomplete']

    assert expected == result


def test_populate_bookautocomplete_from_titles():
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

    populate_bookautocomplete(None, record)

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
    result = record['bookautocomplete']

    assert expected == result


def test_populate_bookautocomplete_from_imprints_dates():
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

    populate_bookautocomplete(None, record)

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
    result = record['bookautocomplete']

    assert expected == result


def test_populate_bookautocomplete_from_imprints_publishers():
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

    populate_bookautocomplete(None, record)

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
    result = record['bookautocomplete']

    assert expected == result


def test_populate_bookautocomplete_from_isbns_values():
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

    populate_bookautocomplete(None, record)

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
    result = record['bookautocomplete']

    assert expected == result


def test_populate_bookautocomplete_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_bookautocomplete(None, record)

    assert 'bookautocomplete' not in record


def test_populate_bookautocomplete_does_nothing_if_record_is_not_a_book():
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

    populate_bookautocomplete(None, record)

    assert 'bookautocomplete' not in record


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


def test_populate_title_suggest_with_all_inputs():
    schema = load_schema('journals')
    journal_title_schema = schema['properties']['journal_title']
    short_title_schema = schema['properties']['short_title']
    title_variants_schema = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {'title': 'The Journal of High Energy Physics (JHEP)'},
        'short_title': 'JHEP',
        'title_variants': ['JOURNAL OF HIGH ENERGY PHYSICS'],
    }
    assert validate(record['journal_title'], journal_title_schema) is None
    assert validate(record['short_title'], short_title_schema) is None
    assert validate(record['title_variants'], title_variants_schema) is None

    populate_title_suggest(None, record)

    expected = {
        'input': [
            'The Journal of High Energy Physics (JHEP)',
            'JHEP',
            'JOURNAL OF HIGH ENERGY PHYSICS'
        ],
        'output': 'JHEP',
        'payload': {
            'full_title': 'The Journal of High Energy Physics (JHEP)'
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
