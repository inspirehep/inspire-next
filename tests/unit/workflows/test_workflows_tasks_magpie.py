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

import requests
from flask import current_app
from mock import patch

from inspirehep.modules.workflows.tasks.magpie import (
    get_magpie_url,
    prepare_magpie_payload,
    filter_magpie_response,
    guess_keywords,
    guess_categories,
    guess_experiments,
)

from mocks import MockEng, MockObj


def test_get_magpie_url_returns_value_from_configuration():
    config = {'MAGPIE_API_URL': 'https://magpie.inspirehep.net'}

    with patch.dict(current_app.config, config):
        expected = 'https://magpie.inspirehep.net/predict'
        result = get_magpie_url()

        assert expected == result


def test_get_magpie_url_returns_none_when_not_in_configuration():
    config = {}

    with patch.dict(current_app.config, config, clear=True):
        assert get_magpie_url() is None


def test_prepare_magpie_payload():
    record = {
        'titles': [
            {
                'title': 'foo',
            },
            {
                'title': 'bar',
            },
        ],
        'abstracts': [
            {
                'value': 'baz',
            },
        ]
    }

    expected = {
        'text': 'foo. bar. baz',
        'corpus': 'qux',
    }
    result = prepare_magpie_payload(record, 'qux')

    assert expected == result


def test_filter_magpie_response():
    labels = [
        ('foo', 0.75),
        ('bar', 0.50),
        ('baz', 0.25),
    ]

    expected = [
        ('foo', 0.75),
        ('bar', 0.50),
    ]
    result = filter_magpie_response(labels, 0.50)

    assert expected == result


def test_filter_magpie_response_falls_back_to_first_label():
    labels = [
        ('foo', 0.75),
        ('bar', 0.50),
        ('baz', 0.25),
    ]

    expected = [
        ('foo', 0.75),
    ]
    result = filter_magpie_response(labels, 1.00)

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_keywords_accepts_over_point_09(j_a_r, g_m_u):
    j_a_r.return_value = {
        'labels': [
            ('foo', 0.09),
        ],
    }
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_keywords(obj, eng) is None
    assert obj.extra_data['keywords_prediction'] == {
        'keywords': [
            {
                'label': 'foo',
                'score': 0.09,
                'accept': True,
            },
        ]
    }


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_keywords_considers_only_first_ten(j_a_r, g_m_u):
    j_a_r.return_value = {
        'labels': [
            ('k01', 1.00),
            ('k02', 1.00),
            ('k03', 1.00),
            ('k04', 1.00),
            ('k05', 1.00),
            ('k06', 1.00),
            ('k07', 1.00),
            ('k08', 1.00),
            ('k09', 1.00),
            ('k10', 1.00),
            ('k11', 1.00),  # Will be ignored.
        ],
    }
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_keywords(obj, eng) is None
    assert obj.extra_data['keywords_prediction'] == {
        'keywords': [
            {'label': 'k01', 'score': 1.00, 'accept': True},
            {'label': 'k02', 'score': 1.00, 'accept': True},
            {'label': 'k03', 'score': 1.00, 'accept': True},
            {'label': 'k04', 'score': 1.00, 'accept': True},
            {'label': 'k05', 'score': 1.00, 'accept': True},
            {'label': 'k06', 'score': 1.00, 'accept': True},
            {'label': 'k07', 'score': 1.00, 'accept': True},
            {'label': 'k08', 'score': 1.00, 'accept': True},
            {'label': 'k09', 'score': 1.00, 'accept': True},
            {'label': 'k10', 'score': 1.00, 'accept': True},
        ],
    }


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_keywords_does_not_fail_when_request_fails(j_a_r, g_m_u):
    j_a_r.side_effect = requests.exceptions.RequestException()
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_keywords(obj, eng) is None
    assert obj.extra_data == {}


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
def test_guess_keywords_fails_without_a_magpie_url(g_m_u):
    g_m_u.return_value = None

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_keywords(obj, eng) is None
    assert obj.extra_data == {}


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_categories_filters_under_point_22(j_a_r, g_m_u):
    j_a_r.return_value = {
        'labels': [
            ('foo', 0.21),
            ('bar', 0.22),
        ],
    }
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_categories(obj, eng) is None
    assert obj.extra_data['categories_prediction'] == {
        'categories': [
            {
                'label': 'bar',
                'score': 0.22,
                'accept': False,
            },
        ],
    }


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_categories_accepts_over_point_25(j_a_r, g_m_u):
    j_a_r.return_value = {
        'labels': [
            ('foo', 0.25),
        ],
    }
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_categories(obj, eng) is None
    assert obj.extra_data['categories_prediction'] == {
        'categories': [
            {
                'label': 'foo',
                'score': 0.25,
                'accept': True,
            },
        ],
    }


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
def test_guess_categories_fails_without_a_magpie_url(g_m_u):
    g_m_u.return_value = None

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_categories(obj, eng) is None
    assert obj.extra_data == {}


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
@patch('inspirehep.modules.workflows.tasks.magpie.json_api_request')
def test_guess_experiments_filters_under_point_50(j_a_r, g_m_u):
    j_a_r.return_value = {
        'labels': [
            ('foo', 0.49),
            ('bar', 0.50),
        ],
    }
    g_m_u.return_value = 'https://magpie.inspirehep.net/predict'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_experiments(obj, eng) is None
    assert obj.extra_data['experiments_prediction'] == {
        'experiments': [
            {
                'label': 'bar',
                'score': 0.50,
            }
        ],
    }


@patch('inspirehep.modules.workflows.tasks.magpie.get_magpie_url')
def test_guess_experiments_fails_without_a_magpie_url(g_m_u):
    g_m_u.return_value = None

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_experiments(obj, eng) is None
    assert obj.extra_data == {}
