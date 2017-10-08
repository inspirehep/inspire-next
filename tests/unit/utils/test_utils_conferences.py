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

from elasticsearch_dsl.result import Response
from flask import current_app
from mock import ANY, patch

from inspirehep.utils.conferences import (
    conferences_in_the_same_series_from_es,
    render_conferences,
    render_contributions,
)


@patch('inspirehep.utils.conferences.ConferencesSearch')
def test_conferences_in_the_same_series_from_es_handles_unicode(conf_search):
    conf_search().query_from_iq(ANY).params(ANY).sort(ANY).execute().hits = None
    unicode_str = u'φοο_series_name'
    assert conferences_in_the_same_series_from_es(unicode_str) is None


def test_render_conferences():
    hits = Response({
        'hits': {
            'hits': [
                {
                    '_type': 'conferences',
                    '_source': {
                        'address': [
                            {'original_address': 'original_address'},
                        ],
                        'control_number': 1,
                        'titles': [
                            {'title': 'title'},
                        ],
                    },
                },
                {
                    '_type': 'conferences',
                    '_source': {
                        'control_number': 2,
                    },
                },
            ],
            'total': 2,
        },
    }).hits

    expected = ([
        [
            '<a href="/conferences/1">title</a>',
            'original_address',
            '',
            u'  ',
        ],
    ], 1)
    with current_app.test_request_context():
        result = render_conferences(2, hits)

    assert expected == result


def test_render_conferences_handles_unicode():
    hits = Response({
        'hits': {
            'hits': [
                {
                    '_type': 'conference',
                    '_source': {
                        'address': [
                            {'original_address': 'Paris, France'},
                        ],
                        'control_number': 1351301,
                        'titles': [
                            {'title': u'Théorie de Cordes en France'},
                        ],
                    },
                },
            ],
            'total': 1,
        },
    }).hits

    expected = ([
        [
            u'<a href="/conferences/1351301">Théorie de Cordes en France</a>',
            'Paris, France',
            '',
            u'  ',
        ],
    ], 1)
    with current_app.test_request_context():
        result = render_conferences(1, hits)

    assert expected == result


def test_render_contributions():
    hits = Response({
        'hits': {
            'hits': [
                {
                    '_type': 'hep',
                    '_source': {
                        'citation_count': 1,
                        'control_number': 1,
                        'publication_info': [
                            {'journal_title': 'first-journal_title'},
                        ],
                        'titles': [
                            {'title': 'first-title'},
                        ],
                    },
                },
                {
                    '_type': 'hep',
                    '_source': {
                        'control_number': 2,
                        'titles': [
                            {'title': 'second-title'},
                        ],
                    },
                },
            ],
            'total': 2,
        },
    }).hits

    expected = ([
        [
            "<a href='/literature/1'>first-title</a>",
            u'\n\n',
            'first-journal_title',
            1,
        ],
        [
            "<a href='/literature/2'>second-title</a>",
            u'\n\n',
            '',
            0,
        ],
    ], 2)
    result = render_contributions(hits)

    assert expected == result


def test_render_contributions_handles_unicode():
    hits = Response({
        'hits': {
            'hits': [
                {
                    '_type': 'hep',
                    '_source': {
                        'control_number': 1427573,
                        'titles': [
                            {'title': u'Storage Ring Based EDM Search — Achievements and Goals'},
                        ],
                    },
                },
            ],
            'total': 1,
        },
    }).hits

    expected = ([
        [
            u"<a href='/literature/1427573'>Storage Ring Based EDM Search — Achievements and Goals</a>",
            u'\n\n',
            '',
            0,
        ],
    ], 1)
    result = render_contributions(hits)

    assert expected == result
