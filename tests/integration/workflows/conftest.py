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
import re
import pytest
import requests_mock
import sys

from invenio_db import db

from inspirehep.factory import create_app
from inspirehep.modules.fixtures.collections import init_collections
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions

# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture
def workflow_app():
    """Flask application with no records and function scope.

    .. deprecated:: 2017-09-18
       Use ``app`` instead.
    """
    app = create_app(
        BEARD_API_URL="http://example.com/beard",
        DEBUG=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        PRODUCTION_MODE=True,
        LEGACY_ROBOTUPLOAD_URL=(
            'http://localhost:1234'
        ),
        MAGPIE_API_URL="http://example.com/magpie",
        WORKFLOWS_MATCH_REMOTE_SERVER_URL="http://legacy_search.endpoint/",
        WORKFLOWS_FILE_LOCATION="/",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        yield app


def drop_all(app):
    db.drop_all()
    _es = app.extensions['invenio-search']
    list(_es.delete(ignore=[404]))


def create_all(app):
    db.create_all()
    _es = app.extensions['invenio-search']
    list(_es.create(ignore=[400]))

    init_all_storage_paths()
    init_users_and_permissions()
    init_collections()


@pytest.fixture(autouse=True)
def cleanup_workflows(workflow_app):
    db.session.close_all()
    drop_all(app=workflow_app)
    create_all(app=workflow_app)


@pytest.fixture
def mocked_external_services(workflow_app):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer|localhost).*'),
            real_http=True,
        )
        requests_mocker.register_uri(
            'POST',
            re.compile(
                'https?://localhost:1234.*',
            ),
            text=u'[INFO]',
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'] +
                '.*'
            ),
            status_code=200,
            json=[],
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['BEARD_API_URL'] +
                '/text/phonetic_blocks.*'
            ),
            status_code=200,
            json={'phonetic_blocks': {}},
        )

        yield
