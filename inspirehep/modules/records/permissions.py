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

from flask import current_app, session
from flask_principal import ActionNeed
from flask_security import current_user
from werkzeug.local import LocalProxy

from invenio_access.models import ActionUsers, ActionRoles
from invenio_access.permissions import (
    Permission,
    ParameterizedActionNeed,
)
from invenio_cache import current_cache


action_view_restricted_collection = ParameterizedActionNeed(
    'view-restricted-collection', argument=None
)
action_update_collection = ParameterizedActionNeed(
    'update-collection', argument=None
)

all_restricted_collections = LocalProxy(lambda: load_restricted_collections())

user_collections = LocalProxy(lambda: get_user_collections())


def get_user_collections():
    """Get user restricted collections."""
    return session.get('restricted_collections', set())


def load_user_collections(app, user):
    """Load user restricted collections upon login.

    Receiver for flask_login.user_logged_in
    """
    user_collections = set(
        [a.argument for a in ActionUsers.query.filter_by(
            action='view-restricted-collection',
            user_id=current_user.get_id()).all()]
    )
    user_roles = user.roles
    for role in user_roles:
        user_collections = user_collections | set(
            [a.argument for a in ActionRoles.query.filter_by(
                action='view-restricted-collection',
                role_id=role.id).all()]
        )
    session['restricted_collections'] = user_collections


def load_restricted_collections():
    restricted_collections = current_cache.get('restricted_collections')
    if restricted_collections:
        return restricted_collections
    else:
        restricted_collections = set(
            [
                a.argument for a in ActionUsers.query.filter_by(
                    action='view-restricted-collection').all()
            ]
        )
        restricted_collections = restricted_collections | set(
            [
                a.argument for a in ActionRoles.query.filter_by(
                    action='view-restricted-collection').all()
            ]
        )
        if restricted_collections:
            current_cache.set(
                'restricted_collections',
                restricted_collections,
                timeout=current_app.config.get(
                    'INSPIRE_COLLECTIONS_RESTRICTED_CACHE_TIMEOUT', 120)
            )
        return restricted_collections


def record_read_permission_factory(record=None):
    """Record permission factory."""
    return RecordPermission.create(record=record, action='read')


def record_update_permission_factory(record=None):
    """Record permission factory."""
    return RecordPermission.create(record=record, action='update')


class RecordPermission(object):
    """Record permission.

    - Read access given if collection not restricted.
    - Update access given to admins and cataloguers.
    - All other actions are denied for the moment.
    """

    read_actions = ['read']
    update_actions = ['update']

    def __init__(self, record, func, user):
        """Initialize a file permission object."""
        self.record = record
        self.func = func
        self.user = user or current_user

    def can(self):
        """Determine access."""
        return self.func(self.user, self.record)

    @classmethod
    def create(cls, record, action, user=None):
        """Create a record permission."""
        if action in cls.read_actions:
            return cls(record, has_read_permission, user)
        elif action in cls.update_actions:
            return cls(record, has_update_permission, user)
        else:
            return cls(record, deny, user)


def has_read_permission(user, record):
    """Check if user has read access to the record."""
    def _cant_view(collection):
        return not Permission(
            ParameterizedActionNeed(
                'view-restricted-collection',
                collection)).can()

    user_roles = [r.name for r in current_user.roles]
    if 'superuser' in user_roles:
        return True

    if '_collections' in record:
        record_collections = set(record['_collections'])
        restricted_coll = all_restricted_collections & record_collections
        if restricted_coll:
            if any(map(_cant_view, restricted_coll)):
                return False

    # By default we allow access
    return True


def has_update_permission(user, record):
    """Check if user has update access to the record."""
    def _cant_update(collection):
        return not Permission(
            ParameterizedActionNeed(
                'update-collection',
                collection)).can()

    user_roles = [r.name for r in current_user.roles]
    if 'superuser' in user_roles:
        return True

    if '_collections' in record:
        record_collections = set(record['_collections'])
        if any(map(_cant_update, record_collections)):
            return False
        return True

    return False


def has_admin_permission(user, record):
    """Check if user has admin access to record."""
    # Allow administrators
    if Permission(ActionNeed('admin-access')):
        return True


#
# Utility functions
#

def deny(user, record):
    """Deny access."""
    return False
