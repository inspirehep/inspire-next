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
        self.id = id_
        self.data = data
        self.extra_data = extra_data


def test_add_note_entry_does_not_add_value_that_is_already_present():
    class MockObj(object):
        def __init__(self, data, extra_data):
            self.data = data
            self.extra_data = extra_data

    obj = MockObj({'public_notes': [{'value': '*Temporary entry*'}]}, {'core': 'something'})
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

