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

import pytest
from langdetect import DetectorFactory

from inspirehep.factory import create_app


@pytest.fixture(autouse=True, scope='session')
def app():
    app = create_app(
        DEBUG=True,
        WTF_CSRF_ENABLED=False,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        TESTING=True,
    )

    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def app_client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def request_context(app):
    with app.test_request_context() as request_context:
        yield request_context


@pytest.fixture(scope='function')
def stable_langdetect(app):
    """Ensure that ``langdetect`` always returns the same thing.

    See: https://github.com/Mimino666/langdetect#basic-usage."""
    DetectorFactory.seed = 0

    yield


@pytest.fixture(scope='function')
def stub_obj_cls():

    yield StubObj


@pytest.fixture(scope='function')
def dummy_eng_cls():

    yield DummyEng


class StubObj(object):
    def __init__(self, data, extra_data, files=None, id=1, id_user=1):
        self.data = data
        self.extra_data = extra_data
        self.files = files
        self.id = id
        self.id_user = id_user

        self.log = MockLog()


class DummyEng(object):
    pass


class MockLog(object):
    def __init__(self):
        self._debug = StringIO()
        self._info = StringIO()

    def debug(self, message):
        self._debug.write(message)

    def info(self, message):
        self._info.write(message)
