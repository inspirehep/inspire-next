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

from inspirehep.utils.experiments import render_people, render_contributions


def test_render_people():
    hits = Response({
        'hits': {
            'hits': [
                {
                    '_type': 'authors',
                    '_source': {
                        'control_number': 1,
                        'name': {
                            'preferred_name': 'preferred_name',
                        },
                    },
                },
            ],
            'total': 1,
        },
    }).hits

    expected = ([
        [
            "<a href='/authors/1'>preferred_name</a>",
        ],
    ], 1)
    result = render_people(hits)

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
