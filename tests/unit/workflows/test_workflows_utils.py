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
import time

from contextlib import contextmanager
from mock import patch

from timeout_decorator import timeout

from inspirehep.modules.workflows.utils import (
    convert,
    copy_file_to_workflow,
    download_file_to_workflow,
    get_document_in_workflow,
    get_source_for_root,
    ignore_timeout_error,
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


@patch('inspirehep.modules.workflows.utils.fsopen')
def test_copy_file_to_workflow(mock_fsopen):
    mock_fsopen.return_value = 'jessica jones'

    data = {}
    extra_data = {}
    files = MockFiles({})

    obj = MockObj(data, extra_data, files=files)

    expected = MockFileObject(key='jessicajones.defenders;1')
    result = copy_file_to_workflow(
        obj, 'jessicajones.defenders;1', 'file://jessicajones.defenders%3B1')

    assert expected == result
    mock_fsopen.assert_called_once_with(
        'file://jessicajones.defenders;1', mode='rb')


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


@contextmanager
def mock_retrieve_uri(arg):
    yield arg


@patch('inspirehep.modules.workflows.utils.retrieve_uri', mock_retrieve_uri)
def test_get_document_in_workflow():
    data = {
        'documents': [
            {
                'key': 'fulltext.xml',
                'fulltext': True,
            },
        ],
    }
    files = MockFiles({})
    files['fulltext.xml'] = None
    obj = MockObj(data, {}, files=files)

    with get_document_in_workflow(obj) as local_file:
        assert local_file == files['fulltext.xml'].file.uri


@patch('inspirehep.modules.workflows.utils.retrieve_uri', mock_retrieve_uri)
def test_get_document_in_workflow_returns_None_when_no_documents():
    files = MockFiles({})
    obj = MockObj({}, {}, files=files)

    with get_document_in_workflow(obj) as local_file:
        assert local_file is None


@patch('inspirehep.modules.workflows.utils.retrieve_uri', mock_retrieve_uri)
def test_get_document_in_workflow_prefers_fulltext():
    data = {
        'documents': [
            {
                'key': 'table_of_contents.pdf',
            },
            {
                'key': 'fulltext.xml',
                'fulltext': True,
            },
        ],
    }
    files = MockFiles({})
    files['fulltext.xml'] = None
    files['table_of_contents.pdf'] = None
    obj = MockObj(data, {}, files=files)

    with get_document_in_workflow(obj) as local_file:
        assert local_file == files['fulltext.xml'].file.uri


@patch('inspirehep.modules.workflows.utils.retrieve_uri', mock_retrieve_uri)
def test_get_document_in_workflow_takes_first_among_equals():
    data = {
        'documents': [
            {
                'key': 'table_of_contents.pdf',
            },
            {
                'key': 'document.pdf',
            },
        ],
    }
    files = MockFiles({})
    files['document.pdf'] = None
    files['table_of_contents.pdf'] = None
    obj = MockObj(data, {}, files=files)

    with get_document_in_workflow(obj) as local_file:
        assert local_file == files['table_of_contents.pdf'].file.uri

    assert 'More than one document in workflow, first one used' in obj.log._error.getvalue()


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


@patch('inspirehep.modules.workflows.utils.LOGGER')
def test_ignore_timeout_decorator(mock_logger):

    @ignore_timeout_error()
    @timeout(1)
    def f():
        time.sleep(2)

    f()

    assert mock_logger.error.called


@patch('inspirehep.modules.workflows.utils.LOGGER')
def test_ignore_timeout_decorator_returns_the_argument_on_error(mock_logger):

    @ignore_timeout_error('foo')
    @timeout(1)
    def f():
        time.sleep(2)

    result = f()

    assert mock_logger.error.called
    assert result == 'foo'


@pytest.mark.parametrize('source,expected_source', [
    ('publisher', 'publisher'),
    ('desy', 'publisher'),
    ('jessica jones', 'publisher'),
    ('arxiv', 'arxiv'),
    ('submitter', 'submitter'),
])
def test_get_source_root(source, expected_source):
    result = get_source_for_root(source)

    assert expected_source == result
