# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import mock

from inspirehep.modules.records.receivers import (
    dates_validator,
    match_valid_experiments,
    normalize_field_categories,
    populate_inspire_document_type,
    populate_inspire_subjects,
    populate_recid_from_ref,
    references_validator,
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
        'control_number': 'foo',
        'opening_date': 'bar',
    }

    dates_validator(None, json_dict)

    warning.assert_called_once_with(
        'MALFORMED: %s value in %s: %s', 'opening_date', 'foo', 'bar')


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
    json_dict = {
        'accelerator_experiments': [],
    }

    match_valid_experiments(None, json_dict)

    assert json_dict['accelerator_experiments'] == []


def test_normalize_field_categories_skips_normalized_fields():
    json_dict = {
        'field_categories': [
            {'scheme': 'INSPIRE'},
            {'_scheme': 'foo'},
            {'_term': 'bar'},
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {'scheme': 'INSPIRE'},
        {'_scheme': 'foo'},
        {'_term': 'bar'},
    ]


def test_normalize_field_categories_recognizes_known_terms():
    json_dict = {
        'field_categories': [
            {
                'scheme': 'foo',
                'term': 'alg-geom',
            },
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': 'foo',
            'scheme': 'INSPIRE',
            '_term': 'alg-geom',
            'term': 'Math and Math Physics',
        },
    ]


def test_normalize_field_categories_ignores_missing_terms():
    json_dict = {
        'field_categories': [
            {'scheme': 'foo'},
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': 'foo',
            'scheme': None,
            '_term': None,
            'term': None,
        },
    ]


def test_normalize_field_categories_selects_first_scheme():
    json_dict = {
        'field_categories': [
            {'scheme': ['foo', 'bar']},
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': 'foo',
            'scheme': None,
            '_term': None,
            'term': None,
        },
    ]


def test_normalize_field_categories_ignores_unknown_terms_from_unknown_schemes():
    json_dict = {
        'field_categories': [
            {
                'scheme': 'foo',
                'term': 'bar',
            },
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': 'foo',
            'scheme': 'INSPIRE',
            '_term': 'bar',
            'term': 'Other',
        },
    ]


def test_normalize_field_categories_retains_source():
    json_dict = {
        'field_categories': [
            {'source': 'foo'},
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': None,
            'scheme': None,
            '_term': None,
            'term': None,
            'source': 'foo',
        },
    ]


def test_normalize_field_categories_changes_source_to_inspire():
    json_dict = {
        'field_categories': [
            {'source': 'automatically'},
        ],
    }

    normalize_field_categories(json_dict)

    assert json_dict['field_categories'] == [
        {
            '_scheme': None,
            'scheme': None,
            '_term': None,
            'term': None,
            'source': 'INSPIRE',
        },
    ]


def test_populate_inspire_document_type_no_doc_type_when_no_collections():
    json_dict = {}

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == []


def test_populate_inspire_document_type_no_doc_type_when_collections_empty():
    json_dict = {
        'collections': [],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['preprint']


def test_populate_inspire_document_type_no_doc_type_when_no_primary():
    json_dict = {
        'collections': [
            {'not-primary': 'foo'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['preprint']


def test_populate_inspire_document_type_doc_type_from_primary_published():
    json_dict = {
        'collections': [
            {'primary': 'published'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['peer reviewed']


def test_populate_inspire_document_type_doc_type_from_primary_thesis():
    json_dict = {
        'collections': [
            {'primary': 'thesis'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['thesis']


def test_populate_inspire_document_type_doc_type_from_primary_book():
    json_dict = {
        'collections': [
            {'primary': 'book'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['book']


def test_populate_inspire_document_type_doc_type_from_primary_bookchapter():
    json_dict = {
        'collections': [
            {'primary': 'bookchapter'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['book chapter']


def test_populate_inspire_document_type_doc_type_from_primary_proceedings():
    json_dict = {
        'collections': [
            {'primary': 'proceedings'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['proceedings']


def test_populate_inspire_document_type_doc_type_from_primary_conferencepaper():
    json_dict = {
        'collections': [
            {'primary': 'conferencepaper'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['conference paper']


def test_populate_inspire_document_type_doc_type_from_primary_note():
    json_dict = {
        'collections': [
            {'primary': 'note'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['note']


def test_populate_inspire_document_type_doc_type_from_primary_report():
    json_dict = {
        'collections': [
            {'primary': 'report'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['report']


def test_populate_inspire_document_type_doc_type_from_primary_activityreport():
    json_dict = {
        'collections': [
            {'primary': 'activityreport'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['activity report']


def test_populate_inspire_document_type_without_page_start_and_artid():
    json_dict = {
        'collections': [],
        'publication_info': [
            {
                'not-page_start': 'foo',
                'not-artid': 'bar',
            },
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['preprint']


def test_populate_inspire_document_type_with_page_start_without_artid():
    json_dict = {
        'collections': [],
        'publication_info': [
            {
                'page_start': 'foo',
                'not-artid': 'bar',
            },
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == []


def test_populate_inspire_document_type_without_page_start_with_artid():
    json_dict = {
        'collections': [],
        'publication_info': [
            {
                'not-page_start': 'foo',
                'artid': 'bar',
            },
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == []


def test_populate_inspire_document_type_with_page_start_and_artid():
    json_dict = {
        'collections': [],
        'publication_info': [
            {
                'page_start': 'foo',
                'artid': 'bar',
            },
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == []


def test_populate_inspire_document_type_no_preprint_if_valid_primary():
    json_dict = {
        'collections': [
            {'primary': 'published'},
        ],
        'publication_info': [
            {
                'not-page_start': 'foo',
                'not-artid': 'bar',
            },
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == ['peer reviewed']


def test_populate_inspire_document_type_doc_type_from_primary_review():
    json_dict = {
        'collections': [
            {'primary': 'review'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'preprint',
        'review',
    ]


def test_populate_inspire_document_type_doc_type_from_primary_lectures():
    json_dict = {
        'collections': [
            {'primary': 'lectures'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'preprint',
        'lectures',
    ]


def test_populate_inspire_document_type_doc_type_from_primary_lectures_and_review():
    json_dict = {
        'collections': [
            {'primary': 'review'},
            {'primary': 'lectures'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'preprint',
        'review',
        'lectures',
    ]


def test_populate_inspire_document_type_doc_type_from_valid_primary_and_lectures():
    json_dict = {
        'collections': [
            {'primary': 'published'},
            {'primary': 'lectures'},
        ],
    }

    populate_inspire_document_type(None, json_dict)

    assert json_dict['facet_inspire_doc_type'] == [
        'peer reviewed',
        'lectures',
    ]


def test_populate_inspire_subjects_preserves_terms_from_inspire():
    json_dict = {
        'field_categories': [
            {
                'scheme': 'INSPIRE',
                'term': 'foo',
            },
        ],
    }

    populate_inspire_subjects(None, json_dict)

    assert json_dict['facet_inspire_subjects'] == ['foo']


def test_populate_inspire_subjects_discards_terms_from_other_schemes():
    json_dict = {
        'field_categories': [
            {
                'scheme': 'foo',
                'term': 'bar',
            },
        ],
    }

    populate_inspire_subjects(None, json_dict)

    assert json_dict['facet_inspire_subjects'] == []


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
        'control_number': '123',
        'references': [
            {'recid': 'foo'},
            {'recid': 456},
        ],
    }

    references_validator(None, json_dict)

    warning.assert_called_once_with(
        'MALFORMED: recid value found in references of %s: %s', '123', 'foo')
    assert json_dict['references'] == [
        {},
        {'recid': 456},
    ]
