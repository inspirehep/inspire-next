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

from inspire_dojson.utils import validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.workflows.tasks.matching import (
    already_harvested,
    is_being_harvested_on_legacy,
)

from mocks import MockEng, MockObj


def test_is_being_harvested_on_legacy_returns_true_when_there_is_one_core_category():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ph',
                    'astro-ph.CO',
                    'gr-qc',
                ],
                'value': '1609.03939',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None

    assert is_being_harvested_on_legacy(record)


def test_is_being_harvested_on_legacy_uses_the_correct_capitalization():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.CO',
                ],
                'value': '1705.00502',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None

    assert is_being_harvested_on_legacy(record)


def test_is_being_harvested_on_legacy_returns_false_otherwise():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CO',
                ],
                'value': '1705.01122',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None

    assert not is_being_harvested_on_legacy(record)


def test_already_harvested_returns_true_when_there_is_one_core_category():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ph',
                    'astro-ph.CO',
                    'gr-qc',
                ],
                'value': '1609.03939',
            },
        ],
    }
    extra_data = {}
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert already_harvested(obj, eng)

    expected = (
        'Record with arXiv id 1609.03939 is'
        ' already being harvested on Legacy.'
    )
    result = obj.log._info.getvalue()

    assert expected == result


def test_already_harvested_returns_false_otherwise():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CO',
                ],
                'value': '1705.01122',
            },
        ],
    }
    extra_data = {}
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not already_harvested(obj, eng)

    expected = ''
    result = obj.log._info.getvalue()

    assert expected == result
