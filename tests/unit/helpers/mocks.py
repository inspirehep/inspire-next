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

from six import StringIO


class MockEng(object):
    def __init__(self, data_type='hep'):
        self.workflow_definition = AttrDict(data_type=data_type)

    def halt(self, msg='', action=None):
        self.msg = msg
        self.action = action


class MockObj(object):
    def __init__(self, data, extra_data, data_type='hep', files=None, id=1, id_user=1):
        self.data = data
        self.extra_data = extra_data

        self.data_type = data_type
        self.files = files
        self.id = id
        self.id_user = id_user

        self.log = MockLog()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class MockFiles(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def __setitem__(self, key, value):
        self.data[key] = MockFileObject(key=key)

    def __delitem__(self, key):
        del self.data[key]

    @property
    def keys(self):
        return self.data.keys()


class MockFileObject(object):
    def __init__(self, key):
        self.obj = {'key': key}

    def __eq__(self, other):
        return self.obj['key'] == other.obj['key']

    def __getitem__(self, key):
        return self.obj[key]

    def __setitem__(self, key, value):
        self.obj[key] = value

    def delete(self):
        pass

    def get_version(self):
        return MockObjectVersion()


class MockObjectVersion(object):
    @property
    def mimetype(self):
        return 'application/pdf'


class MockLog(object):
    def __init__(self):
        self._debug = StringIO()
        self._error = StringIO()
        self._info = StringIO()
        self._warning = StringIO()

    def debug(self, msg, *args, **kwargs):
        self._debug.write(msg % args if args else msg)

    def error(self, msg, *args, **kwargs):
        self._error.write(msg % args if args else msg)

    def info(self, msg, *args, **kwargs):
        self._info.write(msg % args if args else msg)

    def warning(self, msg, *args, **kwargs):
        self._warning.write(msg % args if args else msg)


class MockRT(object):
    def __init__(self):
        self.last_id = 0
        self.tickets = {}

    def create_ticket(self, **kwargs):
        self.last_id += 1
        kwargs.update({'ticket_id': self.last_id})
        self.tickets[self.last_id] = kwargs
        return self.last_id

    def edit_ticket(self, ticket_id, **kwargs):
        try:
            ticket = self.tickets[ticket_id]
            if ticket['Status'] == 'resolved':
                raise KeyError
        except KeyError:
            raise IndexError

        ticket.update(kwargs)

    def get_ticket(self, ticket_id):
        return self.tickets[ticket_id]

    def reply(self, ticket_id, **kwargs):
        kwargs.update({'Status': 'acknowledged'})
        self.tickets[ticket_id].update(kwargs)


class MockUser(object):
    def __init__(self, email, roles=[]):
        self.email = email
        self.roles = [MockRole(el) for el in roles]

    @property
    def is_anonymous(self):
        return False


class MockRole(object):
    def __init__(self, name):
        self.name = name
