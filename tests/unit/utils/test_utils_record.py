# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for record-related utilities."""

from __future__ import absolute_import, print_function

from inspirehep.utils.record import (
    get_abstract,
    get_record_type,
    get_subtitle,
    get_title,
    get_value,)

from invenio_records.api import Record

import pytest


def test_get_title_returns_empty_string_when_no_titles():
    no_titles = Record({})

    expected = ''
    result = get_title(no_titles)

    assert expected == result


def test_get_subtitle_returns_empty_string_when_no_titles():
    no_titles = Record({})

    expected = ''
    result = get_subtitle(no_titles)

    assert expected == result


def test_get_abstract_returns_empty_string_when_no_titles():
    no_abstracts = Record({})

    expected = ''
    result = get_abstract(no_abstracts)

    assert expected == result


def test_get_abstract_returns_empty_string_when_abstracts_is_empty():
    empty_abstracts = Record({'abstracts': []})

    expected = ''
    result = get_abstract(empty_abstracts)

    assert expected == result


def test_get_title_returns_the_only_title():
    single_title = Record({
        'titles': [
            {
                'source': "arXiv",
                'title': 'The Large Hadron Collider'
            }
        ]
    })

    expected = 'The Large Hadron Collider'
    result = get_title(single_title)

    assert expected == result


def test_get_subtitle_returns_the_only_subtitle():
    single_subtitle = Record({
        'titles': [
            {
                "source": "arXiv",
                'subtitle': 'Harvest of Run 1'
            }
        ]
    })

    expected = 'Harvest of Run 1'
    result = get_subtitle(single_subtitle)

    assert expected == result


def test_get_abstract_returns_the_only_abstract():
    single_abstract = Record({
        "abstracts": [
            {
                "source": "arXiv",
                "value": "abstract",
            }
        ]
    })

    expected = 'abstract'
    result = get_abstract(single_abstract)

    assert expected == result


def test_get_title_returns_the_non_arxiv_title_with_source():
    double_title = Record({
        "titles": [
            {
                "source": "other",
                "title": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "source": "arXiv",
                "title": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia'
    result = get_title(double_title)

    assert expected == result


def test_get_title_returns_the_non_arxiv_title():
    double_title = Record({
        "titles": [
            {
                "title": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "source": "arXiv",
                "title": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia'
    result = get_title(double_title)

    assert expected == result


def test_get_subtitle_returns_the_non_arxiv_subtitle_with_source():
    double_subtitle = Record({
        "titles": [
            {
                "source": "other",
                "subtitle": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "source": "arXiv",
                "subtitle": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia'
    result = get_subtitle(double_subtitle)

    assert expected == result


def test_get_subtitle_returns_the_non_arxiv_subtitle():
    double_subtitle = Record({
        "titles": [
            {
                "subtitle": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "source": "arXiv",
                "subtitle": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia'
    result = get_subtitle(double_subtitle)

    assert expected == result


def test_get_abstract_returns_the_non_arxiv_abstract():
    double_abstract = Record({
        "abstracts": [
            {
                "source": "arXiv",
                "value": "arXiv abstract"
            },
            {
                "value": "abstract"
            }
        ]
    })

    expected = 'abstract'
    result = get_abstract(double_abstract)

    assert expected == result


def test_get_abstract_with_multiple_sources_returns_the_non_arxiv_abstract():
    double_abstract = Record({
        "abstracts": [
            {
                "source": "arXiv",
                "value": "arXiv abstract"
            },
            {
                "source": "other",
                "value": "abstract"
            }
        ]
    })

    expected = 'abstract'
    result = get_abstract(double_abstract)

    assert expected == result


def test_get_value_returns_the_two_titles():
    double_title = Record({
        "titles": [
            {
                "title": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "title": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 2
    result = len(get_value(double_title, "titles.title"))

    assert expected == result


def test_get_value_returns_the_selected_title():
    double_title = Record({
        "titles": [
            {
                "title": "Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia"
            },
            {
                "title": "Monte Carlo tuning in the presence of Matching"
            }
        ],
    })

    expected = 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia'
    result = get_value(double_title, "titles.title[0]")

    assert expected == result


def test_get_value_returns_single_title():
    empty_titles = Record({'titles': []})

    expected = []
    result = get_value(empty_titles, "titles.title")

    assert expected == result


@pytest.mark.xfail(reason='Returns None instead of {}.')
def test_get_value_returns_empty_dic_when_there_are_no_titles():
    empty_titles = Record({'titles': []})

    expected = {}
    result = get_value(empty_titles, "foo")

    assert expected == result


def test_get_value_returns_none_on_index_error():
    single_title = Record({
        'titles': [
            {
                'title': 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia',
            }
        ],
    })

    assert get_value(single_title, 'titles.title[1]') is None


def test_get_record_type_returns_type_for_existing_schema():
    record = Record({
        '$schema': 'http://localhost:5000/schemas/records/jobs.json'
    })

    assert get_record_type(record) == 'jobs'


@pytest.mark.xfail(reason="No information available \
                   about existing and non-existing schemas.")
def test_get_record_type_raises_error_for_nonexisting_schema():
    record = Record({
        '$schema': 'does-not-exist.json'
    })

    with pytest.raises(TypeError):
        get_record_type(record) is None


def test_get_record_type_raises_error_when_no_type():
    record = Record({})

    with pytest.raises(TypeError):
        get_record_type(record) is None
