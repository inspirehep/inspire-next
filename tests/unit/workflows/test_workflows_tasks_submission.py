# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspirehep.modules.workflows.tasks.submission import (
    submit_rt_ticket,
    create_ticket,
    reply_ticket,
    close_ticket,
    send_robotupload,
    add_note_entry,
    filter_keywords,
    prepare_keywords,
    user_pdf_get,
)

from six import StringIO
from mock import MagicMock
import mock, pytest


class MockObj(object):
    class MockLog(object):
        def __init__(self):
            self._log = StringIO()

        def info(self, *args, **kwargs):
            self._log.write(args[0])

        def error(self, *args, **kwargs):
            self.info(args[0])

        def debug(self, message, format=None):
            self.info(message)

    log = MockLog()

    def __init__(self, id_, data, extra_data):
        self.id = id_
        self.id_user = id_
        self.data = data
        self.extra_data = extra_data


def mock_context_function(user, obj):
    return {}


@mock.patch('inspirehep.modules.workflows.tasks.submission.get_instance')
@mock.patch('inspirehep.modules.workflows.tasks.submission.in_production_mode')
def test_submit_rt_ticket(mock_production_mode, mock_rt_instance):
    mock_file = MagicMock()
    mock_file.create_ticket = MagicMock(return_value=1)
    mock_rt_instance.return_value = mock_file
    mock_production_mode.return_value = True

    obj = MockObj(1, {}, {'recid': 1})

    assert submit_rt_ticket(obj, '', None, '', 'mail@ma.il', 'ticket_id')
    assert obj.extra_data['ticket_id'] == 1

    mock_file.create_ticket.assert_called_with(
        CF_RecordID=1,
        Queue='',
        Subject=None,
        Text='',
        requestors='mail@ma.il'
    )


@mock.patch('inspirehep.modules.workflows.tasks.submission.submit_rt_ticket')
@mock.patch('inspirehep.modules.workflows.tasks.submission.render_template')
@mock.patch('inspirehep.modules.workflows.tasks.submission.User')
def test_create_ticket(mock_user_query, mock_render_template, mock_submit_rt_ticket):
    template = 'literaturesuggest/tickets/curator_submitted.html'
    ticket_id_key = 'ticket_id'
    queue = 'HEP_add_user'
    create_ticket_function = create_ticket(
        template=template,
        queue=queue,
        context_factory=mock_context_function,
        ticket_id_key=ticket_id_key
    )

    mock_user = MagicMock()
    mock_user.email.return_value = ''
    mock_user_query.query.get.return_value = mock_user
    mock_render_template.return_value = ''

    obj = MockObj(1, {}, {})
    create_ticket_function(obj, {})

    mock_render_template.assert_called_with(template)
    mock_submit_rt_ticket.assert_called_with(obj, queue, None, '',
                                             mock_user.email, ticket_id_key)


@pytest.mark.parametrize('mock_template', [None, MagicMock()])
@mock.patch('inspirehep.utils.tickets.get_instance')
@mock.patch('inspirehep.modules.workflows.tasks.submission.User')
@mock.patch('inspirehep.modules.workflows.tasks.submission.render_template')
def test_reply_ticket_with_template(mock_render_template, mock_user_query, mock_get_instance, mock_template):
    mock_rt = MagicMock()
    mock_get_instance.return_value = mock_rt
    mock_template = mock_template
    mock_render_template.return_value = 'Reason\ndescription'
    mock_user_query.query.get.return_value = MagicMock()

    reply_ticket_function = reply_ticket(
        template=mock_template,
        context_factory=mock_context_function,
        keep_new=True
    )

    obj = MockObj(1, {}, {'ticket_id': 1, 'reason': 'Reason\ndescription '})
    reply_ticket_function(obj, {})

    mock_rt.edit_ticket.assert_called_with(ticket_id=1, Status='new')
    mock_rt.reply.assert_called_with(ticket_id=1, text='Reason\n description')


@mock.patch('inspirehep.utils.tickets.get_instance')
def test_close_ticket(mock_get_instance):
    mock_rt = MagicMock()
    mock_get_instance.return_value = mock_rt
    close_ticket_function = close_ticket(ticket_id_key='ticket_id')

    obj = MockObj(1, {}, {'ticket_id': 1})
    close_ticket_function(obj, {})

    mock_rt.edit_ticket.assert_called_with(ticket_id=1, Status='resolved')


