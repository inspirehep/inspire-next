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

from inspire_schemas.utils import load_schema
from inspirehep.dojson.utils import validate
from inspirehep.modules.records.receivers import (
    dates_validator,
    earliest_date,
    match_valid_experiments,
    populate_inspire_document_type,
    populate_recid_from_ref,
    references_validator,
    populate_abstract_source_suggest,
    populate_title_suggest
)


def test_dates_validator_does_nothing_when_dates_are_valid():
    json_dict = {
        'opening_date': '1993-02-02',
        'closing_date': '1993-02-02',
        'deadline_date': '1993-02-02',
    }

    dates_validator(None, json_dict)

    assert json_dict['opening_date'] == '1993-02-02'
    assert json_dict['closing_date'] == '1993-02-02'
    assert json_dict['deadline_date'] == '1993-02-02'


@mock.patch('inspirehep.modules.records.receivers.current_app.logger.warning')
def test_dates_validator_warns_when_date_is_invalid(warning):
    json_dict = {
        'control_number': 123,
        'opening_date': 'bar',
    }

    dates_validator(None, json_dict)

    warning.assert_called_once_with(
        'MALFORMED: %s value in %s: %s', 'opening_date', 123, 'bar')


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


def test_match_valid_experiments_adds_facet_experiment():
    json_dict = {
        'accelerator_experiments': [
            {'experiment': 'CERN-LHC-ATLAS'},
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': 'CERN-LHC-ATLAS',
            'facet_experiment': [['CERN-LHC-ATLAS']],
        },
    ]


def test_match_valid_experiments_ignores_case():
    json_dict = {
        'accelerator_experiments': [
            {'experiment': 'cern-lhc-cms'},
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': 'cern-lhc-cms',
            'facet_experiment': [['CERN-LHC-CMS']],
        },
    ]


def test_match_valid_experiments_ignores_spaces():
    json_dict = {
        'accelerator_experiments': [
            {'experiment': 'JeffersonLab'},
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': 'JeffersonLab',
            'facet_experiment': [['Jefferson Lab']],
        },
    ]


def test_match_valid_experiments_accepts_unknown_experiments():
    json_dict = {
        'accelerator_experiments': [
            {'experiment': 'NOT-THERE'},
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': 'NOT-THERE',
            'facet_experiment': [['NOT-THERE']],
        },
    ]


def test_match_valid_experiments_accepts_lists_of_experiments():
    json_dict = {
        'accelerator_experiments': [
            {
                'experiment': [
                    'CERN-LHC-ATLAS',
                    'CERN-LHC-CMS',
                ],
            },
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': [
                'CERN-LHC-ATLAS',
                'CERN-LHC-CMS',
            ],
            'facet_experiment': [
                [
                    'CERN-LHC-ATLAS',
                    'CERN-LHC-CMS',
                ],
            ],
        },
    ]


def test_match_valid_experiments_accepts_lists_of_accelerator_experiments():
    json_dict = {
        'accelerator_experiments': [
            {'experiment': 'CERN-LHC-ATLAS'},
            {'experiment': 'CERN-LHC-CMS'},
        ],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == [
        {
            'experiment': 'CERN-LHC-ATLAS',
            'facet_experiment': [['CERN-LHC-ATLAS']],
        },
        {
            'experiment': 'CERN-LHC-CMS',
            'facet_experiment': [['CERN-LHC-CMS']],
        },
    ]


def test_match_valid_experiments_does_nothing_on_missing_key():
    json_dict = {}

    match_valid_experiments(None, json_dict)

    assert 'accelerator_experiments' not in json_dict


def test_match_valid_experiments_does_nothing_on_empty_list():
    json_dict = {'accelerator_experiments': []}

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == []


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


def test_references_validator_does_nothing_on_missing_key():
    json_dict = {}

    references_validator(None, json_dict)

    assert 'references' not in json_dict


def test_references_validator_does_nothing_on_empty_list():
    json_dict = {
        'references': [],
    }

    references_validator(None, json_dict)

    assert json_dict['references'] == []


def test_references_validator_does_nothing_on_numerical_recids():
    json_dict = {
        'references': [
            {'recid': 123},
            {'recid': 456},
        ],
    }

    references_validator(None, json_dict)

    assert json_dict['references'] == [
        {'recid': 123},
        {'recid': 456},
    ]


@mock.patch('inspirehep.modules.records.receivers.current_app.logger.warning')
def test_references_validator_removes_and_warns_on_non_numerical_recids(warning):
    json_dict = {
        'control_number': 123,
        'references': [
            {'recid': 'foo'},
            {'recid': 456},
        ],
    }

    references_validator(None, json_dict)

    warning.assert_called_once_with(
        'MALFORMED: recid value found in references of %s: %s', 123, 'foo')
    assert json_dict['references'] == [
        {},
        {'recid': 456},
    ]


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
    subschema_journal_titles = schema['properties']['journal_titles']
    subschema_short_titles = schema['properties']['short_titles']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_titles': [{'title': 'The Journal of High Energy Physics (JHEP)'}],
        'short_titles': [{'title': 'JHEP'}],
        'title_variants': [{'title': 'JOURNAL OF HIGH ENERGY PHYSICS'}],
    }
    assert validate(record['journal_titles'], subschema_journal_titles) is None
    assert validate(record['short_titles'], subschema_short_titles) is None
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


def test_populate_title_suggest_without_short_titles():
    schema = load_schema('journals')
    subschema_journal_titles = schema['properties']['journal_titles']
    subschema_short_titles = schema['properties']['short_titles']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_titles': [{'title': 'The Journal of High Energy Physics (JHEP)'}],
        'short_titles': [],
        'title_variants': [{'title': 'JOURNAL OF HIGH ENERGY PHYSICS'}],
    }
    assert validate(record['journal_titles'], subschema_journal_titles) is None
    assert validate(record['short_titles'], subschema_short_titles) is None
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
    subschema_journal_titles = schema['properties']['journal_titles']
    subschema_short_titles = schema['properties']['short_titles']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_titles': [{'title': 'The Journal of High Energy Physics (JHEP)'}],
        'short_titles': [{'title': 'JHEP'}],
        'title_variants': [],
    }
    assert validate(record['journal_titles'], subschema_journal_titles) is None
    assert validate(record['short_titles'], subschema_short_titles) is None
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
    subschema_journal_titles = schema['properties']['journal_titles']
    subschema_short_titles = schema['properties']['short_titles']
    subschema_title_variants = schema['properties']['title_variants']

    record = {
        '$schema': 'http://localhost:5000/schemas/records/journals.json',
        'journal_titles': [],
        'short_titles': [{'title': 'JHEP'}],
        'title_variants': [{'title': 'JOURNAL OF HIGH ENERGY PHYSICS'}],
    }
    assert validate(record['journal_titles'], subschema_journal_titles) is None
    assert validate(record['short_titles'], subschema_short_titles) is None
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
