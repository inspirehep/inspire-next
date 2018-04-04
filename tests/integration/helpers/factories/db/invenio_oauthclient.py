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

from invenio_db import db
from invenio_oauthclient.models import (
    UserIdentity,
    RemoteAccount,
    RemoteToken,
)

from .base import TestBaseModel, generate_random_string
from .invenio_accounts import TestUser


class TestUserIdentity(TestBaseModel):
    """
    Create UserIdentity instances.

    Example:
        >>> from factories.db.invenio_oauthclient import TestUserIdentity
        >>> factory = TestUserIdentity.create_from_kwargs(id='myorcid')
        >>> factory.user_identity
        <UserIdentity (transient 4661300240)>
        >>> factory.user_identity.id
        'myorcid'
        >>> factory.user
        <User 41>
    """
    model_class = UserIdentity

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()

        # Check all required fields.
        updated_kwargs = kwargs.copy()
        if not kwargs.pop('id', None):
            updated_kwargs['id'] = generate_random_string(255)
        if not kwargs.pop('method', None):
            updated_kwargs['method'] = generate_random_string(255)
        if not kwargs.pop('id_user', None):
            # Create a User.
            instance.user = TestUser.create_from_kwargs(**kwargs).user
            db.session.flush()
            updated_kwargs['id_user'] = instance.user.id

        instance.user_identity = super(TestUserIdentity, cls)\
            .create_from_kwargs(updated_kwargs)
        return instance

    @classmethod
    def create_for_user(cls, user):
        return cls.create_from_kwargs(id_user=user.id)

    @classmethod
    def create_for_orcid(cls, orcid):
        return cls.create_from_kwargs(id=orcid)


class TestRemoteAccount(TestBaseModel):
    """
    Create RemoteAccount instances.

    Example:
        >>> from factories.db.invenio_oauthclient import TestRemoteAccount
        >>> factory = TestRemoteAccount.create_from_kwargs(client_id='myclientid')
        >>> factory.remote_account
        Remote Account <id=9, user_id=42>
        >>> factory.remote_account.client_id
        'myclientid'
        >>> factory.user
        <User 41>
    """
    model_class = RemoteAccount

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()

        # Check all required fields.
        updated_kwargs = kwargs.copy()
        if not kwargs.pop('client_id', None):
            updated_kwargs['client_id'] = generate_random_string(255)
        if not kwargs.pop('user_id', None):
            # Create a User.
            instance.user = TestUser.create_from_kwargs(**kwargs).user
            db.session.flush()
            updated_kwargs['user_id'] = instance.user.id

        instance.remote_account = super(TestRemoteAccount, cls)\
            .create_from_kwargs(updated_kwargs)
        return instance

    @classmethod
    def create_for_user(cls, user, **kwargs):
        return cls.create_from_kwargs(user_id=user.id, **kwargs)


class TestRemoteToken(TestBaseModel):
    """
    Create RemoteToken instances.

    Example:
        >>> from factories.db.invenio_oauthclient import TestRemoteToken
        >>> factory = TestRemoteToken.create_from_kwargs(access_token='myaccesstoken')
        >>> factory.remote_token
        Remote Token <token_type=None access_token=****oken>
        >>> factory.remote_token.access_token
        'myaccesstoken'
        >>> factory.remote_account
        Remote Account <id=10, user_id=43>
    """
    model_class = RemoteToken

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()

        # Check all required fields.
        updated_kwargs = kwargs.copy()
        if not kwargs.pop('access_token', None):
            updated_kwargs['access_token'] = generate_random_string(255)
        if not kwargs.pop('remote_account', None):
            # Create a RemoteAccount.
            instance.remote_account = TestRemoteAccount\
                .create_from_kwargs(**kwargs).remote_account
            db.session.flush()
            updated_kwargs['remote_account'] = instance.remote_account

        instance.remote_token = super(TestRemoteToken, cls)\
            .create_from_kwargs(updated_kwargs)
        return instance

    @classmethod
    def create_for_remote_account(cls, remote_account):
        return cls.create_from_kwargs(remote_account=remote_account)

    @classmethod
    def create_for_orcid(cls, orcid, allow_push=True):
        factory_user_identity = TestUserIdentity.create_for_orcid(orcid)
        extra_data = dict(allow_push=allow_push, orcid=orcid)
        factory_remote_account = TestRemoteAccount.create_for_user(
            factory_user_identity.user, extra_data=extra_data)
        db.session.flush()
        return cls.create_for_remote_account(factory_remote_account.remote_account)
