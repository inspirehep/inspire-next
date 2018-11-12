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

from inspirehep.modules.workflows.tasks.beard import (
    get_beard_url,
    prepare_payload,
    guess_coreness,
)

from mocks import MockEng, MockObj


def test_get_beard_url_from_configuration():
    config = {'BEARD_API_URL': 'https://beard.inspirehep.net'}

    with patch.dict(current_app.config, config):
        expected = 'https://beard.inspirehep.net/predictor/coreness'
        result = get_beard_url()

        assert expected == result


def test_get_beard_url_returns_none_when_not_in_configuration():
    config = {'BEARD_API_URL': ''}

    with patch.dict(current_app.config, config):
        assert get_beard_url() is None


def test_prepare_payload():
    record = {
        'titles': [
            {
                'title': 'Effects of top compositeness',
            },
        ],
        'arxiv_eprints': [
            {
                'categories': [
                    'cond-mat.mes-hall',
                    'cond-mat.mtrl-sci',
                ],
            },
        ],
        'abstracts': [
            {
                'value': 'We investigate the effects of (...)',
            },
        ],
    }

    expected = {
        'title': 'Effects of top compositeness',
        'abstract': 'We investigate the effects of (...)',
        'categories': [
            'cond-mat.mes-hall',
        ],
    }
    result = prepare_payload(record)

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.beard.get_beard_url')
def test_guess_coreness_fails_without_a_beard_url(g_b_u):
    g_b_u.return_value = ''

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert 'relevance_prediction' not in obj.extra_data


@patch('inspirehep.modules.workflows.tasks.beard.get_beard_url')
@patch('inspirehep.modules.workflows.tasks.beard.json_api_request')
def test_guess_coreness_does_not_fail_when_request_fails(j_a_r, g_b_u):
    j_a_r.side_effect = requests.exceptions.RequestException()
    g_b_u.return_value = 'https://beard.inspirehep.net/predictor/coreness'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert 'relevance_prediction' not in obj.extra_data


@patch('inspirehep.modules.workflows.tasks.beard.get_beard_url')
@patch('inspirehep.modules.workflows.tasks.beard.json_api_request')
def test_guess_coreness_when_core(j_a_r, g_b_u):
    j_a_r.return_value = {
        'decision': 'CORE',
        'scores': [
            1.375354035683761,
            -1.2487082195061714,
            -3.064134460779941,
        ],
    }
    g_b_u.return_value = 'https://beard.inspirehep.net/predictor/coreness'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 1.375354035683761,
        'decision': 'CORE',
        'scores': {
            'CORE': 1.375354035683761,
            'Non-CORE': -1.2487082195061714,
            'Rejected': -3.064134460779941,
        },
        'relevance_score': 11.375354035683761,
    }


@patch('inspirehep.modules.workflows.tasks.beard.get_beard_url')
@patch('inspirehep.modules.workflows.tasks.beard.json_api_request')
def test_guess_coreness_when_non_core(j_a_r, g_b_u):
    j_a_r.return_value = {
        'decision': 'Non-CORE',
        'scores': [
            -1.2487082195061714,
            1.375354035683761,
            -3.064134460779941,
        ],
    }
    g_b_u.return_value = 'https://beard.inspirehep.net/predictor/coreness'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 1.375354035683761,
        'decision': 'Non-CORE',
        'scores': {
            'CORE': -1.2487082195061714,
            'Non-CORE': 1.375354035683761,
            'Rejected': -3.064134460779941,
        },
        'relevance_score': 1.375354035683761,
    }


@patch('inspirehep.modules.workflows.tasks.beard.get_beard_url')
@patch('inspirehep.modules.workflows.tasks.beard.json_api_request')
def test_guess_coreness_when_rejected(j_a_r, g_b_u):
    j_a_r.return_value = {
        'decision': 'Rejected',
        'scores': [
            -3.064134460779941,
            -1.2487082195061714,
            1.375354035683761,
        ],
    }
    g_b_u.return_value = 'https://beard.inspirehep.net/predictor/coreness'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 1.375354035683761,
        'decision': 'Rejected',
        'scores': {
            'CORE': -3.064134460779941,
            'Non-CORE': -1.2487082195061714,
            'Rejected': 1.375354035683761,
        },
        'relevance_score': -11.375354035683761,
    }
