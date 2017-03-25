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

import sys
import os

import pytest

from functools import partial

from click.testing import CliRunner
from flask import current_app
from flask.cli import ScriptInfo

from invenio_db import db
from invenio_search import current_search_client as es

from inspirehep.factory import create_app
from inspirehep.modules.fixtures.collections import init_collections
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions


# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture(scope='session')
def app():
    """Flask application.

    Creates a Flask application with a simple testing configuration,
    then creates an application context and inside of it recreates
    all databases and indices from the fixtures. Finally it yields,
    so that all tests that explicitly use the ``app`` fixture have
    access to an application context.

    See: http://flask.pocoo.org/docs/0.12/appcontext/.
    """
    app = create_app(
        DEBUG=True,
        WTF_CSRF_ENABLED=False,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_TASK_EAGER_PROPAGATES=True,
        SECRET_KEY='secret!',
        RECORD_EDITOR_FILE_UPLOAD_FOLDER='tests/integration/editor/temp',
        TESTING=True,
    )

    with app.app_context():
        # Celery task imports must be local, otherwise their
        # configuration would use the default pickle serializer.
        from inspirehep.modules.migrator.tasks import add_citation_counts, migrate_from_file

        db.drop_all()
        db.create_all()

        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()
        init_collections()

        migrate_from_file('./inspirehep/demosite/data/demo-records.xml.gz', wait_for_results=True)
        es.indices.refresh('records-hep')  # Makes sure that all HEP records were migrated.

        add_citation_counts()
        es.indices.refresh('records-hep')  # Makes sure that all citation counts were added.

        yield app


@pytest.fixture(scope='function')
def isolated_app(app):
    """Flask application with database isolation and function scope.

    When using this fixture no changes will be persisted to the database
    because at the end of each test the database is rolled back. This is
    achieved by using a nested transaction. For examples on how to use it,
    please see tests/integration/test_db_isolation.py.

    Note:
        A neater solution seems to be the one suggested in https://goo.gl/31EKXq.

    """
    with db.session.begin_nested():
        yield app
    db.session.rollback()


@pytest.fixture()
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


@pytest.fixture()
def api_client(api):
    """Flask test client for the API application."""
    with api.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def app_cli_runner(app):
    """Click CLI runner inside the Flask application."""
    runner = CliRunner()
    obj = ScriptInfo(create_app=lambda info: current_app)
    runner._invoke = runner.invoke
    runner.invoke = partial(runner.invoke, obj=obj)
    return runner
