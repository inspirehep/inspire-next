# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

import flask
from flask import current_app as app
from redis import StrictRedis
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from time_execution import time_execution

from invenio_db import db
from invenio_oauthclient.models import (
    UserIdentity,
    RemoteAccount,
    RemoteToken,
)


CACHE_PREFIX = None
CACHE_EXPIRE = 60 * 60 * 24 * 30  # 30 days in seconds.


def get_access_tokens(orcids):
    """Get the remote tokens for the given ORCIDs.

    Args:
        orcids(List[str]): ORCIDs to get the tokens for.

    Returns:
        sqlalchemy.util._collections.result: pairs of (ORCID, access_token),
        for ORCIDs having a token. These are similar to named tuples, in that
        the values can be retrieved by index or by attribute, respectively
        ``id`` and ``access_token``.

    """
    return db.session.query(UserIdentity.id, RemoteToken.access_token).filter(
        RemoteToken.id_remote_account == RemoteAccount.id,
        RemoteAccount.user_id == UserIdentity.id_user,
        UserIdentity.id.in_(orcids),
        cast(RemoteAccount.extra_data, JSONB).contains({'allow_push': True}),
    ).all()


@time_execution
def delete_access_token(token_plain, orcid):
    # Store the invalid token in Redis to prevent it from coming back
    # from Legacy when `inspirehep.modules.orcid.tasks.import_legacy_orcid_tokens`
    # runs.
    cache = _OrcidInvalidTokensCache(token_plain)
    cache.write_invalid_token(orcid)

    # Delete token from the db.
    remote_token = RemoteToken.query.filter(
        RemoteToken.id_remote_account == RemoteAccount.id,
        RemoteAccount.user_id == UserIdentity.id_user,
        UserIdentity.id == orcid).one()
    assert remote_token.access_token == token_plain
    db.session.delete(remote_token)
    db.session.commit()


def is_access_token_invalid(token_plain):
    cache = _OrcidInvalidTokensCache(token_plain)
    return cache.does_invalid_token_exist()


class _OrcidInvalidTokensCache(object):
    def __init__(self, token_plain):
        self.token_plain = token_plain

    @property
    def redis(self):
        redis = getattr(flask.g, 'redis_client', None)
        if redis is None:
            url = app.config.get('CACHE_REDIS_URL')
            redis = StrictRedis.from_url(url)
            flask.g.redis_client = redis
        return redis

    @property
    def _key(self):
        prefix = ''
        if CACHE_PREFIX:
            prefix = '{}:'.format(CACHE_PREFIX)
        return '{}orcidinvalidtoken:{}'.format(prefix, self.token_plain)

    def write_invalid_token(self, orcid):
        data = {'orcid': orcid}
        self.redis.hmset(self._key, data)
        if CACHE_EXPIRE:
            self.redis.expire(self._key, CACHE_EXPIRE)

    def does_invalid_token_exist(self):
        return bool(self.redis.exists(self._key))

    def delete_invalid_token(self):
        return self.redis.delete(self._key)
