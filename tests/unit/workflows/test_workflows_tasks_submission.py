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
    add_note_entry,
    create_ticket,
)

from six import StringIO
from mock import MagicMock
import mock


class MockObj(object):
    class MockLog(object):
        def __init__(self):
            self._log = StringIO()

        def info(self, *args, **kwargs):
            self._log.write(args[0])

        def error(self, *args, **kwargs):
            self.info(args[0])

    log = MockLog()

    def __init__(self, id_, data, extra_data):
        self.id_user = id_
        self.data = data
        self.extra_data = extra_data


def test_add_note_entry_does_not_add_value_that_is_already_present():
    obj = MockObj(1, {'public_notes': [{'value': '*Temporary entry*'}]}, {'core': 'something'})
    eng = {}

    assert add_note_entry(obj, eng) is None
    assert {'public_notes': [{'value': '*Temporary entry*'}]} == obj.data


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
    def mock_context_function(user, obj):
        return {}

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
