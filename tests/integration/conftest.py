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
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        SECRET_KEY='secret!',
        RECORD_EDITOR_FILE_UPLOAD_FOLDER='tests/integration/editor/temp',
        TESTING=True,
    )

    with app.app_context():
        # Celery task imports must be local, otherwise their
        # configuration would use the default pickle serializer.
        from inspirehep.modules.migrator.tasks import add_citation_counts, migrate

        db.drop_all()
        db.create_all()

        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records.xml.gz', wait_for_results=True)
        es.indices.refresh('records-hep')  # Makes sure that all HEP records were migrated.

        add_citation_counts()
        es.indices.refresh('records-hep')  # Makes sure that all citation counts were added.

        yield app


@pytest.fixture(scope='module')
def small_app():
    """Flask application with few records and module scope.

    .. deprecated:: 2017-09-18
       Use ``app`` instead.
    """
    app = create_app()
    app.config.update({'DEBUG': True})

    with app.app_context():
        # Celery task imports must be local, otherwise their
        # configuration would use the default pickle serializer.
        from inspirehep.modules.migrator.tasks import migrate

        db.drop_all()
        db.create_all()

        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records-small.xml', wait_for_results=True)
        es.indices.refresh('records-hep')

        yield app


@pytest.fixture()
def alembic_app():
    """Flask application with no records and module scope."""
    app = create_app(
        SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://inspirehep:dbpass123@localhost:5432/inspirehep_alembic'
    )
    app.config.update({
        'DEBUG': True,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


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
