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
from mock import patch
from inspire_utils.record import get_value

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.matching import (
    exact_match,
    fuzzy_match,
    has_fully_harvested_category,
    is_fuzzy_match_approved,
    pending_in_holding_pen,
    physics_data_an_is_primary_category,
    set_core_in_extra_data,
    set_exact_match_as_approved_in_extradata,
    set_fuzzy_match_approved_in_extradata,
)

from mocks import MockEng, MockObj


@pytest.fixture
def enable_fuzzy_matcher(app):
    with patch.dict(app.config, {'FEATURE_FLAG_ENABLE_FUZZY_MATCHER': True}):
        yield


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_exact_match_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{'_source': {'control_number': 4328}}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert exact_match(obj, eng)
    assert 'matches' in obj.extra_data

    expected = [4328]
    result = get_value(obj.extra_data, 'matches.exact')

    assert expected == result


def test_set_exact_match_as_approved_in_extradata():
    data = {}
    extra_data = {
        'matches': {'exact': [1, 2]}
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_exact_match_as_approved_in_extradata(obj, eng)

    assert get_value(obj.extra_data, 'matches.approved') is 1


def test_set_exact_match_as_approved_in_extradata_with_empty_list_raises_exception():
    data = {}
    extra_data = {
        'matches': {'exact': []}
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with pytest.raises(IndexError):
        set_exact_match_as_approved_in_extradata(obj, eng)


def test_set_exact_match_as_approved_in_extradata_no_exact_key_raises_exception():
    data = {}
    extra_data = {
        'matches': {'wrongkey': [1]}
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with pytest.raises(KeyError):
        set_exact_match_as_approved_in_extradata(obj, eng)


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_exact_match_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not exact_match(obj, eng)
    assert 'matches' in obj.extra_data

    expected = []
    result = get_value(obj.extra_data, 'matches.exact')

    assert expected == result


def test_has_fully_harvested_category_is_true_with_core_categories(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
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
        assert has_fully_harvested_category(record)


def test_has_fully_harvested_category_is_true_with_non_core_categories(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        record = {
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
        assert validate(record['arxiv_eprints'], subschema) is None
        assert has_fully_harvested_category(record)


def test_has_fully_harvested_category_is_false_with_others_categories(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        record = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'math',
                    ],
                    'value': '1609.03939',
                },
            ],
        }
        assert validate(record['arxiv_eprints'], subschema) is None
        assert not has_fully_harvested_category(record)


def physics_data_an_is_primary_category_is_false(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']
    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math',
                ],
                'value': '1609.03939',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None
    assert not physics_data_an_is_primary_category(record)


def physics_data_an_is_primary_category_is_true(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']
    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'physics.data-an',
                ],
                'value': '1609.03939',
            },
        ],
    }
    assert validate(record['arxiv_eprints'], subschema) is None
    assert physics_data_an_is_primary_category(record)


def test_core_is_written_in_extradata_if_article_is_core(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'hep-ph',
                    ],
                    'value': '1705.01122',
                },
            ],
        }
        assert validate(obj.data['arxiv_eprints'], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert obj.extra_data['core']


def test_core_is_not_written_in_extradata_if_article_is_non_core(app):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    categories_config = {
        'ARXIV_CATEGORIES': {
            'core': ['hep-ph'],
            'non-core': ['astro-ph.CO', 'gr-qc']
        }
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'astro-ph.CO',
                    ],
                    'value': '1705.01122',
                },
            ],
        }
        assert validate(obj.data['arxiv_eprints'], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert 'core' not in obj.extra_data


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{'_id': 1}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data, id=2)
    eng = MockEng()

    assert pending_in_holding_pen(obj, eng)


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_pending_in_holding_pen_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not pending_in_holding_pen(obj, eng)


@patch('inspirehep.modules.workflows.tasks.matching.get_record_ref')
@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_fuzzy_match_returns_true_if_something_matched(mock_match, mock_get_record_ref, enable_fuzzy_matcher):
    mock_match.return_value = iter([{'_source': {'control_number': 4328}}])
    mock_get_record_ref.side_effect = lambda recid, pid_type: {'$ref': '/ref/{recid}'.format(recid=recid)}
    expected = [{'$ref': '/ref/4328'}]

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert fuzzy_match(obj, eng)
    assert 'matches' in obj.extra_data

    result = get_value(obj.extra_data, 'matches.fuzzy')

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_fuzzy_match_returns_false_if_nothing_matched(mock_match, enable_fuzzy_matcher):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not fuzzy_match(obj, eng)
    assert 'matches' in obj.extra_data

    expected = []
    result = get_value(obj.extra_data, 'matches.fuzzy')

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_is_fuzzy_match_approved_returns_true_if_there_is_a_match_approved(mock_match):
    data = {}
    extra_data = {'fuzzy_match_approved_id': 4328}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_fuzzy_match_approved(obj, eng)


@patch('inspirehep.modules.workflows.tasks.matching.match')
def test_is_fuzzy_match_approved_returns_False_if_there_is_not_a_match_approved(mock_match):
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_fuzzy_match_approved(obj, eng)


def test_set_fuzzy_match_approved_in_extradata():
    data = {}
    extra_data = {
        'fuzzy_match_approved_id': 1
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_fuzzy_match_approved_in_extradata(obj, eng)

    expected = 1
    result = get_value(obj.extra_data, 'matches.approved')

    assert expected == result


def test_set_fuzzy_match_approved_in_extradata_no_fuzzy_key():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_fuzzy_match_approved_in_extradata(obj, eng)

    expected = None
    result = get_value(obj.extra_data, 'matches.approved')

    assert expected == result


def test_fuzzy_matcher_not_run_on_feat_flag_disabled():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    with patch('inspirehep.modules.workflows.tasks.matching.match') as match:
        fuzzy_match(obj, eng)

        match.assert_not_called()


def test_fuzzy_matcher_run_on_feat_flag_enabled(enable_fuzzy_matcher):
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    with patch('inspirehep.modules.workflows.tasks.matching.match') as match:
        fuzzy_match(obj, eng)

        match.assert_called()
