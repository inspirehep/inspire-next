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

from inspirehep.modules.workflows.tasks.actions import check_if_uk_in_raw_affiliations, jlab_ticket_needed, load_from_source_data, \
    extract_authors_from_pdf, is_suitable_for_pdf_authors_extraction, is_fermilab_report, add_collection, \
    check_if_france_in_fulltext, check_if_france_in_raw_affiliations, check_if_germany_in_fulltext, \
    check_if_germany_in_raw_affiliations, check_if_uk_in_fulltext


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
    obj.data = {
        'authors': [
            {"full_name": "author 1"},
            {"full_name": "author 2"},
            {"full_name": "author 3"}
        ]
    }
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
def test_extract_authors_from_pdf_number_of_authors_is_same_after_merge_with_grobid(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )

    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1"}
        ]
    }
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
    assert len(obj.data['authors']) == 1
    assert len(obj.extra_data.get('authors_with_affiliations')) == 3


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_when_no_authors_in_metadata(mocked_get_document, app):
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
    assert len(obj.data['authors']) == 3
    assert len(obj.extra_data['authors_with_affiliations']) == 3


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_when_no_authors_in_metadata_and_no_authors_from_grobid(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_no_authors_doc.xml'
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
    assert 'authors' not in obj.data
    assert 'authors_with_affiliations' not in obj.extra_data


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_merges_grobid_affiliations(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )

    obj = MagicMock()
    obj.data = {
        "authors": [
            {
                'raw_affiliations': [{'value': u'S. N. Bose National Centre, India'}],
                'emails': [u'parthanandi@bose.res.in'],
                'full_name': u'Nandi, Partha'},
            {
                'raw_affiliations': [{'value': u'IIEST, Shibpur, Howrah, West Bengal-711103, India.'}],
                'full_name': u'Sahu, Sankarshan'},
            {
                'raw_affiliations': [{'value': u'S. N. Bose National Centre, India.'}],
                'full_name': u'Pal, Sayan Kumar'
            }
        ]
    }
    obj.extra_data = {}
    eng = None

    expected_authors = [
        {
            'raw_affiliations': [
                {'value': u'S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India.'}
            ],
            'emails': [u'parthanandi@bose.res.in'], 'full_name': u'Nandi, Partha'
        },
        {
            'raw_affiliations': [
                {'value': u'Indian Institute of Engineering Science and Technology, Shibpur, Howrah, West Bengal-711103, India.'}
            ], 'emails': [u'sankarshan.sahu2000@gmail.com'], 'full_name': u'Sahu, Sankarshan'
        },
        {
            'raw_affiliations': [
                {'value': u'S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India.'}
            ], 'emails': [u'sayankpal@bose.res.in'], 'full_name': u'Pal, Sayan Kumar'
        }
    ]

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

    assert obj.data['authors'] == expected_authors
    assert len(obj.extra_data['authors_with_affiliations']) == 3


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


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_extract_authors_from_pdf_do_not_run_when_there_is_more_authors_than_max_authors_parameter(mocked_get_document,
                                                                                                   app):
    mocked_get_document.return_value.__enter__.side_effect = Exception
    max_authors_parameter = app.config.get('WORKFLOWS_MAX_AUTHORS_COUNT_FOR_GROBID_EXTRACTION') + 1
    obj = MagicMock()
    obj.data = {'authors': [i for i in range(max_authors_parameter)]}
    # Should not raise exception
    extract_authors_from_pdf(obj, None)


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_france_in_fulltext_when_france_in_header(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_authors_full_response.txt'
        )
    )

    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1"},
            {"full_name": "author 2"},
            {"full_name": "author 3"}
        ]
    }

    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                france_in_fulltext = check_if_france_in_fulltext(obj, eng)

    assert france_in_fulltext


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_france_in_fulltext_doesnt_include_francesco(mocked_get_document, app):
    fake_grobid_response = "<author>Francesco, Papa</author>"

    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1"},
            {"full_name": "author 2"},
            {"full_name": "author 3"}
        ]
    }

    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=fake_grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                france_in_fulltext = check_if_france_in_fulltext(obj, eng)

    assert not france_in_fulltext


def test_check_if_france_in_affiliations(app):
    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Laboratoire de Physique des 2 Infinis Irene Joliot-Curie (IJCLab), CNRS, Université Paris-Saclay, Orsay, 91405, France"}]

             }
        ]
    }

    obj.extra_data = {}
    eng = None
    result = check_if_france_in_raw_affiliations(obj, eng)
    assert result


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_france_in_fulltext_when_france_in_text_body(mocked_get_document, app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_response_fulltext.txt'
        )
    )

    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1"},
            {"full_name": "author 2"},
            {"full_name": "author 3"}
        ]
    }

    obj.extra_data = {}
    eng = None

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                france_in_fulltext = check_if_france_in_fulltext(obj, eng)

    assert france_in_fulltext


