# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2020 CERN.
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
import pytest
import mock
from flask import current_app
from inspire_schemas.api import validate
from inspirehep.modules.workflows.utils import (
    get_record_from_hep,
    post_record_to_hep,
    put_record_to_hep
)

from inspirehep.modules.workflows.errors import (
    InspirehepMissingDataError,
)


@pytest.mark.vcr()
def test_get_record_from_hep(app):
    config = {
        'INSPIREHEP_URL': 'https://inspirebeta.net/api',
    }
    expected_control_number = 20
    with mock.patch.dict(current_app.config, config):
        record = get_record_from_hep('lit', '20')
    validate(record['metadata'])
    assert expected_control_number == record['metadata']['control_number']
    assert 'uuid' in record.keys()


@mock.patch(
    'inspirehep.modules.workflows.utils.requests.get',
    side_effect=requests.exceptions.ConnectionError()
)
def test_get_record_from_hep_with_connection_error(mock_requests_get, app):
    with pytest.raises(requests.exceptions.ConnectionError):
        get_record_from_hep('lit', '20')

    assert 5 == mock_requests_get.call_count


@pytest.mark.vcr()
def test_post_record_to_hep(app):
    config = {
        'INSPIREHEP_URL': 'https://inspirebeta.net/api',
    }
    with mock.patch.dict(current_app.config, config):
        data = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature'
            ],
            'document_type': [
                'article'
            ],
            'titles': [
                {
                    'title': 'Autobiography from Jessica Jones'
                },
            ]
        }
        record = post_record_to_hep('lit', data=data)
    assert 'control_number' in record['metadata'].keys()


@mock.patch(
    'inspirehep.modules.workflows.utils.requests.post',
    side_effect=requests.exceptions.ConnectionError()
)
def test_post_record_to_hep_with_connection_error(mock_requests_get, app):
    with pytest.raises(requests.exceptions.ConnectionError):
        data = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature'
            ],
            'document_type': [
                'article'
            ],
            'titles': [
                {
                    'title': 'Autobiography from Jessica Jones'
                },
            ]
        }
        post_record_to_hep('lit', data=data)

    assert 5 == mock_requests_get.call_count


def test_post_record_to_hep_with_missing_data_error(app):
    with pytest.raises(InspirehepMissingDataError):
        post_record_to_hep('lit', data={})


@pytest.mark.vcr()
def test_put_record_to_hep(app):
    config = {
        'INSPIREHEP_URL': 'https://inspirebeta.net/api',
    }
    with mock.patch.dict(current_app.config, config):
        data = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature'
            ],
            'document_type': [
                'article'
            ],
            'titles': [
                {
                    'title': 'Autobiography from Jessica Jones'
                },
            ]
        }
        record = post_record_to_hep('lit', data=data)
        record_control_number = record['metadata']['control_number']

        data = get_record_from_hep('lit', record_control_number)

        expected_title = 'Autobiography from Frank Castle'
        data['metadata']['titles'][0]['title'] = expected_title
        record_updated = put_record_to_hep('lit', record_control_number, data=data['metadata'])
        assert expected_title == record_updated['metadata']['titles'][0]['title']


@mock.patch(
    'inspirehep.modules.workflows.utils.requests.put',
    side_effect=requests.exceptions.ConnectionError()
)
def test_put_record_to_hep_with_connection_error(mock_requests_get, app):
    with pytest.raises(requests.exceptions.ConnectionError):
        data = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature'
            ],
            'document_type': [
                'article'
            ],
            'titles': [
                {
                    'title': 'Autobiography from Jessica Jones'
                },
            ]
        }
        put_record_to_hep('lit', '20', data=data)
    assert 5 == mock_requests_get.call_count


def test_put_record_to_hep_with_missing_data_error(app):
    with pytest.raises(InspirehepMissingDataError):
        put_record_to_hep('lit', '20', data={})
