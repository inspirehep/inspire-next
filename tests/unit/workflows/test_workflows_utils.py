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

from inspirehep.modules.workflows.utils.grobid_authors_parser import GrobidAuthors


def test_download_file_to_workflow_retries_on_protocol_error():
    with requests_mock.Mocker() as requests_mocker:
        filename = pkg_resources.resource_filename(
            __name__, os.path.join('fixtures', '1605.03844.pdf'))

        requests_mocker.register_uri(
            'GET', 'https://arxiv.org/pdf/1605.03844', [
                {'exc': requests.packages.urllib3.exceptions.ProtocolError},
                {'body': filename, 'status_code': 200},
            ])

        data = {}
        extra_data = {}
        files = MockFiles({})

        obj = MockObj(data, extra_data, files=files)

        expected = MockFileObject(key='1605.03844.pdf')
        result = download_file_to_workflow(
            obj, '1605.03844.pdf', 'https://arxiv.org/pdf/1605.03844')

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


def test_process_grobid_authors():
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )
    expected_authors = [
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                    "address": {
                        "country": u"India",
                        "cities": [u"Kolkata-700106"],
                        "postal_address": u"Sector III, Salt Lake, Kolkata-700106, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"parthanandi@bose.res.in"],
                "full_name": u"Nandi, Partha",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [
                        u"Indian Institute of Engineering Science and Technology"
                    ],
                    "address": {
                        "country": u"India",
                        "cities": [u"Shibpur, Howrah"],
                        "postal_address": u"Shibpur, Howrah, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"Indian Institute of Engineering Science and Technology, Shibpur, Howrah, West Bengal-711103, India."
                    }
                ],
                "emails": [u"sankarshan.sahu2000@gmail.com"],
                "full_name": u"Sahu, Sankarshan",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                    "address": {
                        "country": u"India",
                        "cities": [u"Kolkata-700106"],
                        "postal_address": u"Sector III, Salt Lake, Kolkata-700106, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"sayankpal@bose.res.in"],
                "full_name": u"Pal, Sayan Kumar",
            },
        },
    ]

    expected_authors_count = len(expected_authors)

    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_incomplete_authors():
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_incomplete_doc.xml'
        )
    )
    expected_authors = [
        {"parsed_affiliations": None, "author": {"full_name": u"Nandi"}},
        {
            "parsed_affiliations": [
                {
                    "address": {
                        "cities": [u"Shibpur, Howrah"],
                        "postal_address": u"Shibpur, Howrah",
                    }
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"Indian Institute of Engineering Science and Technology, Shibpur, Howrah, West Bengal-711103, India."
                    }
                ],
                "full_name": u"Sahu, Sankarshan",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"sayankpal@bose.res.in"],
                "full_name": u"Pal, Sayan Kumar",
            },
        },
    ]

    expected_authors_count = len(expected_authors)
    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_no_authors():
    input_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<TEI xml:space="preserve"
    xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.tei-c.org/ns/1.0 /opt/grobid/grobid-home/schemas/xsd/Grobid.xsd"
    xmlns:xlink="http://www.w3.org/1999/xlink">
    <teiHeader xml:lang="en">
        <fileDesc>
            <titleStmt>
                <title level="a" type="main">Remarks on noncommutativity and scale anomaly in planar quantum mechanics</title>
            </titleStmt>
            <publicationStmt>
                <publisher/>
                <availability status="unknown">
                    <licence/>
                </availability>
                <date type="published" when="2021-01-21">January 21, 2021</date>
            </publicationStmt>
            <sourceDesc>
                <biblStruct>
                    <analytic>
                    </analytic>
                    <monogr>
                        <imprint>
                            <date type="published" when="2021-01-21">January 21, 2021</date>
                        </imprint>
                    </monogr>
                    <idno type="arXiv">arXiv:2101.07076v2[hep-th]</idno>
                </biblStruct>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <appInfo>
                <application version="0.6.1" ident="GROBID" when="2021-02-09T09:29+0000">
                    <desc>GROBID - A machine learning software for extracting information from scholarly documents</desc>
                    <ref target="https://github.com/kermitt2/grobid"/>
                </application>
            </appInfo>
        </encodingDesc>
        <profileDesc>
            <abstract/>
        </profileDesc>
    </teiHeader>
    <text xml:lang="en"></text>
</TEI>
    """
    expected_authors = []
    expected_authors_count = 0
    authors = GrobidAuthors(input_xml)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_empty_author():
    input_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<TEI xml:space="preserve"
    xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.tei-c.org/ns/1.0 /opt/grobid/grobid-home/schemas/xsd/Grobid.xsd"
    xmlns:xlink="http://www.w3.org/1999/xlink">
    <teiHeader xml:lang="en">
        <fileDesc>
            <titleStmt>
                <title level="a" type="main">Remarks on noncommutativity and scale anomaly in planar quantum mechanics</title>
            </titleStmt>
            <publicationStmt>
                <publisher/>
                <availability status="unknown">
                    <licence/>
                </availability>
                <date type="published" when="2021-01-21">January 21, 2021</date>
            </publicationStmt>
            <sourceDesc>
                <biblStruct>
                    <analytic>
                     <author>
                            <persName
                                xmlns="http://www.tei-c.org/ns/1.0">
                                <forename type="first"> FIRST </forename>
                                <surname></surname>
                            </persName>
                            <email> email@cern.io </email>
                     </author>
                     <author>
                            <persName
                                xmlns="http://www.tei-c.org/ns/1.0">
                                <forename type="first">XYZ</forename>
                                <surname>ABC</surname>
                            </persName>
                            <email>   </email>
                     </author>
                      <author>
                            <persName
                                xmlns="http://www.tei-c.org/ns/1.0">
                                <forename type="first">   </forename>
                                <surname>YZC</surname>
                            </persName>
                            <email> some@email.cern </email>
                     </author>
                    </analytic>
                    <monogr>
                        <imprint>
                            <date type="published" when="2021-01-21">January 21, 2021</date>
                        </imprint>
                    </monogr>
                    <idno type="arXiv">arXiv:2101.07076v2[hep-th]</idno>
                </biblStruct>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
            <appInfo>
                <application version="0.6.1" ident="GROBID" when="2021-02-09T09:29+0000">
                    <desc>GROBID - A machine learning software for extracting information from scholarly documents</desc>
                    <ref target="https://github.com/kermitt2/grobid"/>
                </application>
            </appInfo>
        </encodingDesc>
        <profileDesc>
            <abstract/>
        </profileDesc>
    </teiHeader>
    <text xml:lang="en"></text>
</TEI>
    """
    expected_authors = [{'parsed_affiliations': None, 'author': {'full_name': u'Abc, Xyz'}}, {'parsed_affiliations': None, 'author': {'emails': [u'some@email.cern'], 'full_name': u'Yzc'}}]
    expected_authors_count = 2
    authors = GrobidAuthors(input_xml)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors
