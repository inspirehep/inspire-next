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
from sqlalchemy import inspect

from invenio_db.utils import drop_alembic_version_table
from invenio_db import db


def test_alembic_revision_fddb3cfe7a9c(alembic_app):
    ext = alembic_app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    db.drop_all()
    drop_alembic_version_table()

    inspector = inspect(db.engine)
    assert 'inspire_prod_records' not in inspector.get_table_names()
    assert 'workflows_audit_logging' not in inspector.get_table_names()
    assert 'workflows_pending_record' not in inspector.get_table_names()

    ext.alembic.upgrade(target='fddb3cfe7a9c')
    inspector = inspect(db.engine)
    assert 'inspire_prod_records' in inspector.get_table_names()
    assert 'workflows_audit_logging' in inspector.get_table_names()
    assert 'workflows_pending_record' in inspector.get_table_names()

    ext.alembic.downgrade(target='a82a46d12408')
    inspector = inspect(db.engine)
    assert 'inspire_prod_records' not in inspector.get_table_names()
    assert 'workflows_audit_logging' not in inspector.get_table_names()
    assert 'workflows_pending_record' not in inspector.get_table_names()

    drop_alembic_version_table()


def test_alembic_revision_cb9f81e8251c(alembic_app):
    def get_indexes(tablename):
        index_names = db.session.execute("select indexname from pg_indexes where tablename='{}'".format(tablename)).fetchall()
        return [index[0] for index in index_names]

    ext = alembic_app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    ext.alembic.stamp()

    ext.alembic.downgrade(target='fddb3cfe7a9c')

    index_names = get_indexes('records_metadata')
    assert 'idxgindoctype' not in index_names
    assert 'idxgintitles' not in index_names
    assert 'idxginjournaltitle' not in index_names
    assert 'idxgincollections' not in index_names

    ext.alembic.upgrade(target='cb9f81e8251c')

    index_names = get_indexes('records_metadata')
    assert 'idxgindoctype' in index_names
    assert 'idxgintitles' in index_names
    assert 'idxginjournaltitle' in index_names
    assert 'idxgincollections' in index_names

    drop_alembic_version_table()


def test_alembic_revision_cb5153afd839(alembic_app):
    ext = alembic_app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    db.drop_all()
    drop_alembic_version_table()

    inspector = inspect(db.engine)
    assert 'workflows_record_sources' not in inspector.get_table_names()

    ext.alembic.upgrade(target='cb5153afd839')
    inspector = inspect(db.engine)
    assert 'workflows_record_sources' in inspector.get_table_names()

    ext.alembic.downgrade(target='fddb3cfe7a9c')
    inspector = inspect(db.engine)
    assert 'workflows_record_sources' not in inspector.get_table_names()

    drop_alembic_version_table()
