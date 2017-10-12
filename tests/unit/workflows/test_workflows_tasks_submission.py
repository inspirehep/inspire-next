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
import requests_mock
from flask import current_app
from mock import patch

from inspire_dojson.hep import hep2marc
from inspire_dojson.hepnames import hepnames2marc
from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.submission import (
    close_ticket,
    create_ticket,
    filter_keywords,
    prepare_keywords,
    remove_references,
    reply_ticket,
    send_robotupload,
    wait_webcoll,
)

from mocks import MockEng, MockObj, MockUser


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.tickets.reply_ticket_with_template')
@patch('inspirehep.modules.workflows.tasks.submission.rt_instance', lambda: True)
def test_reply_ticket_calls_tickets_reply_with_template_when_template_is_set(mock_reply_ticket_with_template, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {'ticket_id': 1}
    template = 'template_path'
    obj = MockObj(data, extra_data)
    eng = MockEng()
    _reply_ticket = reply_ticket(template=template)
    _reply_ticket(obj, eng)
    mock_reply_ticket_with_template.assert_called_with(
        extra_data['ticket_id'],
        template,
        {},
        False
    )


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.tickets.reply_ticket')
@patch('inspirehep.modules.workflows.tasks.submission.rt_instance', lambda: True)
def test_reply_ticket_calls_tickets_reply_when_template_is_not_set(mock_reply_ticket, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {'ticket_id': 1, 'reason': 'reply reason'}
    obj = MockObj(data, extra_data)
    eng = MockEng()
    _reply_ticket = reply_ticket()
    _reply_ticket(obj, eng)
    mock_reply_ticket.assert_called_with(
        extra_data['ticket_id'],
        extra_data['reason'],
        False
    )


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.tickets.resolve_ticket')
@patch('inspirehep.modules.workflows.tasks.submission.rt_instance', lambda: True)
def test_close_ticket_calls_tickets_resolve(mock_resolve_ticket, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {'ticket_id': 1}
    obj = MockObj(data, extra_data)
    eng = MockEng()
    _close_ticket = close_ticket()
    _close_ticket(obj, eng)
    mock_resolve_ticket.assert_called_with(
        extra_data['ticket_id']
    )


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.tickets.create_ticket_with_template')
@patch('inspirehep.modules.workflows.tasks.submission.rt_instance', lambda: True)
def test_create_ticket_calls_tickets_create_with_template(mock_create_ticket_with_template, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    template = 'template_path'
    extra_data = {'recid': '1'}
    obj = MockObj(data, extra_data)
    eng = MockEng()
    _create_ticket = create_ticket(template=template)
    _create_ticket(obj, eng)
    mock_create_ticket_with_template.assert_called_with(
        'Test',
        'user@example.com',
        template,
        {},
        None,
        extra_data['recid']
    )


def test_send_robotupload_works_with_mode_correct_and_extra_data_key():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/correct',
            text='[INFO] foo bar baz'
        )

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': True,
        }

        with patch.dict(current_app.config, config):
            data = {}
            extra_data = {
                'update_payload': {
                    'arxiv_eprints': [
                        {
                            'categories': [
                                'hep-th',
                            ],
                            'value': 'hep-th/9711200',
                        },
                    ],
                },
            }

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hep2marc,
                mode='correct',
                extra_data_key='update_payload',
            )

            assert _send_robotupload(obj, eng) is None

            expected = (
                'Robotupload sent!'
                '[INFO] foo bar baz'
                'end of upload'
            )
            result = obj.log._info.getvalue()

            assert expected == result

            expected = 'Waiting for robotupload: [INFO] foo bar baz'
            result = eng.msg

            assert expected == result


def test_send_robotupload_works_with_hep2marc_and_mode_insert():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/insert',
            text='[INFO] foo bar baz'
        )

        schema = load_schema('hep')
        subschema = schema['properties']['arxiv_eprints']

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': True,
        }

        with patch.dict(current_app.config, config):
            data = {
                'arxiv_eprints': [
                    {
                        'categories': [
                            'hep-th',
                        ],
                        'value': 'hep-th/9711200',
                    },
                ],
            }
            extra_data = {}
            assert validate(data['arxiv_eprints'], subschema) is None

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hep2marc,
                mode='insert',
            )

            assert _send_robotupload(obj, eng) is None

            expected = (
                'Robotupload sent!'
                '[INFO] foo bar baz'
                'end of upload'
            )
            result = obj.log._info.getvalue()

            assert expected == result

            expected = 'Waiting for robotupload: [INFO] foo bar baz'
            result = eng.msg

            assert expected == result


