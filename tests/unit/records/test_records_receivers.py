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

import mock
import requests_mock
from flask import current_app

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.receivers import (
    assign_phonetic_block,
    assign_uuid,
    earliest_date,
    generate_name_variations,
    populate_abstract_source_suggest,
    populate_affiliation_suggest,
    populate_inspire_document_type,
    populate_recid_from_ref,
    populate_title_suggest,
)


def test_phonetic_block_generation_ascii():
    json_dict = {
        'authors': [{
            'full_name': 'John Richard Ellis'
        }]
    }

    assign_phonetic_block(json_dict)

    assert json_dict['authors'][0]['signature_block'] == 'ELj'


def test_phonetic_block_generation_broken():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    extra_config = {
        'BEARD_API_URL': 'http://example.com/beard',
    }

    with mock.patch.dict(current_app.config, extra_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{base_url}/text/phonetic_blocks'.format(
                    base_url=current_app.config.get('BEARD_API_URL')),
                status_code=200,
                headers={'content-type': 'application/json'},
                json={'phonetic_blocks': {}}
            )

        json_dict = {
            'authors': [{
                'full_name': '** NOT VALID **'
            }]
        }

        assign_phonetic_block(json_dict)

        assert validate(json_dict['authors'], subschema) is None
        assert json_dict['authors'][0].get('signature_block') is None


def test_phonetic_block_generation_unicode():
    extra_config = {
        'BEARD_API_URL': 'http://example.com/beard',
    }

    with mock.patch.dict(current_app.config, extra_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{base_url}/text/phonetic_blocks'.format(
                    base_url=current_app.config.get('BEARD_API_URL')),
                status_code=200,
                headers={'content-type': 'application/json'},
                text=u'{"phonetic_blocks": {"Grzegorz Jacenków": "JACANCg"}}'
            )

        json_dict = {
            'authors': [{
                'full_name': u'Grzegorz Jacenków'
            }]
        }

        assign_phonetic_block(json_dict)

        assert json_dict['authors'][0]['signature_block'] == 'JACANCg'


def test_uuid_generation():
    json_dict = {
        'authors': [{
            'full_name': 'John Doe',
            'uuid': 'I am unique'
        }, {
            'full_name': 'John Richard Ellis'
        }]
    }

    assign_uuid(json_dict)

    # Check if the author with existing UUID has still the same UUID.
    assert(json_dict['authors'][0]['uuid'] == 'I am unique')

    # Check if the author with no UUID got one.
    assert(json_dict['authors'][1]['uuid'] is not None)


def test_earliest_date_from_preprint_date():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    record = {'preprint_date': '2014-05-29'}
    assert validate(record['preprint_date'], subschema) is None

    earliest_date(None, record)

    expected = '2014-05-29'
    result = record['earliest_date']

    assert expected == result


def test_earliest_date_from_thesis_info_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {'thesis_info': {'date': '2008'}}
    assert validate(record['thesis_info'], subschema) is None

    earliest_date(None, record)

    expected = '2008'
    result = record['earliest_date']

    assert expected == result


def test_earliest_date_from_thesis_info_defense_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {'thesis_info': {'defense_date': '2012-06-01'}}
    assert validate(record['thesis_info'], subschema) is None

    earliest_date(None, record)

    expected = '2012-06-01'
    result = record['earliest_date']

    assert expected == result


def test_earliest_date_from_publication_info_year():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        'publication_info': [
            {'year': 2014},
        ],
    }
    assert validate(record['publication_info'], subschema) is None

    earliest_date(None, record)

    expected = '2014'
    result = record['earliest_date']

    assert expected == result


def test_earliest_date_from_legacy_creation_date():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_creation_date']

    record = {'legacy_creation_date': '2015-11-04'}
    assert validate(record['legacy_creation_date'], subschema) is None

    earliest_date(None, record)

    expected = '2015-11-04'
    result = record['earliest_date']

    assert expected == result


def test_earliest_date_from_imprints_date():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    record = {
        'imprints': [
            {'date': '2014-09-26'}
        ]
    }
    assert validate(record['imprints'], subschema) is None

    earliest_date(None, record)

    expected = '2014-09-26'
    result = record['earliest_date']

    assert expected == result


def test_generate_name_variations():
    json_dict = {
        "authors": [{
            "full_name": "John Richard Ellis"
        }]
    }

    generate_name_variations(None, json_dict)

    assert(
        json_dict['authors'][0]['name_variations'] == [
            'Ellis',
            'Ellis J',
            'Ellis J R',
            'Ellis J Richard',
            'Ellis John',
            'Ellis John R',
            'Ellis John Richard',
            'Ellis R',
            'Ellis Richard',
            'Ellis, J',
            'Ellis, J R',
            'Ellis, J Richard',
            'Ellis, John',
            'Ellis, John R',
            'Ellis, John Richard',
            'Ellis, R',
            'Ellis, Richard',
            'J Ellis',
            'J R Ellis',
            'J Richard Ellis',
            'John Ellis',
            'John R Ellis',
            'John Richard Ellis',
            'R Ellis',
            'Richard Ellis'])


def test_populate_inspire_document_type_doc_type_from_refereed():
    json_dict = {
        'document_type': [
            'article',
        ],
        'refereed': True,
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'article',
        'peer reviewed',
    ]


