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

import httpretty
import pytest
from flask import current_app
from mock import patch

from inspire_dojson.hep import hep2marc
from inspire_dojson.hepnames import hepnames2marc
from inspire_dojson.utils import validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.literaturesuggest.tasks import (
    reply_ticket_context as literaturesuggest_reply_ticket_context,
)
from inspirehep.modules.workflows.tasks.submission import (
    add_note_entry,
    close_ticket,
    create_ticket,
    filter_keywords,
    prepare_files,
    prepare_keywords,
    reply_ticket,
    send_robotupload,
    wait_webcoll,
)

from mocks import AttrDict, MockEng, MockFiles, MockObj, MockUser, MockRT


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
def test_create_ticket_handles_unicode_when_not_in_production_mode(mock_render_template, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    mock_render_template.return_value = u'φοο'

    config = {'PRODUCTION_MODE': False}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        _create_ticket = create_ticket(None)

        assert _create_ticket(obj, eng) is None

        expected = (
            u'Was going to create ticket: None\n\nφοο\n\n'
            u'To: user@example.com Queue: Test'
        )
        result = obj.log._info.getvalue()

        assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_create_ticket_handles_unicode_when_in_production_mode(mock_get_instance, mock_render_template, mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')
    mock_render_template.return_value = u'φοο'
    mock_get_instance.return_value = MockRT()

    config = {'PRODUCTION_MODE': True}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        _create_ticket = create_ticket(None)

        assert _create_ticket(obj, eng) is None

        expected = {'ticket_id': 1}
        result = obj.extra_data

        assert expected == result

        expected = u'Ticket 1 created:\nφοο'
        result = obj.log._info.getvalue()

        assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_reply_ticket_thanks_the_user_when_their_literature_submission_is_received(mock_get_instance, mock_user):
    mock_rt = MockRT()
    mock_rt.create_ticket(Queue='Test', Status='new')
    mock_get_instance.return_value = mock_rt
    mock_user.query.get.return_value = MockUser('user@example.com')

    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {'ticket_id': 1}
    assert validate(data['titles'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _reply_ticket = reply_ticket(
        template='literaturesuggest/tickets/user_submitted.html',
        context_factory=literaturesuggest_reply_ticket_context,
        keep_new=True,
    )

    assert _reply_ticket(obj, eng) is None

    expected = (
        'Dear user@example.com,\n '
        '\n '
        'Thank you very much for suggesting "Partial Symmetries of Weak Interactions" '
        'to INSPIRE. It has been received and will be reviewed by our staff as '
        'soon as possible. You will hear back from us shortly.\n '
        '\n '
        'Thank you for sharing with INSPIRE!'
    )
    result = mock_rt.get_ticket(1)

    assert expected == result['text']

    expected = 'new'
    result = mock_rt.get_ticket(1)

    assert expected == result['Status']


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_reply_ticket_thanks_user_when_their_literature_submission_is_accepted(mock_get_instance, mock_user):
    mock_rt = MockRT()
    mock_rt.create_ticket(Queue='Test', Status='new')
    mock_get_instance.return_value = mock_rt
    mock_user.query.get.return_value = MockUser('user@example.com')

    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    data = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {'ticket_id': 1}
    assert validate(data['titles'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _reply_ticket = reply_ticket(
        template='literaturesuggest/tickets/user_accepted.html',
        context_factory=literaturesuggest_reply_ticket_context,
    )

    assert _reply_ticket(obj, eng) is None

    expected = (
        'Dear user@example.com,\n '
        '\n '
        'Thank you very much again for your suggestion "Partial Symmetries of Weak Interactions". '
        'It has been reviewed by our curators and is now in INSPIRE.\n '
        '\n '
        "If you have any further questions, don't hesitate to contact us.\n "
        '\n '
        'Thanks again for your submission!'
    )
    result = mock_rt.get_ticket(1)

    assert expected == result['text']

    expected = 'acknowledged'
    result = mock_rt.get_ticket(1)

    assert expected == result['Status']


def test_reply_ticket_logs_an_error_when_there_is_no_ticket_id():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _reply_ticket = reply_ticket()

    assert _reply_ticket(obj, eng) is None

    expected = 'No ticket ID found!'
    result = obj.log._error.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
def test_reply_ticket_logs_an_error_when_there_is_no_user(mock_user):
    mock_user.query.get.return_value = None

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket()

    assert _reply_ticket(obj, eng) is None

    expected = 'No user found for object 1, skipping ticket creation'
    result = obj.log._error.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
def test_reply_ticket_falls_back_to_reason_when_there_is_no_template(mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')

    data = {}
    extra_data = {
        'reason': 'reason',
        'ticket_id': 1,
    }

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket()

    assert _reply_ticket(obj, eng) is None


@patch('inspirehep.modules.workflows.tasks.submission.User')
def test_reply_ticket_logs_an_error_when_the_fallback_is_an_empty_string(mock_user):
    mock_user.query.get.return_value = MockUser('user@example.com')

    data = {}
    extra_data = {
        'reason': '',
        'ticket_id': 1,
    }

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket()

    assert _reply_ticket(obj, eng) is None

    expected = 'No body for ticket reply. Skipping reply.'
    result = obj.log._error.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_reply_ticket_logs_when_there_is_no_rt_instance(mock_get_instance, mock_render_template, mock_user):
    mock_get_instance.return_value = None
    mock_render_template.return_value = 'foo'
    mock_user.query.get.return_value = MockUser('user@example.com')

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket(template='foo')

    assert _reply_ticket(obj, eng) is None

    expected = 'No RT instance available. Skipping!'
    result = obj.log._error.getvalue()

    assert expected == result

    expected = 'Was going to reply to 1\n\nfoo\n\n'
    result = obj.log._info.getvalue()

    assert expected == result


@pytest.mark.xfail
@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_reply_ticket_handles_unicode_when_there_is_no_rt_instance(mock_get_instance, mock_render_template, mock_user):
    mock_get_instance.return_value = None
    mock_render_template.return_value = u'φοο'
    mock_user.query.get.return_value = MockUser('user@example.com')

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket(template='foo')

    assert _reply_ticket(obj, eng) is None

    expected = 'No RT instance available. Skipping!'
    result = obj.log._error.getvalue()

    assert expected == result

    expected = u'Was going to reply to 1\n\nφοο\n\n'
    result = obj.log._info.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_reply_ticket_keeps_new_status_when_requested(mock_get_instance, mock_render_template, mock_user):
    mock_rt = MockRT()
    mock_rt.create_ticket(Queue='Test', Status='new')
    mock_get_instance.return_value = mock_rt
    mock_render_template.return_value = 'foo'
    mock_user.query.get.return_value = MockUser('user@example.com')

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data, id=1, id_user=1)
    eng = MockEng()

    _reply_ticket = reply_ticket(keep_new=True, template='foo')

    assert _reply_ticket(obj, eng) is None

    expected = 'foo'
    result = mock_rt.get_ticket(1)

    assert expected == result['text']

    expected = 'new'
    result = mock_rt.get_ticket(1)

    assert expected == result['Status']


@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_close_ticket_marks_a_ticket_as_resolved(mock_get_instance):
    mock_rt = MockRT()
    mock_rt.create_ticket(Queue='Test', Status='new')
    mock_get_instance.return_value = mock_rt

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _close_ticket = close_ticket()

    assert _close_ticket(obj, eng) is None

    expected = 'resolved'
    result = mock_rt.get_ticket(1)

    assert expected == result['Status']


def test_close_ticket_logs_an_error_when_there_is_no_ticket_id():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _close_ticket = close_ticket()

    assert _close_ticket(obj, eng) is None

    expected = 'No ticket ID found!'
    result = obj.log._error.getvalue()

    assert expected == result


def test_close_ticket_logs_when_there_is_no_rt_instance():
    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _close_ticket = close_ticket()

    assert _close_ticket(obj, eng) is None

    expected = 'No RT instance available. Skipping!'
    result = obj.log._error.getvalue()

    assert expected == result

    expected = 'Was going to close ticket 1'
    result = obj.log._info.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_close_ticket_logs_a_warning_if_the_ticket_is_already_resolved(mock_get_instance):
    mock_rt = MockRT()
    mock_rt.create_ticket(Queue='Test', Status='resolved')
    mock_get_instance.return_value = mock_rt

    data = {}
    extra_data = {'ticket_id': 1}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _close_ticket = close_ticket()

    assert _close_ticket(obj, eng) is None

    expected = 'Ticket is already resolved.'
    result = obj.log._warning.getvalue()

    assert expected == result


@pytest.mark.httpretty
def test_send_robotupload_works_with_mode_correct_and_extra_data_key():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/correct',
        body='[INFO] foo bar baz')

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

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_send_robotupload_works_with_hep2marc_and_mode_insert():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/insert',
        body='[INFO] foo bar baz')

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

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_send_robotupload_works_with_hepnames2marc_and_mode_insert():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/insert',
        body='[INFO] foo bar baz')

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

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_send_robotupload_works_with_mode_holdingpen_and_without_callback_url():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/holdingpen',
        body='[INFO] foo bar baz')

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

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_send_robotupload_logs_on_error_response():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/insert',
        body='[ERROR] cannot use the service')

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
            'Your IP is not in app.config_BATCHUPLOADER_WEB_ROBOT_RIGHTS on host'
            '[ERROR] cannot use the service'
        )
        result = obj.log._error.getvalue()

        assert expected == result

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_send_robotupload_does_nothing_when_not_in_production_mode():
    httpretty.HTTPretty.allow_net_connect = False

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

    httpretty.HTTPretty.allow_net_connect = True


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


