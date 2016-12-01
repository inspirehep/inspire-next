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

from inspirehep.modules.hal.core.tei import (
    get_first_doi,
    get_titles,
    get_typology,
    is_peer_reviewed,
    parse_authors,
    parse_publication_info,
)


def test_get_first_doi():
    record = {
        'dois': [
            {'value': 'foo'},
            {'value': 'bar'},
        ],
    }

    expected = 'foo'
    result = get_first_doi(record)

    assert expected == result


def test_get_first_doi_returns_empty_string_when_there_are_no_dois():
    record = {}

    expected = ''
    result = get_first_doi(record)

    assert expected == result


def test_get_titles():
    record = {
        'titles': [
            {'title': 'foo'},
            {'title': 'bar'},
            {'title': 'baz'},
        ],
    }

    expected = [
        {'title': 'foo'},
        {'title': 'bar'},
        {'title': 'baz'},
    ]
    result = get_titles(record)

    assert expected == result


def test_get_titles_returns_empty_list_when_record_has_no_titles():
    record = {}

    expected = []
    result = get_titles(record)

    assert expected == result


def test_get_typology_converts_document_type_to_hal_typology():
    record = {
        'document_type': [
            'conference paper',
        ],
    }

    expected = 'COMM'
    result = get_typology(record)

    assert expected == result


def test_is_peer_reviewed_returns_true_if_refereed_is_present_and_true():
    record = {'refereed': True}

    assert is_peer_reviewed(record)


def test_is_peer_reviewed_returns_false_otherwise():
    record = {}

    assert not is_peer_reviewed(record)


def test_parse_authors():
    record = {
        'authors': [
            {'full_name': 'Skachkova, A.N.'},
        ],
    }

    expected = [
        {
            'full_name': 'Skachkova, A.N.',
            'parsed_name': {
                'title': '',
                'first': 'A.N.',
                'middle': '',
                'last': 'Skachkova',
                'suffix': '',
                'nickname': '',
            },
        },
    ]
    result = parse_authors(record)

    assert expected == result


def test_parse_authors_returns_empty_list_when_record_has_no_authors():
    record = {}

    expected = []
    result = parse_authors(record)

    assert expected == result


def test_parse_authors_ignores_authors_without_a_full_name():
    record = {
        'authors': [
            {'not-full_name': 'Skachkova, A.N.'},
        ],
    }

    expected = [{'not-full_name': 'Skachkova, A.N.'}]
    result = parse_authors(record)

    assert expected == result


def test_parse_publication_info():
    record = {
        'publication_info': [
            {
                'journal_title': 'Nucl.Phys.',
                'journal_volume': '22',
                'page_start': '579',
                'page_end': '588',
                'year': 1961
            },
        ]
    }  # record/4328

    expected = {
        'issue': None,
        'name': 'Nucl.Phys.',
        'pp': '579-588',
        'type': 'journal',
        'volume': '22',
        'year': 1961,
    }
    result = parse_publication_info(record)

    assert expected == result


def test_parse_publication_info_with_artid():
    record = {
        'publication_info': [
            {
                'artid': '096003',
                'journal_title': 'Phys.Rev.',
            },
        ],
    }  # record/767534

    expected = {
        'issue': None,
        'name': 'Phys.Rev.',
        'pp': '096003',
        'type': 'journal',
        'volume': None,
        'year': None,
    }
    result = parse_publication_info(record)

    assert expected == result


def test_parse_publication_info_with_page_start_and_no_page_end():
    record = {
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'page_start': '026',
            },
        ],
    }  # record/712925

    expected = {
        'issue': None,
        'name': 'JHEP',
        'pp': '026',
        'type': 'journal',
        'volume': None,
        'year': None,
    }
    result = parse_publication_info(record)

    assert expected == result


def test_parse_publication_info_without_artid_page_start_and_page_end():
    record = {
        'publication_info': [
            {
                'journal_title': 'EPJ Web Conf.',
            },
        ],
    }  # record/1498175

    expected = {
        'issue': None,
        'name': 'EPJ Web Conf.',
        'pp': '',
        'type': 'journal',
        'volume': None,
        'year': None,
    }
    result = parse_publication_info(record)

    assert expected == result


def test_parse_publication_info_without_publication_info():
    record = {}

    expected = {}
    result = parse_publication_info(record)

    assert expected == result
