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

"""Fixtures for users, roles and actions."""

from __future__ import absolute_import, division, print_function

from flask import current_app
from flask_security.utils import hash_password

from invenio_access.models import ActionRoles
from invenio_accounts.models import Role

from invenio_db import db


def init_roles():
    ds = current_app.extensions['invenio-accounts'].datastore
    with db.session.begin_nested():
        ds.create_role(
            name='superuser',
            description='admin with no restrictions'
        )
        ds.create_role(
            name='cataloger',
            description='users with editing capabilities'
        )
        ds.create_role(
            name='hermescurator',
            description='curator for HERMES Internal Notes'
        )
        ds.create_role(
            name='hermescoll',
            description='HERMES Collaboration access to Internal Notes'
        )
    db.session.commit()


def init_users():
    """Sample users, not to be used in production."""
    ds = current_app.extensions['invenio-accounts'].datastore
    superuser = Role.query.filter_by(name='superuser').one()
    cataloger = Role.query.filter_by(name='cataloger').one()
    hermes_curator = Role.query.filter_by(name='hermescurator').one()
    hermes_collections = Role.query.filter_by(name='hermescoll').one()
    with db.session.begin_nested():
        ds.create_user(
            email='admin@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[superuser]
        )
        ds.create_user(
            email='cataloger@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[cataloger]
        )
        ds.create_user(
            email='hermescataloger@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[hermes_curator, hermes_collections]
        )
        ds.create_user(
            email='johndoe@inspirehep.net',
            password=hash_password("123456"),
            active=True
        )
    db.session.commit()


def init_permissions():
    superuser = Role.query.filter_by(name='superuser').one()
    cataloger = Role.query.filter_by(name='cataloger').one()
    hermes_collections = Role.query.filter_by(name='hermescoll').one()
    hermes_curator = Role.query.filter_by(name='hermescurator').one()
    db.session.add(ActionRoles(
        action='superuser-access',
        role=superuser)
    )
    db.session.add(ActionRoles(
        action='admin-access',
        role=superuser)
    )
    db.session.add(ActionRoles(
        action='workflows-ui-admin-access',
        role=cataloger)
    )
    db.session.add(ActionRoles(
        action='admin-holdingpen-authors',
        role=cataloger)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='HERMES Internal Notes',
        role=hermes_collections)
    )
    db.session.add(ActionRoles(
        action='update-collection',
        role=cataloger)
    )
    db.session.add(ActionRoles(
        action='editor-use-api',
        role=cataloger)
    )
    db.session.add(ActionRoles(
        action='update-collection',
        argument='HERMES Internal Notes',
        role=hermes_curator)
    )
    db.session.commit()


def init_users_and_permissions():
    init_roles()
    init_users()
    init_permissions()