def test_populate_inspire_document_type_doc_type_from_document_type_thesis():
    json_dict = {'document_type': ['thesis']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['thesis']


def test_populate_inspire_document_type_doc_type_from_document_type_book():
    json_dict = {'document_type': ['book']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['book']


def test_populate_inspire_document_type_doc_type_from_document_type_book_chapter():
    json_dict = {'document_type': ['book chapter']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['book chapter']


def test_populate_inspire_document_type_doc_type_from_document_type_proceedings():
    json_dict = {'document_type': ['proceedings']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['proceedings']


def test_populate_inspire_document_type_doc_type_from_document_type_conference_paper():
    json_dict = {'document_type': ['conference paper']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['conference paper']


def test_populate_inspire_document_type_doc_type_from_document_type_note():
    json_dict = {'document_type': ['note']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['note']


def test_populate_inspire_document_type_doc_type_from_document_type_report():
    json_dict = {'document_type': ['report']}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['report']


def test_populate_inspire_document_type_doc_type_from_publication_type_introductory():
    json_dict = {
        'document_type': [
            'article',
        ],
        'publication_type': [
            'introductory',
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'article',
        'introductory',
    ]


def test_populate_inspire_document_type_doc_type_from_publication_type_review():
    json_dict = {
        'document_type': [
            'article',
        ],
        'publication_type': [
            'review',
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'article',
        'review',
    ]


def test_populate_inspire_document_type_doc_type_from_publication_type_lectures():
    json_dict = {
        'document_type': [
            'article',
        ],
        'publication_type': [
            'lectures'
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'article',
        'lectures',
    ]


def test_populate_recid_from_ref_naming():
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


def test_populate_recid_from_ref_deleted_records():
    json_dict = {
        'deleted_records': [{'$ref': 'http://x/y/1'},
                            {'$ref': 'http://x/y/2'}]
    }

    populate_recid_from_ref(None, json_dict)

    assert json_dict['deleted_recids'] == [1, 2]


def test_populate_abstract_source_suggest():
    json_dict = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'abstracts': [
            {'source': 'foo'},
            {'source': 'bar'},
        ],
    }

    populate_abstract_source_suggest(None, json_dict)

    assert json_dict['abstracts'] == [
        {
            'abstract_source_suggest': {
                'input': 'foo',
                'output': 'foo',
            },
            'source': 'foo',
        },
        {
            'abstract_source_suggest': {
                'input': 'bar',
                'output': 'bar',
            },
            'source': 'bar',
        },
    ]


def test_populate_abstract_source_suggest_does_nothing_if_record_is_not_hep():
    json_dict = {
        '$schema': 'http://localhost:5000/schemas/records/other.json',
        'abstracts': [
            {'source': 'foo'},
            {'source': 'bar'},
        ],
    }

    populate_abstract_source_suggest(None, json_dict)

    assert json_dict['abstracts'] == [
        {'source': 'foo'},
        {'source': 'bar'},
    ]


def test_populate_title_suggest_with_all_inputs():
    schema = load_schema('journals')
    subschema_journal_title = schema['properties']['journal_title']
    subschema_short_title = schema['properties']['short_title']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {'title': 'The Journal of High Energy Physics (JHEP)'},
        'short_title': 'JHEP',
        'title_variants': ['JOURNAL OF HIGH ENERGY PHYSICS'],
    }
    assert validate(record['journal_title'], subschema_journal_title) is None
    assert validate(record['short_title'], subschema_short_title) is None
    assert validate(record['title_variants'], subschema_title_variants) is None

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


def test_populate_title_suggest_without_short_title():
    schema = load_schema('journals')
    subschema_journal_title = schema['properties']['journal_title']
    subschema_short_title = schema['properties']['short_title']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {'title': 'The Journal of High Energy Physics (JHEP)'},
        'short_title': '',
        'title_variants': ['JOURNAL OF HIGH ENERGY PHYSICS'],
    }
    assert validate(record['journal_title'], subschema_journal_title) is None
    assert validate(record['short_title'], subschema_short_title) is None
    assert validate(record['title_variants'], subschema_title_variants) is None

    populate_title_suggest(None, record)

    expected = {
        'input': [
            'The Journal of High Energy Physics (JHEP)',
            'JOURNAL OF HIGH ENERGY PHYSICS'
        ],
        'output': '',
        'payload': {
            'full_title': 'The Journal of High Energy Physics (JHEP)'
        }
    }

    result = record['title_suggest']

    assert expected == result


def test_populate_title_suggest_without_title_variants():
    schema = load_schema('journals')
    subschema_journal_title = schema['properties']['journal_title']
    subschema_short_title = schema['properties']['short_title']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {'title': 'The Journal of High Energy Physics (JHEP)'},
        'short_title': 'JHEP',
        'title_variants': [],
    }
    assert validate(record['journal_title'], subschema_journal_title) is None
    assert validate(record['short_title'], subschema_short_title) is None
    assert validate(record['title_variants'], subschema_title_variants) is None

    populate_title_suggest(None, record)

    expected = {
        'input': [
            'The Journal of High Energy Physics (JHEP)',
            'JHEP'
        ],
        'output': 'JHEP',
        'payload': {
            'full_title': 'The Journal of High Energy Physics (JHEP)'
        }
    }

    result = record['title_suggest']

    assert expected == result


def test_populate_title_suggest_without_full_title():
    schema = load_schema('journals')
    subschema_journal_title = schema['properties']['journal_title']
    subschema_short_title = schema['properties']['short_title']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_title': {},
        'short_title': 'JHEP',
        'title_variants': ['JOURNAL OF HIGH ENERGY PHYSICS'],
    }
    assert validate(record['journal_title'], subschema_journal_title) is None
    assert validate(record['short_title'], subschema_short_title) is None
    assert validate(record['title_variants'], subschema_title_variants) is None

    populate_title_suggest(None, record)

    expected = {
        'input': [
            "JHEP",
            "JOURNAL OF HIGH ENERGY PHYSICS"
        ],
        'output': 'JHEP',
        'payload': {
            'full_title': ''
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
            '$ref': 'api/institutions/902725',
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
            '$ref': 'api/institutions/902725',
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
