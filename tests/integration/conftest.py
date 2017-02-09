# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from time import sleep

import pytest

from invenio_db import db
from invenio_search import current_search_client as es
from invenio_accounts.models import User
from invenio_oauthclient.models import RemoteAccount, RemoteToken, UserIdentity

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
        TESTING=True,
    )

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks.records import add_citation_counts, migrate
        from inspirehep.modules.fixtures.collections import init_collections
        from inspirehep.modules.fixtures.files import init_all_storage_paths
        from inspirehep.modules.fixtures.users import init_users_and_permissions

        db.drop_all()
        db.create_all()

        sleep(10)  # Makes sure that ES is up.
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
    """Flask application fixture."""
    app = create_app()
    app.config.update({'DEBUG': True})

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks.records import migrate
        from inspirehep.modules.fixtures.collections import init_collections
        from inspirehep.modules.fixtures.files import init_all_storage_paths
        from inspirehep.modules.fixtures.users import init_users_and_permissions

        db.drop_all()
        db.create_all()

        sleep(10)
        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records-small.xml', wait_for_results=True)
        es.indices.refresh('records-hep')

        yield app


@pytest.yield_fixture()
def app_client(app):
    """Flask test client for APP app."""
    with app.test_client() as client:
        yield client


@pytest.yield_fixture(scope='session')
def api(app):
    """Flask application fixture."""
    yield app.wsgi_app.mounts['/api']


@pytest.yield_fixture()
def api_client(api):
    """Flask test client for API app."""
    with api.test_client() as client:
        yield client


class OrcidApiMock(object):

    def __init__(self, put_code):
        self.put_code = put_code

    def add_record(self, author_orcid, token, category, orcid_json):
        return self.put_code

    def update_record(self, author_orcid, token, category, orcid_json, put_code):
        pass

    def remove_record(self, author_orcid, token, category, put_code):
        pass


@pytest.fixture(scope='module')
def mock_user(app, request):
    user = User(
        email='test_orcid_user@inspirehep.net',
    )
    db.session.add(user)
    db.session.commit()

    token = RemoteToken(
        id_remote_account=1,
        access_token='123'
    )
    user_identity = UserIdentity(
        id='0000-0001-9412-8627',
        id_user=str(user.id),
        method='orcid'
    )
    remote_account = RemoteAccount(
        id=1,
        user_id=user.id,
        extra_data={},
        client_id=1,
        user=user
    )

    db.session.add(user_identity)
    db.session.add(remote_account)
    db.session.add(token)
    db.session.commit()

    yield user

    remote_account = RemoteAccount.query.filter_by(user_id=user.id).first()
    db.session.delete(token)
    db.session.delete(user_identity)
    db.session.delete(remote_account)
    db.session.delete(user)
    db.session.commit()
