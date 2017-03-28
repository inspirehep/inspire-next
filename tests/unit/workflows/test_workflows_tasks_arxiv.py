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

import pytest

from inspire_schemas.utils import load_schema
from inspirehep.dojson.utils import validate
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_derive_inspire_categories
)


class StubObj(object):
    def __init__(self, data, extra_data):
        self.data = data
        self.extra_data = extra_data


class DummyEng(object):
    pass


def test_arxiv_derive_inspire_categories():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    obj = StubObj(
        {
            'arxiv_eprints': [
                {
                    'categories': [
                        'alg-geom',
                    ],
                }
            ],
            'inspire_categories': [
                {
                    'source': 'arxiv',
                    'term': 'General Physics',
                }, {
                    'source': 'user',
                    'term': 'Math and Math Physics',
                }
            ]
        },
        {}
    )
    eng = DummyEng()

    expected_value = [
        {
            'source': 'arxiv',
            'term': 'General Physics',
        }, {
            'source': 'user',
            'term': 'Math and Math Physics',
        }, {
            'source': 'arxiv',
            'term': 'Math and Math Physics',
        }
    ]

    assert arxiv_derive_inspire_categories(obj, eng) is None
    assert obj.data['inspire_categories'] == expected_value
    assert validate(obj.data['inspire_categories'], subschema) is None


def test_arxiv_derive_inspire_categories_other():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    obj = StubObj(
        {
            'arxiv_eprints': [
                {
                    'categories': [
                        'q-bio',
                    ],
                }
            ],
            'inspire_categories': [
                {
                    'source': 'arxiv',
                    'term': 'General Physics',
                }, {
                    'source': 'user',
                    'term': 'Math and Math Physics',
                }
            ]
        },
        {}
    )
    eng = DummyEng()

    expected_value = [
        {
            'source': 'arxiv',
            'term': 'General Physics',
        }, {
            'source': 'user',
            'term': 'Math and Math Physics',
        }, {
            'source': 'arxiv',
            'term': 'Other',
        }
    ]

    assert arxiv_derive_inspire_categories(obj, eng) is None
    assert obj.data['inspire_categories'] == expected_value
    assert validate(obj.data['inspire_categories'], subschema) is None


def test_arxiv_derive_inspire_categories_already_present():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    obj = StubObj(
        {
            'arxiv_eprints': [
                {
                    'categories': [
                        'physics.gen-ph',
                    ],
                }
            ],
            'inspire_categories': [
                {
                    'source': 'arxiv',
                    'term': 'General Physics',
                }, {
                    'source': 'user',
                    'term': 'Math and Math Physics',
                }
            ]
        },
        {}
    )
    eng = DummyEng()

    expected_value = [
        {
            'source': 'arxiv',
            'term': 'General Physics',
        }, {
            'source': 'user',
            'term': 'Math and Math Physics',
        }
    ]

    assert arxiv_derive_inspire_categories(obj, eng) is None
    assert obj.data['inspire_categories'] == expected_value
    assert validate(obj.data['inspire_categories'], subschema) is None


def test_arxiv_derive_inspire_categories_multiple_eprints():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    obj = StubObj(
        {
            'arxiv_eprints': [
                {
                    'categories': [
                        'alg-geom',
                    ],
                }, {
                    'categories': [
                        'physics.data-an',
                    ],
                }
            ],
            'inspire_categories': [
                {
                    'source': 'arxiv',
                    'term': 'General Physics',
                }, {
                    'source': 'user',
                    'term': 'Math and Math Physics',
                }
            ]
        },
        {}
    )
    eng = DummyEng()

    expected_value = [
        {
            'source': 'arxiv',
            'term': 'General Physics',
        }, {
            'source': 'user',
            'term': 'Math and Math Physics',
        }, {
            'source': 'arxiv',
            'term': 'Math and Math Physics',
        }, {
            'source': 'arxiv',
            'term': 'Data Analysis and Statistics',
        }
    ]

    assert arxiv_derive_inspire_categories(obj, eng) is None
    assert obj.data['inspire_categories'] == expected_value
    assert validate(obj.data['inspire_categories'], subschema) is None