def test_send_robotupload_works_with_hepnames2marc_and_mode_insert():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/insert',
            text='[INFO] foo bar baz'
        )

        schema = load_schema('authors')
        subschema = schema['properties']['arxiv_categories']

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': True,
        }

        with patch.dict(current_app.config, config):
            data = {
                'arxiv_categories': [
                    'hep-th',
                ],
            }
            extra_data = {}
            assert validate(data['arxiv_categories'], subschema) is None

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hepnames2marc,
                mode='insert',
            )

            assert _send_robotupload(obj, eng) is None

            expected = (
                'Robotupload sent!'
                '[INFO] foo bar baz'
                'end of upload'
            )
            result = obj.log._info.getvalue()

            assert expected == result

            expected = 'Waiting for robotupload: [INFO] foo bar baz'
            result = eng.msg

            assert expected == result


def test_send_robotupload_works_with_mode_holdingpen_and_without_callback_url():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/holdingpen',
            text='[INFO] foo bar baz'
        )

        schema = load_schema('authors')
        subschema = schema['properties']['arxiv_categories']

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': True,
        }

        with patch.dict(current_app.config, config):
            data = {
                'arxiv_categories': [
                    'hep-th',
                ],
            }
            extra_data = {}
            assert validate(data['arxiv_categories'], subschema) is None

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hepnames2marc,
                mode='holdingpen',
                callback_url=None,
            )

            assert _send_robotupload(obj, eng) is None

            expected = (
                'Robotupload sent!'
                '[INFO] foo bar baz'
                'end of upload'
            )
            result = obj.log._info.getvalue()

            assert expected == result


def test_send_robotupload_logs_on_error_response():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/insert',
            text='[ERROR] cannot use the service'
        )

        schema = load_schema('hep')
        subschema = schema['properties']['arxiv_eprints']

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': True,
        }

        with patch.dict(current_app.config, config):
            data = {
                'arxiv_eprints': [
                    {
                        'categories': [
                            'hep-th',
                        ],
                        'value': 'hep-th/9711200',
                    },
                ],
            }
            extra_data = {}
            assert validate(data['arxiv_eprints'], subschema) is None

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hep2marc,
                mode='insert',
            )

            with pytest.raises(Exception) as excinfo:
                _send_robotupload(obj, eng)

            expected = (
                'Error while submitting robotupload: '
                '[ERROR] cannot use the service'
            )
            result = str(excinfo.value)

            assert expected == result

            expected = (
                'Your IP is not in app.config_BATCHUPLOADER_WEB_ROBOT_RIGHTS on host: '
                '[ERROR] cannot use the service'
            )
            result = obj.log._error.getvalue()

            assert expected == result


def test_send_robotupload_does_nothing_when_not_in_production_mode():
    with requests_mock.Mocker():
        schema = load_schema('hep')
        subschema = schema['properties']['arxiv_eprints']

        config = {
            'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net',
            'PRODUCTION_MODE': False,
        }

        with patch.dict(current_app.config, config):
            data = {
                'arxiv_eprints': [
                    {
                        'categories': [
                            'hep-th',
                        ],
                        'value': 'hep-th/9711200',
                    },
                ],
            }
            extra_data = {}
            assert validate(data['arxiv_eprints'], subschema) is None

            obj = MockObj(data, extra_data)
            eng = MockEng()

            _send_robotupload = send_robotupload(
                marcxml_processor=hep2marc,
                mode='insert',
            )

            assert _send_robotupload(obj, eng) is None