@pytest.mark.parametrize('extra_data_key', [None, 'something'])
@mock.patch('inspirehep.modules.workflows.tasks.submission.in_production_mode')
@mock.patch('inspirehep.utils.robotupload.make_robotupload_marcxml')
@mock.patch('inspirehep.dojson.utils.legacy_export_as_marc')
def test_send_robotupload(mock_legacy_export_as_marc,
                          mock_make_robotupload_marcxml,
                          mock_production_mode,
                          extra_data_key):
    marc_xml = '<marc_xml=data>'
    eng = MagicMock()
    mock_result = MagicMock()
    marcxml_processor = MagicMock()
    obj = MockObj(1, {}, {'ticket_id': 1})

    mock_result.text = '[INFO]'
    mock_production_mode.return_value = True
    mock_legacy_export_as_marc.return_value = marc_xml
    mock_make_robotupload_marcxml.return_value = mock_result
    marcxml_processor.do.return_value = {'marc_json': 'data'}

    send_robotupload_function = send_robotupload(
        url=None,
        marcxml_processor=marcxml_processor,
        callback_url='callback/workflows/continue',
        mode='insert',
        extra_data_key=extra_data_key
    )
    send_robotupload_function(obj, eng)

    mock_make_robotupload_marcxml.assert_called_with(
        url=None,
        marcxml=marc_xml,
        callback_url='https://localhost:5000/callback/workflows/continue',
        mode='insert',
        nonce=1,
        priority=5,
    )


def test_add_note_entry_temporary_type():
    obj = MockObj(1, {'public_notes': []}, {'core': True})

    add_note_entry(obj, {})

    assert obj.data['public_notes'] == [{'value': '*Temporary entry*'}]


def test_add_note_entry_brief_type():
    obj = MockObj(1, {'public_notes': []}, {'core': False})

    add_note_entry(obj, {})

    assert obj.data['public_notes'] == [{'value': '*Brief entry*'}]


def test_add_note_entry_doubled():
    obj = MockObj(1, {'public_notes': [{'value': '*Brief entry*'}]}, {'core': False})

    add_note_entry(obj, {})

    assert obj.data['public_notes'] == [{'value': '*Brief entry*'}]


def test_add_note_entry_multiple():
    obj = MockObj(1, {'public_notes': [{'value': '*Something for test*'}]}, {'core': True})

    add_note_entry(obj, {})

    assert obj.data['public_notes'] == [{'value': '*Something for test*'},
                                        {'value': '*Temporary entry*'}]


def test_add_note_entry_empty_notes():
    obj = MockObj(1, {'public_notes': None}, {'core': True})

    add_note_entry(obj, {})

    assert obj.data['public_notes'] == [{'value': '*Temporary entry*'}]


def test_filter_keywords():
    obj = MockObj(
        1,
        {},
        {
            'keywords_prediction': {
                'keywords': [
                    {'accept': True, 'keyword': 'Physics'},
                    {'accept': False, 'keyword': 'Biology'}
                ]
            }
        }
    )
    filter_keywords(obj, {})

    assert obj.extra_data == {'keywords_prediction': {'keywords': [{'accept': True, 'keyword': 'Physics'}]}}


def test_prepare_keywords():
    obj = MockObj(
        1,
        {},
        {
            'keywords_prediction': {
                'keywords': [
                    {
                        'accept': True,
                        'keyword': 'Physics',
                        'label': 'Physics_mock_label',
                        'curated': True
                    }
                ]
            }
        }
    )
    prepare_keywords(obj, {})
    assert obj.data == {
        'keywords': [
            {
                'keyword': 'Physics_mock_label',
                'classification_scheme': '',
                'source': 'curator',
            },
        ]
    }


def test_prepare_keywords_magpie():
    obj = MockObj(
        1,
        {},
        {
            'keywords_prediction': {
                'keywords': [
                    {
                        'accept': True,
                        'keyword': 'Physics',
                        'label': 'Physics_mock_label',
                        'curated': False,
                    },
                ]
            }
        }
    )
    prepare_keywords(obj, {})

    assert obj.data == {
        'keywords': [
            {
                'keyword': 'Physics_mock_label',
                'classification_scheme': '',
                'source': 'magpie',
            },
        ]
    }


def test_user_pdf_get_with_file():
    obj = MockObj(
        1,
        {'fft': [{'url': 'pdf_file_0', 'docfile_type': 'INSPIRE-PUBLIC'}]},
        {
            'pdf_upload': True,
            'submission_data': {
                'pdf': 'pdf_file_1'
            }
        }
    )
    user_pdf_get(obj, {})

    assert obj.data == {
        'fft': [
            {'url': 'pdf_file_0', 'docfile_type': 'INSPIRE-PUBLIC'},
            {'url': 'pdf_file_1', 'docfile_type': 'INSPIRE-PUBLIC'}
        ]
    }


def test_user_pdf_get():
    obj = MockObj(
        1,
        {},
        {
            'pdf_upload': True,
            'submission_data': {
                'pdf': 'pdf_file_0'
            }
        }
    )
    user_pdf_get(obj, {})

    assert obj.data == {
        'fft': [
            {'url': 'pdf_file_0', 'docfile_type': 'INSPIRE-PUBLIC'}
        ]
    }
