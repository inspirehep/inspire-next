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

import pkg_resources
import pytest
import requests
import requests_mock

from inspirehep.modules.workflows.utils import (
    convert,
    download_file_to_workflow,
    json_api_request,
)

from mocks import MockFiles, MockFileObject, MockObj


def test_download_file_to_workflow_retries_on_protocol_error():
    with requests_mock.Mocker() as requests_mocker:
        filename = pkg_resources.resource_filename(
            __name__, os.path.join('fixtures', '1605.03844.pdf'))

        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844', [
                {'exc': requests.packages.urllib3.exceptions.ProtocolError},
                {'body': filename, 'status_code': 200},
            ])

        data = {}
        extra_data = {}
        files = MockFiles({})

        obj = MockObj(data, extra_data, files=files)

        expected = MockFileObject(key='1605.03844.pdf')
        result = download_file_to_workflow(
            obj, '1605.03844.pdf', 'http://export.arxiv.org/pdf/1605.03844')

        assert expected == result


def test_json_api_request_retries_on_connection_error():
    with requests_mock.Mocker() as requests_mocker:
        body = {'foo': 'bar'}

        requests_mocker.register_uri(
            'POST', 'http://example.org/api', [
                {'exc': requests.packages.urllib3.exceptions.ConnectionError},
                {'json': body},
            ])

        expected = {'foo': 'bar'}
        result = json_api_request('http://example.org/api', {})

        assert expected == result


@pytest.fixture
def oai_xml():
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv.xml'
        )
    )


@pytest.fixture
def oai_xml_result():
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'arxiv_marcxml.xml'
        )
    )


def test_xslt(oai_xml, oai_xml_result):
    xml = convert(xml=oai_xml, xslt_filename='oaiarXiv2marcxml.xsl')
    assert xml
    assert xml == oai_xml_result