def test_check_if_germany_in_affiliations(app):
    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Laboratoire de Physique des 2 Infinis Irene Joliot-Curie (IJCLab), CNRS, Université Paris-Saclay, Orsay, 91405, Germany"}]

             }
        ]
    }

    obj.extra_data = {}
    eng = None
    result = check_if_germany_in_raw_affiliations(obj, eng)
    assert result


def test_check_if_deutschland_in_affiliations(app):
    obj = MagicMock()
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Laboratoire de Physique des 2 Infinis Irene Joliot-Curie (IJCLab), CNRS, Université Paris-Saclay, Orsay, 91405, Deutschland"}]

             }
        ]
    }

    obj.extra_data = {}
    eng = None
    result = check_if_germany_in_raw_affiliations(obj, eng)
    assert result


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_germany_in_fulltext_when_germany_in_text_body(mocked_get_document, app):
    fake_grobid_response = "<country key=\"DE\">Germany</country>"
    obj = MagicMock()
    obj.data = {
        'core': False
    }
    obj.extra_data = {}
    eng = None
    new_config = {"GROBID_URL": "http://grobid_url.local"}

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=fake_grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                germany_in_fulltext = check_if_germany_in_fulltext(obj, eng)

    assert germany_in_fulltext


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_germany_in_fulltext_when_deutschland_in_text_body(mocked_get_document, app):
    fake_grobid_response = "<country key=\"DE\">Deutschland</country>"
    obj = MagicMock()
    obj.data = {
        'core': False
    }
    obj.extra_data = {}
    eng = None
    new_config = {"GROBID_URL": "http://grobid_url.local"}

    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=fake_grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                germany_in_fulltext = check_if_germany_in_fulltext(obj, eng)

    assert germany_in_fulltext


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_uk_in_fulltext(mocked_get_document, app):
    fake_grobid_response = "<country key=\"UK\">England</country>"
    obj = MagicMock()
    obj.extra_data = {}
    eng = None
    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=fake_grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                uk_in_fulltext = check_if_uk_in_fulltext(
                    obj, eng)

    assert uk_in_fulltext


@patch("inspirehep.modules.workflows.tasks.actions.get_document_in_workflow")
def test_check_if_uk_in_fulltext_case_insensitive(mocked_get_document, app):
    fake_grobid_response = "<country>unitEd KiNgdOm</country>"
    obj = MagicMock()
    obj.extra_data = {}
    eng = None
    new_config = {"GROBID_URL": "http://grobid_url.local"}
    with patch.dict(current_app.config, new_config):
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                'POST', 'http://grobid_url.local/api/processFulltextDocument',
                text=fake_grobid_response,
                headers={'content-type': 'application/xml'},
                status_code=200,
            )
            with tempfile.NamedTemporaryFile() as tmp_file:
                mocked_get_document.return_value.__enter__.return_value = tmp_file.name
                uk_in_fulltext_and_core = check_if_uk_in_fulltext(
                    obj, eng)

    assert uk_in_fulltext_and_core


def test_check_if_uk_in_affiliations(app):
    obj = MagicMock()
    obj.extra_data = {}
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam, 91405, UK"}]

             }
        ]
    }
    result = check_if_uk_in_raw_affiliations(obj, None)
    assert result
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Lorem ipsum dolor united kingdom amet, consetetur sadipscing elitr, sed diam, 91405"}]

             }
        ]
    }
    result = check_if_uk_in_raw_affiliations(obj, None)
    assert result
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Lorem ipsum dolor sit amet, Scotland sadipscing elitr, sed diam, 91405"}]

             }
        ]
    }
    result = check_if_uk_in_raw_affiliations(obj, None)
    assert result
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Lorem engLand dolor sit amet, sadipscing elitr, sed diam, 91405"}]

             }
        ]
    }
    result = check_if_uk_in_raw_affiliations(obj, None)
    assert result
    obj.data = {
        'authors': [
            {"full_name": "author 1",
             "raw_affiliations": [{"value": "Lorem ipsum dolor sit amet, Northern ireland, sed diam, 91405"}]

             }
        ]
    }
    result = check_if_uk_in_raw_affiliations(obj, None)
    assert result
