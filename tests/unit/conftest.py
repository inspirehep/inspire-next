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

import os
import sys

import pytest

from inspirehep.factory import create_app

# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture(autouse=True, scope='session')
def app():
    """Flask application.

    Creates a Flask application with a simple testing configuration,
    then creates an application context and yields, so that all tests
    have access to one.

    See: http://flask.pocoo.org/docs/0.12/appcontext/.
    """
    app = create_app(
        DEBUG=False,
        # Tests may fail when turned on because of Flask bug (A setup function was called after the first request was handled. when initializing - when Alembic initialization)
        WTF_CSRF_ENABLED=False,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_TASK_EAGER_PROPAGATES=True,
        TESTING=True,
        PRODUCTION_MODE=True,
        WORKFLOWS_MAX_AUTHORS_COUNT_FOR_GROBID_EXTRACTION=50,
    )

    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def app_client(app):
    """Flask test client for the application.

    See: http://flask.pocoo.org/docs/0.12/testing/#keeping-the-context-around.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def api(app):
    """Flask API application."""
    yield app.wsgi_app.mounts['/api']


@pytest.fixture(scope='function')
def api_client(api):
    """Flask test client for the API application."""
    with api.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def request_context(app):
    """Flask request context.

    See: http://flask.pocoo.org/docs/0.12/reqcontext/.
    """
    with app.test_request_context() as request_context:
        yield request_context


@pytest.fixture
def vcr_config():
    return {
        'decode_compressed_response': True,
        'filter_headers': ('Authorization', 'User-Agent'),
        'ignore_hosts': (
            'localhost',
            'test-indexer',
            'test-redis',
            'test-database',
            'test-rabbitmq',
            'test-worker',
            'test-web',
        ),
    }


@pytest.fixture
def vcr(vcr):
    vcr.register_matcher(
        'accept',
        lambda r1, r2: r1.headers.get('Accept') == r2.headers.get('Accept'),
    )
    vcr.match_on = ['method', 'scheme', 'host', 'port', 'path', 'query', 'accept']
    return vcr
