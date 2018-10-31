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

from inspire_schemas.api import load_schema, validate
from inspire_utils.name import generate_name_variations

from inspirehep.modules.records.utils import (
    get_endpoint_from_record,
    get_pid_from_record_uri,
    populate_abstract_source_suggest,
    populate_affiliation_suggest,
    populate_author_count,
    populate_authors_full_name_unicode_normalized,
    populate_authors_name_variations,
    populate_bookautocomplete,
    populate_earliest_date,
    populate_experiment_suggest,
    populate_inspire_document_type,
    populate_recid_from_ref,
    populate_title_suggest,
    populate_number_of_references,
)


def test_populate_number_references():
    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'references': [
            {
                'reference': {
                    'label': '1'
                }
            }
        ]
    }

    populate_number_of_references(record)

    expected = 1
    result = record['number_of_references']

    assert expected == result


def test_populate_number_references_does_nothing_if_references_is_none():
    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
    }

    populate_number_of_references(record)

    assert 'number_of_references' not in record


def test_get_endpoint_from_record():
    expected = 'literature'
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json'
    }
    result = get_endpoint_from_record(record)

    assert expected == result


def test_get_endpoint_from_record_supports_relative_urls():
    expected = 'authors'
    record = {
        '$schema': 'schemas/records/authors.json'
    }
    result = get_endpoint_from_record(record)

    assert expected == result


def test_populate_earliest_date_from_preprint_date():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'preprint_date': '2014-05-29',
    }
    assert validate(record['preprint_date'], subschema) is None

    populate_earliest_date(record)

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

    populate_earliest_date(record)

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

    populate_earliest_date(record)

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

    populate_earliest_date(record)

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

    populate_earliest_date(record)

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

    populate_earliest_date(record)

    expected = '2014-09-26'
    result = record['earliest_date']

    assert expected == result


def test_populate_authors_name_variations():
    schema = load_schema('authors')

    record = {
        '$schema': 'http://localhost:5000/records/schemas/authors.json',
        'name': {'value': 'Silk, James Brian'},
        '_collections': ['Authors'],
    }
    assert validate(record, schema) is None

    populate_authors_name_variations(record)

    expected = generate_name_variations(record['name'].get('value'))
    result = record['name_variations']

    assert expected == result


def test_populate_authors_name_variations_does_nothing_if_other_schema():
    schema = load_schema('hep')

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        '_collections': ['Literature'],
        'authors': [
            {'full_name': 'Rafelski, Johann'},
        ],
        'document_type': [
            'book',
        ],
        'titles': [
            {'title': 'Relativity Matters'},
        ],
    }
    assert validate(record, schema) is None

    populate_authors_name_variations(record)

    assert 'name_variations' not in record


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

    populate_bookautocomplete(record)

    expected = {
        'input': [
            'Rafelski, Johann',
        ],
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

    populate_bookautocomplete(record)

    expected = {
        'input': [
            'Relativity Matters',
        ],
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

    populate_bookautocomplete(record)

    expected = {
        'input': [
            '2010-07-23',
        ],
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

    populate_bookautocomplete(record)

    expected = {
        'input': [
            'Springer',
        ]
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

    populate_bookautocomplete(record)

    expected = {
        'input': [
            '0201021153',
        ],
    }
    result = record['bookautocomplete']

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

    populate_experiment_suggest(record)

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
        ]
    }

    result = record['experiment_suggest']

    assert expected == result


def test_populate_inspire_document_type_from_document_type():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'document_type': ['thesis'],
    }
    assert validate(record['document_type'], subschema) is None

    populate_inspire_document_type(record)

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

    populate_inspire_document_type(record)

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

    populate_inspire_document_type(record)

    expected = [
        'article',
        'introductory',
    ]
    result = record['facet_inspire_doc_type']

    assert expected == result


def test_populate_recid_from_ref():
    json_dict = {
        'simple_key': {'$ref': 'http://x/y/1'},
        'key_with_record': {'$ref': 'http://x/y/2'},
        'record': {'$ref': 'http://x/y/3'},
        'embedded_list': [{'record': {'$ref': 'http://x/y/4'}}],
        'embedded_record': {'record': {'$ref': 'http://x/y/5'}}
    }

    populate_recid_from_ref(json_dict)

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

    populate_recid_from_ref(json_dict)

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

    populate_abstract_source_suggest(record)

    expected = [
        {
            'abstract_source_suggest': {
                'input': 'foo',
            },
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

    populate_title_suggest(record)

    expected = {
        'input': [
            'The Journal of High Energy Physics (JHEP)',
            'JHEP',
            'JOURNAL OF HIGH ENERGY PHYSICS'
        ],
    }

    result = record['title_suggest']

    assert expected == result


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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN, Geneva',
            'CERN',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
            'CERN',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'European Organization for Nuclear Research',
            'CERN',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
            u'Centre Européen de Recherches Nucléaires',
        ],
    }
    result = record['affiliation_suggest']

    assert expected == result


def test_populate_affiliation_suggest_from_name_variants_with_umr():
    schema = load_schema('institutions')
    subschema = schema['properties']['name_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/institutions.json',
        'legacy_ICN': 'CERN',
        'name_variants': [
            {'value': u'Centre Européen de Recherches Nucléaires'},
            {'value': u'UMR 2454'},
            {'value': u'umr 1234'},
            {'value': u'umr'},
        ],
    }
    assert validate(record['name_variants'], subschema) is None

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
            u'Centre Européen de Recherches Nucléaires',
            u'UMR 2454',
            u'umr 1234',
            u'umr',
            u'2454',
            u'1234',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
            '1211',
        ],
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

    populate_affiliation_suggest(record)

    expected = {
        'input': [
            'CERN',
        ],
    }
    result = record['affiliation_suggest']

    assert expected == result


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

    populate_author_count(record)

    assert record['author_count'] == 2


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

    populate_authors_full_name_unicode_normalized(record)

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


def test_get_pid_from_record_uri_happy_flow():
    record_uri = 'http://labs.inspirehep.net/api/literature/1273685'
    assert get_pid_from_record_uri(record_uri) == ('lit', '1273685')


def test_get_pid_from_record_uri_ending_slash():
    record_uri = 'http://labs.inspirehep.net/api/literature/1273685/'
    assert get_pid_from_record_uri(record_uri) == ('lit', '1273685')


def test_get_pid_from_record_uri_non_url():
    record_uri = 'non-url-string'
    assert not get_pid_from_record_uri(record_uri)
