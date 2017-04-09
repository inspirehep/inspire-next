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
    def halt(self, action, msg):
        self.action = action
        self.msg = msg


class MockObj(object):
    def __init__(self, data, extra_data, files=None, id=1, id_user=1):
        self.data = data
        self.extra_data = extra_data

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

    @property
    def keys(self):
        return self.data.keys()


class MockLog(object):
    def __init__(self):
        self._debug = StringIO()
        self._error = StringIO()
        self._info = StringIO()

    def debug(self, message):
        self._debug.write(message)

    def error(self, message):
        self._error.write(message)

    def info(self, message):
        self._info.write(message)


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
