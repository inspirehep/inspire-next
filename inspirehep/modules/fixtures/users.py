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
from invenio_oauth2server.models import Client, Token

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
        ds.create_role(
            name='jlabcurator',
            description='curator for JLAB related articles'
        )
        ds.create_role(
            name='chatbot',
            description='chatbot'
        )
    db.session.commit()


def init_users():
    """Sample users, not to be used in production."""
    ds = current_app.extensions['invenio-accounts'].datastore
    superuser = Role.query.filter_by(name='superuser').one()
    cataloger = Role.query.filter_by(name='cataloger').one()
    hermes_curator = Role.query.filter_by(name='hermescurator').one()
    hermes_collections = Role.query.filter_by(name='hermescoll').one()
    jlab_curator = Role.query.filter_by(name='jlabcurator').one()
    with db.session.begin_nested():
        ds.create_user(
            email='admin@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[superuser],
        )
        ds.create_user(
            email='cataloger@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[cataloger],
        )
        ds.create_user(
            email='hermescataloger@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[hermes_curator, hermes_collections],
        )
        ds.create_user(
            email='jlabcurator@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=[jlab_curator],
        )
        ds.create_user(
            email='johndoe@inspirehep.net',
            password=hash_password("123456"),
            active=True,
        )
        ds.create_user(
            email='chatbot@inspirehep.net',
            password=hash_password("123456"),
            active=True,
            roles=['chatbot']
        )
    db.session.commit()


def init_superuser_permissions():
    superuser = Role.query.filter_by(name='superuser').one()
    db.session.add(ActionRoles(
        action='superuser-access',
        role=superuser,
    ))
    db.session.add(ActionRoles(
        action='admin-access',
        role=superuser,
    ))


def init_cataloger_permissions():
    cataloger = Role.query.filter_by(name='cataloger').one()
    db.session.add(ActionRoles(
        action='workflows-ui-admin-access',
        role=cataloger,
    ))
    db.session.add(ActionRoles(
        action='admin-holdingpen-authors',
        role=cataloger,
    ))
    db.session.add(ActionRoles(
        action='update-collection',
        role=cataloger,
    ))
    db.session.add(ActionRoles(
        action='editor-use-api',
        role=cataloger,
    ))
    db.session.add(ActionRoles(
        action='migrator-use-api',
        role=cataloger,
    ))


def init_hermes_permissions():
    hermes_collections = Role.query.filter_by(name='hermescoll').one()
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='HERMES Internal Notes',
        role=hermes_collections,
    ))

    hermes_curator = Role.query.filter_by(name='hermescurator').one()
    db.session.add(ActionRoles(
        action='update-collection',
        argument='HERMES Internal Notes',
        role=hermes_curator,
    ))


def init_jlab_permissions():
    jlab_curator = Role.query.filter_by(name='jlabcurator').one()
    db.session.add(ActionRoles(
        action='workflows-ui-read-access',
        role=jlab_curator,
    ))
    db.session.add(ActionRoles(
        action='update-collection',
        role=jlab_curator,
    ))


def init_permissions():
    init_superuser_permissions()
    init_cataloger_permissions()
    init_hermes_permissions()
    init_jlab_permissions()
    db.session.commit()


def init_users_and_permissions():
    init_roles()
    init_users()
    init_permissions()


def init_authentication_token():
    with db.session.begin_nested():
        client = Client(
            name='admin',
            user_id=1,
            is_internal=True,
            is_confidential=False,
            _default_scopes=""
        )
        client.gen_salt()

        token = Token(
            client_id=client.client_id,
            user_id=1,
            access_token=current_app.config["AUTHENTICATION_TOKEN"],
            expires=None,
            _scopes="",
            is_personal=True,
            is_internal=True,
        )

        db.session.add(client)
        db.session.add(token)
    db.session.commit()
