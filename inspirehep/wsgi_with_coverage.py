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

"""INSPIREHEP WSGI app instantiation with support for coverage.py.

Uses the trick in http://stackoverflow.com/a/20689873/1407497 to instantiate
a WSGI application that reports back information on test coverage.
"""

from __future__ import absolute_import, division, print_function

import atexit

import coverage
from flask import jsonify, request, current_app
from flask_alembic import Alembic
from inspire_crawler.tasks import schedule_crawl
from invenio_search import current_search

from inspire_utils.logging import getStackTraceLogger
from invenio_db import db
from invenio_db.utils import drop_alembic_version_table

from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions

LOGGER = getStackTraceLogger(__name__)

cov = coverage.Coverage()
cov.start()

from .wsgi import application  # noqa


def save_coverage():
    if cov:
        cov.stop()
        cov.save()


atexit.register(save_coverage)

app = getattr(application, 'app', application)


@app.route('/e2e/init_db', methods=['GET'])
def init_db():
    LOGGER.info('Recreating the DB')
    db.session.close()
    db.drop_all()
    drop_alembic_version_table()

    alembic = Alembic(app=current_app)
    alembic.upgrade()

    db.session.commit()
    LOGGER.info('Recreating the DB: done')
    return jsonify("Db recreated")


@app.route('/e2e/init_es', methods=['GET'])
def init_es():
    LOGGER.info('Recreating the ES')
    list(current_search.delete(ignore=[404]))
    list(current_search.create(ignore=[400]))
    LOGGER.info('Recreating the ES: done')
    return jsonify("ES recreated")


@app.route('/e2e/init_fixtures', methods=['GET'])
def init_fixtures():
    LOGGER.info('Initializing fixtures')
    init_all_storage_paths()
    init_users_and_permissions()
    db.session.commit()
    db.session.close()
    LOGGER.info('Initializing fixtures: done')
    return jsonify("Fixtures initialized")


@app.route('/e2e/schedule_crawl', methods=['POST'])
def schedule_crawl_endopint():
    LOGGER.info('Scheduling crawl:\n%s', request.json)
    params = dict(request.json)
    res = schedule_crawl(**params)
    LOGGER.info('Scheduling crawl: done')
    return jsonify(res)
