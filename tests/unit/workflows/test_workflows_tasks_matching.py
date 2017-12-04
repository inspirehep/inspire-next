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

from mock import patch

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.matching import (
    already_harvested,
    article_exists,
    is_being_harvested_on_legacy,
    pending_in_holding_pen,
)

from mocks import MockEng, MockObj


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_article_exists_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{'_source': {'control_number': 4328}}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert article_exists(obj, eng)
    assert 'record_matches' in obj.extra_data

    expected = [4328]
    result = obj.extra_data['record_matches']

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_article_exists_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not article_exists(obj, eng)
    assert 'record_matches' in obj.extra_data

    expected = []
    result = obj.extra_data['record_matches']

    assert expected == result


def test_is_being_harvested_on_legacy_returns_true_when_there_is_one_core_category(app):
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

    extra_config = {
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [
            'hep-ph'
        ]
    }

    with patch.dict(app.config, extra_config):
        assert is_being_harvested_on_legacy(record)


def test_is_being_harvested_on_legacy_uses_the_correct_capitalization(app):
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

    extra_config = {
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [
            'astro-ph.CO'
        ]
    }

    with patch.dict(app.config, extra_config):
        assert is_being_harvested_on_legacy(record)


def test_is_being_harvested_on_legacy_returns_false_otherwise(app):
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

    extra_config = {
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [
            'astro-ph.CO'
        ]
    }

    with patch.dict(app.config, extra_config):
        assert not is_being_harvested_on_legacy(record)


def test_already_harvested_returns_true_when_there_is_one_core_category(app):
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

    extra_config = {
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [
            'astro-ph.CO'
        ]
    }

    with patch.dict(app.config, extra_config):
        assert already_harvested(obj, eng)

    expected = (
        'Record with arXiv id 1609.03939 is'
        ' already being harvested on Legacy.'
    )
    result = obj.log._info.getvalue()

    assert expected == result


def test_already_harvested_returns_false_otherwise(app):
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

    extra_config = {
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY': [
            'astro-ph.CO'
        ]
    }

    with patch.dict(app.config, extra_config):
        assert not already_harvested(obj, eng)

    expected = ''
    result = obj.log._info.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{'_id': 1}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data, id=2)
    eng = MockEng()

    assert pending_in_holding_pen(obj, eng)
    assert 'holdingpen_matches' in obj.extra_data

    expected = [1]
    result = obj.extra_data['holdingpen_matches']

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not pending_in_holding_pen(obj, eng)
    assert 'holdingpen_matches' in obj.extra_data
    expected = []
    result = obj.extra_data['holdingpen_matches']

    assert expected == result
