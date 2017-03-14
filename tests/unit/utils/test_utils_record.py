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

from inspirehep.utils.record import (
    get_abstract,
    get_subtitle,
    get_title,
    get_value,
    is_submitted_but_not_published,
)


def test_get_abstract_returns_empty_string_when_no_abstracts():
    record = {}

    expected = ''
    result = get_abstract(record)

    assert expected == result


def test_get_abstract_returns_empty_string_when_abstracts_is_empty():
    record = {'abstracts': []}

    expected = ''
    result = get_abstract(record)

    assert expected == result


def test_get_abstract_returns_first_abstract_with_source_not_arxiv():
    record = {
        'abstracts': [
            {
                'source': 'arXiv',
                'value': 'abstract with source arXiv',
            },
            {
                'source': 'not arXiv',
                'value': 'abstract with source not arXiv',
            },
        ],
    }

    expected = 'abstract with source not arXiv'
    result = get_abstract(record)

    assert expected == result


def test_get_abstract_returns_last_abstract_without_a_source():
    record = {
        'abstracts': [
            {'value': 'first abstract without a source'},
            {'value': 'last abstract without a source'},
        ],
    }

    expected = 'last abstract without a source'
    result = get_abstract(record)

    assert expected == result


def test_get_abstract_falls_back_to_first_abstract_even_if_from_arxiv():
    record = {
        'abstracts': [
            {
                'source': 'arXiv',
                'value': 'abstract with source arXiv',
            },
        ],
    }

    expected = 'abstract with source arXiv'
    result = get_abstract(record)

    assert expected == result


def test_get_subtitle_returns_empty_string_when_no_titles():
    record = {}

    expected = ''
    result = get_subtitle(record)

    assert expected == result


def test_get_subtitle_returns_empty_string_when_titles_is_empty():
    record = {'titles': []}

    expected = ''
    result = get_subtitle(record)

    assert expected == result


def test_get_subtitle_returns_first_subtitle():
    record = {
        'titles': [
            {'subtitle': 'first subtitle'},
            {'subtitle': 'second subtitle'},
        ],
    }

    expected = 'first subtitle'
    result = get_subtitle(record)

    assert expected == result


def test_get_title_returns_empty_string_when_no_titles():
    record = {}

    expected = ''
    result = get_title(record)

    assert expected == result


def test_get_title_returns_empty_string_when_titles_is_empty():
    record = {'titles': []}

    expected = ''
    result = get_title(record)

    assert expected == result


def test_get_title_returns_first_title():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = 'first title'
    result = get_title(record)

    assert expected == result


def test_get_value_returns_all_values():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = [
        'first title',
        'second title',
    ]
    result = get_value(record, 'titles.title')

    assert expected == result


def test_get_value_allows_indexes_in_paths():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = 'second title'
    result = get_value(record, 'titles.title[1]')

    assert expected == result


def test_get_value_allows_slices_in_paths():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = [
        'first title',
        'second title',
    ]
    result = get_value(record, 'titles.title[:]')

    assert expected == result


def test_is_submitted_but_not_published_returns_false_if_record_has_dois():
    record = {
        'dois': [
            {'value': 'doi'},
        ],
    }

    assert not is_submitted_but_not_published(record)


def test_is_submitted_but_not_published_returns_true_if_record_has_at_least_one_journal_title():
    record = {
        'publication_info': [
            {'journal_title': 'journal title'},
        ],
    }

    assert is_submitted_but_not_published(record)


def test_is_submitted_but_not_published_returns_false_if_record_is_from_econf_and_has_journal_volume():
    record = {
        'publication_info': [
            {
                'journal_title': 'eConf',
                'journal_volume': 'journal volume',
            },
        ],
    }

    assert not is_submitted_but_not_published(record)


def test_is_submitted_but_not_published_returns_false_if_record_has_a_complete_publication_info():
    record = {
        'publication_info': [
            {
                'journal_title': 'journal title',
                'journal_volume': 'journal volume',
                'page_start': 'page start',
            },
        ],
    }

    assert not is_submitted_but_not_published(record)
