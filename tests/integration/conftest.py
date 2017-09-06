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

import pytest

from invenio_db import db
from invenio_search import current_search_client as es

from inspirehep.factory import create_app


@pytest.fixture(scope='session')
def app():
    """Flask application fixture."""
    app = create_app(
        DEBUG=True,
        WTF_CSRF_ENABLED=False,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        SECRET_KEY='secret!',
        TESTING=True,
    )

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks import add_citation_counts, migrate
        from inspirehep.modules.fixtures.collections import init_collections
        from inspirehep.modules.fixtures.files import init_all_storage_paths
        from inspirehep.modules.fixtures.users import init_all_users

        db.drop_all()
        db.create_all()

        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_all_users()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records.xml.gz', wait_for_results=True)
        es.indices.refresh('records-hep')  # Makes sure that all HEP records were migrated.

        add_citation_counts()
        es.indices.refresh('records-hep')  # Makes sure that all citation counts were added.

        yield app


@pytest.fixture(scope='module')
def small_app():
    """Flask application fixture."""
    app = create_app()
    app.config.update({'DEBUG': True})

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks import migrate
        from inspirehep.modules.fixtures.collections import init_collections
        from inspirehep.modules.fixtures.files import init_all_storage_paths
        from inspirehep.modules.fixtures.users import init_all_users

        db.drop_all()
        db.create_all()

        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_all_users()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records-small.xml', wait_for_results=True)
        es.indices.refresh('records-hep')

        yield app


@pytest.fixture()
def app_client(app):
    """Flask test client for APP app."""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def api(app):
    """Flask application fixture."""
    yield app.wsgi_app.mounts['/api']


@pytest.fixture()
def api_client(api):
    """Flask test client for API app."""
    with api.test_client() as client:
        yield client
