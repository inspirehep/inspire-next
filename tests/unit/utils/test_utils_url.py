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

import os

import pytest
import requests_mock
from flask import current_app
from mock import patch
from six import binary_type, text_type

from inspirehep.utils.url import (
    get_legacy_url_for_recid,
    is_pdf_link,
    make_user_agent_string,
    retrieve_uri,
)


def test_is_pdf_link_handles_empty_requests():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri('GET', 'http://example.org/empty-pdf', text='')

        assert not is_pdf_link('http://example.org/empty-pdf')


@pytest.mark.vcr()
def test_is_pdf_link_handles_pdfs_starting_with_blank_lines():
    assert is_pdf_link('https://arxiv.org/pdf/1803.01183.pdf')


@patch('inspirehep.utils.url.__version__', '0.1.0')
def test_make_user_agent_string():
    """Test that user agent is created."""
    config = {'SERVER_NAME': 'http://inspirehep.net'}

    with patch.dict(current_app.config, config):
        user_agent = make_user_agent_string()
        assert user_agent == "InspireHEP-0.1.0 (+http://inspirehep.net;)"

        user_agent_with_component = make_user_agent_string("submission")
        assert user_agent_with_component == "InspireHEP-0.1.0 (+http://inspirehep.net;) [submission]"


def test_retrieve_uri(tmpdir):
    test_file = tmpdir.join('file.txt')
    test_file.write('some content')

    uri = 'file://' + binary_type(test_file)

    with retrieve_uri(uri) as local_path, open(local_path) as local_file:
        path_copy = local_path
        assert local_file.read() == 'some content'

    assert not os.path.exists(path_copy)


@pytest.mark.parametrize(
    'recid,expected',
    [
        (12345, 'http://inspirehep.net/record/12345'),
        (text_type(2434), 'http://inspirehep.net/record/2434'),
        (binary_type(3563), 'http://inspirehep.net/record/3563'),
    ],
    ids=[
        'integer recid',
        'unicode recid',
        'binary string recid',
    ]
)
def test_get_legacy_url_for_record(recid, expected):
    config = {
        'LEGACY_RECORD_URL_PATTERN': 'http://inspirehep.net/record/{recid}',
    }

    with patch.dict(current_app.config, config):
        assert get_legacy_url_for_recid(recid) == expected
