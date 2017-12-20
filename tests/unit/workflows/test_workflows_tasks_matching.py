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
    article_exists,
    belongs_to_relevant_category,
    get_coreness,
    _pending_in_holding_pen,
)

from mocks import MockEng, MockObj

from inspirehep.modules.workflows.tasks.matching import Coreness


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


def test_belongs_to_relevant_category_returns_true_and_is_core(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        obj = MockObj
        eng = MockEng
        obj.data = {
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
        assert validate(obj.data['arxiv_eprints'], subschema) is None
        assert belongs_to_relevant_category(obj, eng) is True
        assert get_coreness(obj.data) is Coreness.core


def test_belongs_to_relevant_category_returns_true_and_is_non_core(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core':     ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        obj = MockObj
        eng = MockEng
        obj.data = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'astro-ph.CO',
                        'gr-qc',
                    ],
                    'value': '1609.03939',
                },
            ],
        }
        assert validate(obj.data['arxiv_eprints'], subschema) is None
        assert belongs_to_relevant_category(obj, eng) is True
        assert get_coreness(obj.data) is Coreness.non_core


def test_belongs_to_relevant_category_returns_false(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core':     ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        obj = MockObj
        eng = MockEng
        obj.data = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'math.CO',
                    ],
                    'value': '1705.01122',
                },
            ],
        }
        assert validate(obj.data['arxiv_eprints'], subschema) is None
        assert belongs_to_relevant_category(obj, eng) is False
        assert get_coreness(obj.data) is Coreness.non_relevant


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{'_id': 1}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data, id=2)
    eng = MockEng()

    assert _pending_in_holding_pen(obj, eng)


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not _pending_in_holding_pen(obj, eng)
