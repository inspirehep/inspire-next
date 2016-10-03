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

from __future__ import absolute_import, division, print_function

from flask import current_app, session
from flask_security import current_user
from werkzeug.local import LocalProxy

from invenio_access.models import ActionUsers
from invenio_access.permissions import (DynamicPermission,
                                        ParameterizedActionNeed)

from inspirehep.modules.cache import current_cache


action_view_restricted_collection = ParameterizedActionNeed(
    'view-restricted-collection', argument=None
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


class RecordPermission(object):
    """Record permission.

    - Read access given if collection not restricted.
    - All other actions are denied for the moment.
    """

    read_actions = ['read']

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
        else:
            return cls(record, deny, user)


def has_read_permission(user, record):
    """Check if user has read access to the record."""
    user_roles = [r.name for r in current_user.roles]
    if 'superuser' in user_roles:
        return True

    if '_collections' in record:
        record_collections = set(record['_collections'])
        restricted_coll = all_restricted_collections & record_collections
        if restricted_coll:
            for collection in restricted_coll:
                if not DynamicPermission(
                        ParameterizedActionNeed(
                            "view-restricted-collection",
                            collection)
                ).can():
                    return False

    # By default we allow access
    return True


#
# Utility functions
#

def deny(user, record):
    """Deny access."""
    return False
