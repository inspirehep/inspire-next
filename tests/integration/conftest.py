# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Pytest configuration for integration tests."""

from time import sleep

import pytest

from invenio_db import db
from invenio_search import current_search_client as es

from inspirehep.factory import create_app


@pytest.yield_fixture(scope='session')
def app(request):
    """Flask application fixture."""
    app = create_app()

    def teardown():
        with app.app_context():
            db.drop_all()

            sleep(10)  # Makes sure that ES is up.
            _es = app.extensions['invenio-search']
            list(_es.delete(ignore=[404]))

    request.addfinalizer(teardown)

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks import add_citation_counts, migrate
        from inspirehep.modules.fixtures.files import init_all_storage_paths

        db.drop_all()
        db.create_all()
        init_all_storage_paths()

        sleep(10)  # Makes sure that ES is up.
        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        migrate('./inspirehep/demosite/data/demo-records.xml.gz', wait_for_results=True)
        es.indices.refresh('records-hep')  # Makes sure that all HEP records were migrated.

        add_citation_counts(request_timeout=80)
        es.indices.refresh('records-hep')  # Makes sure that all citation counts were added.

        yield app
