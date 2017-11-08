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

from invenio_db import db
from invenio_workflows import workflow_object_class

from inspirehep.factory import create_app
from inspirehep.modules.workflows.models import (
    WorkflowsAudit,
    WorkflowsPendingRecord,
)


# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture(autouse=True)
def cleanup_workflows_tables(small_app):
    """Delete the contents of the workflow tables after each test.

    .. deprecated:: 2017-09-18
       Tests that need to clean up should do so explicitly.
    """
    with small_app.app_context():
        obj_types = (
            WorkflowsAudit.query.all(),
            WorkflowsPendingRecord.query.all(),
            workflow_object_class.query(),
        )
        for obj_type in obj_types:
            for obj in obj_type:
                obj.delete()

        db.session.commit()

        _es = small_app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[404]))


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
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        yield app
