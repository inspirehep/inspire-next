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
            name='babarcurator',
            description='curator for BABAR Internal Notes'
        )
        ds.create_role(
            name='babarcoll',
            description='BABAR Collaboration access to Internal Notes'
        )
        ds.create_role(
            name='cdfcurator',
            description='curator for CDF Internal Notes'
        )
        ds.create_role(
            name='cdfcoll',
            description='CDF Collaboration access to Internal Notes'
        )
        ds.create_role(
            name='d0curator',
            description='curator for D0 Internal Notes'
        )
        ds.create_role(
            name='d0coll',
            description='D0 Collaboration access to Internal Notes'
        )
        ds.create_role(
            name='h1curator',
            description='curator for H1 Internal Notes'
        )
        ds.create_role(
            name='h1coll',
            description='H1 Collaboration access to Internal Notes'
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
            name='larsoftcurator',
            description='curator for LARSOFT Internal Notes'
        )
        ds.create_role(
            name='larsoftcoll',
            description='LARSOFT Collaboration access to Internal Notes'
        )
        ds.create_role(
            name='zeuscurator',
            description='curator for ZEUS Internal Notes'
        )
        ds.create_role(
            name='zeuscoll',
            description='ZEUS Collaboration access to Internal Notes'
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
    babar_collections = Role.query.filter_by(name='babarcoll').one()
    cdf_collections = Role.query.filter_by(name='cdfcoll').one()
    d0_collections = Role.query.filter_by(name='d0coll').one()
    h1_collections = Role.query.filter_by(name='h1coll').one()
    hermes_collections = Role.query.filter_by(name='hermescoll').one()
    larsoft_collections = Role.query.filter_by(name='larsoftcoll').one()
    zeus_collections = Role.query.filter_by(name='zeuscoll').one()
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
        argument='BABAR Internal Notes',
        role=babar_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='BABAR Analysis Documents',
        role=babar_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='HEP Hidden',
        role=cataloger)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='CDF Internal Notes',
        role=cdf_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='D0 Internal Notes',
        role=d0_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='H1 Internal Notes',
        role=h1_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='H1 Preliminary Notes',
        role=h1_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='HERMES Internal Notes',
        role=hermes_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='LArSoft Internal Notes',
        role=larsoft_collections)
    )
    db.session.add(ActionRoles(
        action='view-restricted-collection',
        argument='ZEUS Internal Notes',
        role=zeus_collections)
    )
    db.session.commit()


def init_all_users():
    init_roles()
    init_users()
    init_permissions()
