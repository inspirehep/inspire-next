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

import tempfile

import os

import pkg_resources
import pytest
import requests_mock
from flask import current_app
from invenio_workflows import ObjectStatus
from mock import patch, MagicMock

from inspirehep.modules.workflows.actions import MatchApproval, MergeApproval
from mocks import MockEng, MockObj

from inspirehep.modules.workflows.tasks.actions import jlab_ticket_needed, load_from_source_data, \
    extract_authors_from_pdf, is_suitable_for_pdf_authors_extraction, is_fermilab_report, add_collection


def test_match_approval_gets_match_recid():
    data = {}
    extra_data = {}
    obj = MockObj(data, extra_data)

    ui_data = {'match_recid': 1234}
    result = MatchApproval.resolve(obj, request_data=ui_data)

    assert result
    assert 'fuzzy_match_approved_id' in obj.extra_data
    assert obj.extra_data['fuzzy_match_approved_id'] == 1234


def test_match_approval_gets_none():
    data = {}
    extra_data = {}
    obj = MockObj(data, extra_data)

    ui_data = {'request_data': {'match_recid': None}}
    result = MatchApproval.resolve(obj, ui_data)

    assert not result
    assert 'fuzzy_match_approved_id' in obj.extra_data
    assert obj.extra_data['fuzzy_match_approved_id'] is None


def test_match_approval_nothing_sent_via_request():
    data = {}
    extra_data = {}
    obj = MockObj(data, extra_data)

    result = MatchApproval.resolve(obj, None)

    assert not result
    assert 'fuzzy_match_approved_id' in obj.extra_data
    assert obj.extra_data['fuzzy_match_approved_id'] is None
    assert obj.status == ObjectStatus.RUNNING


def test_merge_approval():
    data = {}
    extra_data = {}
    obj = MockObj(data, extra_data)
    obj.workflow.name = 'manual_merge'

    result = MergeApproval.resolve(obj)

    assert result
    assert obj.extra_data['approved']
    assert not obj.extra_data['auto-approved']


def test_jlab_ticket_needed_returns_false():
    config = {'JLAB_ARXIV_CATEGORIES': ['nucl-th']}

    with patch.dict(current_app.config, config):
        data = {
            'arxiv_eprints': [
                {
                    'categories': ['math.DG'],
                    'value': '1806.03979'
                }
            ]
        }
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        assert jlab_ticket_needed(obj, eng) is False


def test_jlab_ticket_needed_returns_true():
    config = {'JLAB_ARXIV_CATEGORIES': ['nucl-th']}

    with patch.dict(current_app.config, config):
        extra_data = {}
        data = {
            'arxiv_eprints': [
                {
                    'categories': ['nucl-th', 'hep-th'],
                    'value': '1806.03979'
                }
            ]
        }

        obj = MockObj(data, extra_data)
        eng = MockEng()

        assert jlab_ticket_needed(obj, eng) is True


def test_load_from_source_data_no_persistent_data():
    data = {
        'document_type': 'article',
        'titles': [{
            'title': 'Changed in previous workflow run'
        }]
    }

    extra_data = {
        '_last_task_name': 'whatever',
        'source_data': {
            'data': {
                'document_type': 'article',
                'titles': [{
                    'title': 'Original title'
                }]
            },
            'extra_data': {}
        }
    }

    expected_data = {
        'document_type': 'article',
        'titles': [{
            'title': 'Original title'
        }]
    }

    expected_extra_data = {
        'source_data': {
            'extra_data': {
                '_task_history': []
            },
            'data': {
                'document_type': 'article',
                'titles': [
                    {
                        'title': 'Original title'
                    }
                ]
            }
        },
        '_task_history': [],
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()

    load_from_source_data(obj, eng)

    assert obj.data == expected_data
    assert obj.extra_data == expected_extra_data


@pytest.mark.parametrize(
    "report_numbers, expected",
    [
        (["REPORT-NUMBER-1", "REPORT-NUMBER-NOT-FERMILAB-11"], False),
        (["REPORT-1", "FERMILAB-2"], True),
        (["FERMILAB-1", "FERMILAB-2"], True),
        (["FERMILAB-ONB"], True),
        (["NOT-FERMILAB-ONE"], False),
        (["fermilab-lowercase"], False),
    ]
)
def test_is_fermilab_report(report_numbers, expected):
    wf_mock = MagicMock()
    wf_mock.data = {}
    if report_numbers:
        wf_mock.data['report_numbers'] = [{"value": number} for number in report_numbers]
    assert is_fermilab_report(wf_mock, None) is expected


@pytest.mark.parametrize(
    "current_collections, new_collection, expected",
    [
        ([], "Fermilab", ["Fermilab"]),
        (["Literature"], "Fermilab", ["Literature", "Fermilab"]),
        (['Literature'], "Literature", ["Literature"]),
    ]
)
def test_add_collection(current_collections, new_collection, expected):
    wf = MagicMock()
    wf.data = {"_collections": current_collections}
    add_collection(new_collection)(wf, None)
    assert wf.data['_collections'] == expected


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )

    obj = MagicMock()
    obj.data = {'authors': [1, 2, 3]}
    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processHeaderDocument',
                text=grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                extract_authors_from_pdf(obj, eng)
    assert len(obj.data['authors']) == 3
    assert len(obj.extra_data['authors_with_affiliations']) == 3


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_ignored_when_different_author_count(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )

    obj = MagicMock()
    obj.data = {'authors': []}
    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processHeaderDocument',
                text=grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                extract_authors_from_pdf(obj, eng)
    assert len(obj.data['authors']) == 0
    assert obj.extra_data.get('authors_with_affiliations') is None


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_ignored_when_authors_is_missing(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )

    obj = MagicMock()
    obj.data = {}
    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processHeaderDocument',
                text=grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                extract_authors_from_pdf(obj, eng)
    assert len(obj.data['authors']) == 0
    assert obj.extra_data.get('authors_with_affiliations') is None


@pytest.mark.parametrize(
    "acquisition_source, authors_xml_mark, expected",
    [
        ("arxiv", False, True),
        ("arxiv", True, False),
        ("pos", False, True),
        ('pos', True, False),
        ("ARxIV", False, True),
        ("pOs", False, True),
        ("ARXIV", True, False),
        ("other", True, False),
        ("other", False, False),
        ("", False, False),
        ("", True, False)
    ]
)
def test_is_suitable_for_pdf_authors_extraction(acquisition_source, authors_xml_mark, expected):
    eng = None
    obj = MagicMock()
    obj.data = {"acquisition_source": {"source": acquisition_source}}
    obj.extra_data = {'authors_xml': authors_xml_mark}
    suitable = is_suitable_for_pdf_authors_extraction(obj, eng)
    assert suitable is expected