def test_wait_webcoll_halts_the_workflow_engine_when_in_production_mode():
    config = {'PRODUCTION_MODE': True}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        assert wait_webcoll(obj, eng) is None

        expected = 'Waiting for webcoll.'
        result = eng.msg

        assert expected == result


def test_wait_webcoll_does_nothing_otherwise():
    config = {'PRODUCTION_MODE': False}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        assert wait_webcoll(obj, eng) is None


def test_filter_keywords():
    data = {}
    extra_data = {
        'keywords_prediction': {
            'keywords': [
                {
                    'accept': True,
                    'label': 'galaxy',
                },
                {
                    'accept': True,
                    'label': 'numerical calculations',
                },
                {
                    'accept': False,
                    'label': 'numerical calculations: interpretation of experiments',
                },
            ],
        },
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert filter_keywords(obj, eng) is None

    expected = [
        {
            'accept': True,
            'label': 'galaxy',
        },
        {
            'accept': True,
            'label': 'numerical calculations',
        },
    ]
    result = obj.extra_data['keywords_prediction']

    assert expected == result['keywords']


def test_filter_keywords_does_nothing_if_no_keywords_were_predicted():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert filter_keywords(obj, eng) is None

    expected = {}
    result = obj.extra_data

    assert expected == result


def test_prepare_keywords():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    data = {}
    extra_data = {
        'keywords_prediction': {
            'keywords': [
                {'label': 'galaxy'},
                {'label': 'numerical calculations'},
            ],
        },
    }

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert prepare_keywords(obj, eng) is None

    expected = [
        {
            'source': 'magpie',
            'value': 'galaxy',
        },
        {
            'source': 'magpie',
            'value': 'numerical calculations',
        },
    ]
    result = obj.data

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']


def test_prepare_keywords_appends_to_existing_keywords():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    data = {
        'keywords': [
            {
                'schema': 'INSPIRE',
                'value': 'field theory: conformal',
            },
        ],
    }
    extra_data = {
        'keywords_prediction': {
            'keywords': [
                {'label': 'expansion 1/N'},
                {'label': 'supergravity'},
            ],
        },
    }
    assert validate(data['keywords'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert prepare_keywords(obj, eng) is None

    expected = [
        {
            'schema': 'INSPIRE',
            'value': 'field theory: conformal',
        },
        {
            'source': 'magpie',
            'value': 'expansion 1/N',
        },
        {
            'source': 'magpie',
            'value': 'supergravity',
        },
    ]
    result = obj.data

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']


def test_prepare_keywords_does_nothing_if_no_keywords_were_predicted():
    schema = load_schema('hep')
    subschema = schema['properties']['keywords']

    data = {
        'keywords': [
            {
                'schema': 'INSPIRE',
                'value': 'field theory: conformal',
            },
        ],
    }
    extra_data = {}
    assert validate(data['keywords'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert prepare_keywords(obj, eng) is None

    expected = [
        {
            'schema': 'INSPIRE',
            'value': 'field theory: conformal',
        },
    ]
    result = obj.data

    assert validate(result['keywords'], subschema) is None
    assert expected == result['keywords']


def test_remove_references():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    data = {
        'references': [
            {
                'reference': {
                    'arxiv_eprint': 'hep-th/9710014',
                    'authors': [
                        {'full_name': 'Maldacena, J.'},
                        {'full_name': 'Strominger, A.'},
                    ],
                    'label': '1',
                },
            },
        ],
    }
    extra_data = {}
    assert validate(data['references'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert remove_references(obj, eng) is None

    expected = {}
    result = obj.data

    assert expected == result


def test_remove_references_does_nothing_when_there_are_no_references():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert remove_references(obj, eng) is None

    expected = {}
    result = obj.data

    assert expected == result