def test_add_note_entry():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    data = {
        'public_notes': [
            {'value': 'Reprinted in *Duff, M.J. (ed.): The world in eleven dimensions* 492-513'},
        ],
    }
    extra_data = {}
    assert validate(data['public_notes'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert add_note_entry(obj, eng) is None

    expected = [
        {'value': 'Reprinted in *Duff, M.J. (ed.): The world in eleven dimensions* 492-513'},
        {'value': '*Brief entry*'},
    ]
    result = obj.data

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_add_note_entry_creates_public_notes_if_not_present():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert add_note_entry(obj, eng) is None

    expected = [
        {'value': '*Brief entry*'},
    ]
    result = obj.data

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


def test_add_note_entry_does_not_add_value_that_is_already_present():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    data = {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ],
    }
    extra_data = {'core': 'something'}
    assert validate(data['public_notes'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert add_note_entry(obj, eng) is None

    expected = [
        {'value': '*Temporary entry*'},
    ]
    result = obj.data

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']


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


def test_prepare_files():
    schema = load_schema('hep')
    subschema = schema['properties']['_fft']

    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None

    expected = [
        {
            'path': '/data/foo.pdf',
            'type': 'INSPIRE-PUBLIC',
            'filename': 'foo',
            'format': '.pdf',
        },
    ]
    result = obj.data

    assert validate(result['_fft'], subschema) is None
    assert expected == result['_fft']

    expected = 'Non-user PDF files added to FFT.'
    result = obj.log._info.getvalue()

    assert expected == result


def test_prepare_files_annotates_files_from_arxiv():
    schema = load_schema('hep')
    _fft_schema = schema['properties']['_fft']
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th'
                ],
                'value': 'hep-th/9711200',
            },
        ],
    }
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None

    expected_fft = [
        {
            'path': '/data/foo.pdf',
            'type': 'arXiv',
            'filename': 'arxiv:foo',
            'format': '.pdf',
        },
    ]
    expected_arxiv_eprints = [
        {
            'categories': [
                'hep-th',
            ],
            'value': 'hep-th/9711200',
        },
    ]
    result = obj.data

    assert validate(result['_fft'], _fft_schema) is None
    assert expected_fft == result['_fft']

    assert validate(result['arxiv_eprints'], arxiv_eprints_schema) is None
    assert expected_arxiv_eprints == result['arxiv_eprints']

    expected = 'Non-user PDF files added to FFT.'
    result = obj.log._info.getvalue()

    assert expected == result


def test_prepare_files_skips_empty_files():
    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({}),
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None

    expected = {}
    result = obj.data

    assert expected == result

    expected = ''
    result = obj.log._info.getvalue()

    assert expected == result


def test_prepare_files_does_nothing_when_obj_has_no_files():
    data = {}
    extra_data = {}
    files = MockFiles({})

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None

    expected = {}
    result = obj.data

    assert expected == result

    expected = ''
    result = obj.log._info.getvalue()

    assert expected == result


def test_prepare_files_ignores_keys_not_ending_with_pdf():
    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.bar': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None

    expected = {}
    result = obj.data

    assert expected == result

    expected = ''
    result = obj.log._info.getvalue()

    assert expected == result
