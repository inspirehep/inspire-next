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
import sqlalchemy

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
    """
    Deprecated: do not use this fixture for new tests, unless for very
    specific use cases. Use `isolated_app` instead.

    Flask application with demosite data and without any database isolation:
    any db transaction performed during the tests are persisted into the db.

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
    """
    Flask application with demosite data and with database isolation: db
    transactions performed during the tests are not persisted into the db,
    because transactions are rolled back on tear down.
    Inspired by: https://goo.gl/31EKXq

    Note: creating an isolated app without the demosite is challenging,
    see: https://its.cern.ch/jira/browse/INSPIR-425

    Note: the order of execution between the `app` fixture (session-scoped)
    and the `isolated_app` fixture should not matter.
    Some work to investigate that was done here:
    https://github.com/turtle321/inspire-next/commit/a3575c4f59890d274e7b5fcdfdaeac9685d0a755
    """
    original_session = db.session
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.begin_nested()

    # Custom attribute to mark the session as isolated.
    db.session._is_isolated = True

    @sqlalchemy.event.listens_for(db.session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested and \
                getattr(db.session, '_is_isolated', False):

            session.expire_all()
            session.begin_nested()

    yield app

    db.session._is_isolated = False
    db.session.close()
    transaction.rollback()
    connection.close()
    db.session = original_session


# TODO: all fixtures using ``app`` must be replaced by ones that use ``isolated_app``.
@pytest.fixture()
def app_client(app):
    """Flask test client for the application.

    See: http://flask.pocoo.org/docs/0.12/testing/#keeping-the-context-around.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture()
def isolated_app_client(isolated_app):
    """Flask test client for the application.

    See: http://flask.pocoo.org/docs/0.12/testing/#keeping-the-context-around.
    """
    with isolated_app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def api(app):
    """Flask API application."""
    yield app.wsgi_app.mounts['/api']


@pytest.fixture(scope='function')
def isolated_api(isolated_app):
    """Flask API application."""
    yield isolated_app.wsgi_app.mounts['/api']


@pytest.fixture()
def api_client(api):
    """Flask test client for the API application."""
    with api.test_client() as client:
        yield client


@pytest.fixture()
def isolated_api_client(isolated_api):
    """Flask test client for the API application."""
    with isolated_api.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def app_cli_runner(app):
    """Click CLI runner inside the Flask application."""
    runner = CliRunner()
    obj = ScriptInfo(create_app=lambda info: current_app)
    runner._invoke = runner.invoke
    runner.invoke = partial(runner.invoke, obj=obj)
    return runner
