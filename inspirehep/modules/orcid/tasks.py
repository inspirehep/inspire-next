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

"""Manage ORCID OAUTH token migration from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

from flask import current_app
from celery import shared_task
from celery.utils.log import get_task_logger
from redis import StrictRedis
from redis_lock import Lock
from simplejson import loads
from invenio_oauthclient.utils import oauth_get_user, oauth_link_external_id
from invenio_oauthclient.models import RemoteToken, User, RemoteAccount, UserIdentity
from invenio_db import db
from inspire_utils.record import get_value
from invenio_oauthclient.errors import AlreadyLinkedError

logger = get_task_logger(__name__)


def legacy_orcid_arrays():
    """Generator to fetch token data from redis.

    Yields:
        list: user data in the form of [orcid, token, email, name]
    """
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    lock = Lock(r, 'import_legacy_orcid_tokens', expire=120, auto_renewal=True)
    if lock.acquire(blocking=False):
        try:
            while r.llen('legacy_orcid_tokens'):
                yield loads(r.lrange('legacy_orcid_tokens', 0, 1)[0])
                r.lpop('legacy_orcid_tokens')
        finally:
            lock.release()
    else:
        logger.info("Import_legacy_orcid_tokens already executed. Skipping.")


def _link_user_and_token(user, name, orcid, token):
    """Create a link between a user and token, if possible.

    Args:
        user (invenio_oauthclient.models.User): an existing user object to connect the token to
        orcid (string): user's ORCID identifier
        token (string): OAUTH token for the user
    """
    try:
        # Link user and ORCID
        oauth_link_external_id(user, {
            'id': orcid,
            'method': 'orcid'
        })
    except AlreadyLinkedError:
        # User already has their ORCID linked
        pass

    # Is there already a token associated with this ORCID identifier?
    if RemoteToken.query.join(RemoteAccount).join(User).join(UserIdentity).filter(UserIdentity.id == orcid).count():
        return

    # If not, create and put the token entry
    with db.session.begin_nested():
        db.session.add(RemoteToken.create(
            user_id=user.id,
            client_id=get_value(current_app.config, 'ORCID_APP_CREDENTIALS.consumer_key'),
            token=token,
            secret=None,
            extra_data={
                'orcid': orcid,
                'full_name': name
            }
        ))


def _register_user(name, email, orcid, token):
    """Add a token to the user, creating the user if doesn't exist.

    There are multiple possible scenarios:
    - user exists, has ORCID and token already linked
    - user exists and has their ORCID linked, but no token is associated
    - user exists, but doesn't have the ORCID identifier linked
    - user doesn't exist at all

    In all the above scenarios this will create the missing parts.

    Args:
        name (string): user's name
        email (string): user's email address
        orcid (string): user's ORCID identifier
        token (string): OAUTH authorization token
    """

    # Try to find an existing user entry
    user_by_orcid = oauth_get_user(orcid)
    user_by_email = oauth_get_user(None, {
        'user': {
            'email': email
        }
    })

    # Make the user if didn't find existing one
    if not user_by_email and not user_by_orcid:
        user = User()
        user.email = email
        with db.session.begin_nested():
            db.session.add(user)
    else:
        user = user_by_orcid or user_by_email

    _link_user_and_token(user, name, orcid, token)


@shared_task(ignore_result=True)
def import_legacy_orcid_tokens():
    """Task to import OAUTH ORCID tokens from legacy."""
    if get_value(current_app.config, 'ORCID_APP_CREDENTIALS.consumer_key') is None:
        return

    for user_data in legacy_orcid_arrays():
        orcid, token, email, name = user_data
        _register_user(name, email, orcid, token)
