# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from click.testing import CliRunner
from functools import partial
from flask.cli import ScriptInfo
from flask_alembic import Alembic

from invenio_db import db
from invenio_db.utils import drop_alembic_version_table
from invenio_search import current_search_client as es

from inspirehep.factory import create_app
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions

# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../integration/helpers'))


from factories.db.invenio_records import TestRecordMetadata  # noqa


@pytest.fixture(scope='session')
def app():
    """
    Flask application without demosite data and without database isolation:
    any db transaction performed during the tests are persisted into the db,
    as well as any operation to Elasticsearch.
    Isolation is provided by `empty_environment`, which runs before every tests
    and initializes DB and ES.
    The Flask app is configured in such a way to use Celery and RabbitMQ in the
    test environment, to achieve async tasks testability.
    """
    app = create_app()
    config = dict(
        DEBUG=True,
        CELERY_BROKER_URL='pyamqp://guest:guest@test-rabbitmq:5672',
        CELERY_RESULT_BACKEND='redis://test-redis:6379/1',
        CELERY_CACHE_BACKEND='redis://test-redis:6379/1',
        TESTING=True,
    )
    app.config.update(config)

    with app.app_context():
        yield app


@pytest.fixture(scope='function', autouse=True)
def clear_environment(app):
    with app.app_context():
        db.session.close()
        db.drop_all()
        drop_alembic_version_table()

        alembic = Alembic(app=app)
        alembic.upgrade()
        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))
        es.indices.refresh('records-hep')

        init_all_storage_paths()
        init_users_and_permissions()


@pytest.fixture
def create_records(app):

    def _records_factory(n=1, additional_props={}, pid_type='lit'):
        records = []
        for i in range(n):
            rec = TestRecordMetadata.create_from_kwargs(
                json=additional_props,
                pid_type=pid_type
            ).record_metadata
            records.append(rec)

        db.session.commit()
        return records

    return _records_factory


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'pyamqp://guest:guest@test-rabbitmq:5672',
        'result_backend': 'redis://test-redis:6379/1'
    }


@pytest.fixture(scope='session')
def celery_app_with_context(app, celery_session_app):
    """
    This fixtures monkey-patches the Task class in the celery_session_app to
    properly run tasks in a Flask application context.
    Note:
        Using `celery_app` and `celery_worker` in the tests will work only
        for the first test, from the second one the worker hangs.
        See: https://github.com/celery/celery/issues/5105
    """
    from flask_celeryext.app import AppContextTask
    celery_session_app.Task = AppContextTask
    celery_session_app.flask_app = app
    return celery_session_app


@pytest.fixture(scope='class')
def app_cli(app):
    """Click CLI runner inside the Flask application."""
    runner = CliRunner()
    obj = ScriptInfo(create_app=lambda info: app)
    runner._invoke = runner.invoke
    runner.invoke = partial(runner.invoke, obj=obj)
    return runner
