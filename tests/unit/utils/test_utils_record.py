# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tests for record-related utilities."""

from __future__ import absolute_import, division, print_function

from inspirehep.utils.record import get_abstract, get_subtitle, get_title, get_value

import pytest

from inspirehep.modules.records.api import InspireRecord


def test_get_title_returns_empty_string_when_no_titles():
    no_titles = InspireRecord({})

    expected = ''
    result = get_title(no_titles)

    assert expected == result


def test_get_subtitle_returns_empty_string_when_no_titles():
    no_titles = InspireRecord({})

    expected = ''
    result = get_subtitle(no_titles)

    assert expected == result


def test_get_abstract_returns_empty_string_when_no_titles():
    no_abstracts = InspireRecord({})

    expected = ''
    result = get_abstract(no_abstracts)

    assert expected == result


def test_get_abstract_returns_empty_string_when_abstracts_is_empty():
    empty_abstracts = InspireRecord({'abstracts': []})

    expected = ''
    result = get_abstract(empty_abstracts)

    assert expected == result


def test_get_title_returns_the_only_title():
    single_title = InspireRecord({
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
    single_subtitle = InspireRecord({
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
    single_abstract = InspireRecord({
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
    double_title = InspireRecord({
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
    double_title = InspireRecord({
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
    double_subtitle = InspireRecord({
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
    double_subtitle = InspireRecord({
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
    double_abstract = InspireRecord({
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
    double_abstract = InspireRecord({
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
    double_title = InspireRecord({
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
    double_title = InspireRecord({
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
    empty_titles = InspireRecord({'titles': []})

    expected = []
    result = get_value(empty_titles, "titles.title")

    assert expected == result


@pytest.mark.xfail(reason='Returns None instead of {}.')
def test_get_value_returns_empty_dic_when_there_are_no_titles():
    empty_titles = InspireRecord({'titles': []})

    expected = {}
    result = get_value(empty_titles, "foo")

    assert expected == result


def test_get_value_returns_none_on_index_error():
    single_title = InspireRecord({
        'titles': [
            {
                'title': 'Importance of a consistent choice of alpha(s) in the matching of AlpGen and Pythia',
            }
        ],
    })

    assert get_value(single_title, 'titles.title[1]') is None
