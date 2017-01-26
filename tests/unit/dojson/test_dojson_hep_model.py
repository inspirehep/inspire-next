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

from inspirehep.dojson.hep.model import add_inspire_category


def test_add_inspire_category_from_arxiv_eprints_categories():
    record = {
        'arxiv_eprints': {
            'categories': [
                'astro-ph',
            ],
        },
    }

    expected = [
        {
            'source': 'arxiv',
            'term': 'Astrophysics',
        },
    ]
    result = add_inspire_category(record, None)

    assert expected == result['inspire_categories']


def test_add_inspire_category_does_nothing_when_no_arxiv_eprints_categories():
    assert 'inspire_categories' not in add_inspire_category({}, None)


def test_add_inspire_category_does_nothing_when_inspire_categories_is_there():
    record = {
        'arxiv_eprints': {
            'categories': [
                'cs.DS',
            ],
        },
        'inspire_categories': [
            {
                'source': 'arxiv',
                'term': 'Astrophysics',
            },
        ],
    }

    expected = [
        {
            'source': 'arxiv',
            'term': 'Astrophysics',
        },
    ]
    result = add_inspire_category(record, None)

    assert expected == result['inspire_categories']
