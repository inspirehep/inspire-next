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

from inspire_schemas.api import load_schema, validate
from inspirehep.utils.record import (
    get_abstract,
    get_arxiv_categories,
    get_arxiv_id,
    get_source,
    get_subtitle,
    get_title,
)


def test_get_abstract():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    record = {
        'abstracts': [
            {
                'source': 'arXiv',
                'value': 'Probably not.',
            },
        ],
    }
    assert validate(record['abstracts'], subschema) is None

    expected = 'Probably not.'
    result = get_abstract(record)

    assert expected == result


def test_get_arxiv_categories():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                    'hep-ph',
                ],
                'value': '1612.08928',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None

    expected = ['hep-th', 'hep-ph']
    result = get_arxiv_categories(record)

    assert expected == result


def test_get_arxiv_id():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                    'hep-ph',
                ],
                'value': '1612.08928',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None

    expected = '1612.08928'
    result = get_arxiv_id(record)

    assert expected == result


def test_get_source():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    record = {
        'acquisition_source': {
            'method': 'oai',
            'source': 'arxiv',
        },
    }
    assert validate(record['acquisition_source'], subschema) is None

    expected = 'arxiv'
    result = get_source(record)

    assert expected == result


def test_get_subtitle():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    record = {
        'titles': [
            {
                'subtitle': 'A mathematical exposition',
                'title': 'The General Theory of Relativity',
            },
        ],
    }
    assert validate(record['titles'], subschema) is None

    expected = 'A mathematical exposition'
    result = get_subtitle(record)

    assert expected == result


def test_get_title():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    record = {
        'titles': [
            {
                'subtitle': 'A mathematical exposition',
                'title': 'The General Theory of Relativity',
            },
        ],
    }
    assert validate(record['titles'], subschema) is None

    expected = 'The General Theory of Relativity'
    result = get_title(record)

    assert expected == result
