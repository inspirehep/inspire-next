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
from flask_alembic import Alembic

from invenio_db import db
from invenio_db.utils import drop_alembic_version_table
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from invenio_search import current_search
from invenio_workflows import workflow_object_class

from inspirehep.bat.arsenic import Arsenic
from inspirehep.bat.pages import top_navigation_page
from inspirehep.factory import create_app
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions
from inspirehep.modules.workflows.models import (
    WorkflowsAudit,
    WorkflowsPendingRecord,
)


@pytest.fixture(scope='session')
def app(request):
    """Flask application fixtures.

    Creates a Flask application with a simple testing configuration,
    then creates an application context and inside of it recreates
    all databases and indices from the fixtures. Finally it yields,
    so that all tests that explicitly use the ``app`` fixtures have
    access to an application context.

    See: http://flask.pocoo.org/docs/0.12/appcontext/.
    """
    app = create_app()
    # app.config.update({'DEBUG': True})

    with app.app_context():
        # Celery task imports must be local, otherwise their
        # configuration would use the default pickle serializer.
        from inspirehep.modules.migrator.tasks import migrate_from_file
        db.drop_all()
        drop_alembic_version_table()

        alembic = Alembic(app=app)
        alembic.upgrade()

        list(current_search.delete(ignore=[404]))
        list(current_search.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()

        migrate_from_file('./inspirehep/demosite/data/demo-records-acceptance.xml.gz', wait_for_results=True)
        current_search.flush_and_refresh('records-hep')

        yield app


@pytest.fixture
def arsenic(selenium, app):
    """Instantiate the Arsenic singleton.

    The ``Arsenic`` singleton provides some helpers and proxies the rest of
    the calls to the wrapped ``selenium`` fixtures.

    .. deprecated:: 2017-09-18
       This is needlessly complicated.
    """
    Arsenic(selenium)


@pytest.fixture
def login(arsenic):
    """Log in as the admin user."""
    top_navigation_page.log_in('admin@inspirehep.net', '123456')
    yield
    top_navigation_page.log_out()


@pytest.fixture(autouse=True, scope='function')
def cleanup_workflows_tables(app):
    """Delete the contentes of the workflow tables after each test.

    .. deprecated:: 2017-09-18
       Tests that need to clean up should do so explicitly.
    """
    with app.app_context():
        obj_types = (
            WorkflowsAudit.query.all(),
            WorkflowsPendingRecord.query.all(),
            workflow_object_class.query(),
        )
        for obj_type in obj_types:
            for obj in obj_type:
                obj.delete()

        db.session.commit()


@pytest.fixture(autouse=True, scope='function')
def cleanup_literatures(app):
    recs = RecordMetadata.query.filter(RecordMetadata.json['_collections'].op('?')('Literature')).all()
    recs_id = (rec.id for rec in recs)
    buckets = RecordsBuckets.query.filter(RecordsBuckets.record_id.in_(recs_id))
    for bucket in buckets:
        db.session.delete(bucket)
    for lit_record in recs:
        db.session.delete(lit_record)

    db.session.commit()
    current_search.flush_and_refresh('records-hep')
