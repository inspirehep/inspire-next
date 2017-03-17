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

"""Pytest configuration for web tests."""

from __future__ import absolute_import, division, print_function

from time import sleep

import pytest

from invenio_db import db
from invenio_search import current_search_client as es
from invenio_workflows import workflow_object_class

from inspirehep.bat.arsenic import Arsenic
from inspirehep.factory import create_app
from inspirehep.modules.workflows.models import (
    WorkflowsAudit,
    WorkflowsPendingRecord,
)


@pytest.fixture(scope='session')
def app(request):
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

        migrate('./inspirehep/demosite/data/demo-records-acceptance.xml.gz', wait_for_results=True)
        es.indices.refresh('records-hep')

        yield app


@pytest.fixture(autouse=True, scope='function')
def arsenic(selenium, app):
    Arsenic(selenium)


@pytest.fixture(autouse=True, scope='function')
def cleanup_workflows_tables(app):
    with app.app_context():
        WorkflowsAudit.query.delete()
        WorkflowsPendingRecord.query.delete()

        for obj in workflow_object_class.query():
            obj.delete()

        db.session.commit()
