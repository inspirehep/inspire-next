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

import re
import traceback

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from celery import shared_task
from redis import StrictRedis
from simplejson import loads

from invenio_oauthclient.utils import oauth_link_external_id
from invenio_oauthclient.models import RemoteToken, User, RemoteAccount, UserIdentity
from invenio_db import db
from invenio_oauthclient.errors import AlreadyLinkedError
from inspire_utils.logging import getStackTraceLogger
from inspire_utils.record import get_value
from inspirehep.modules.orcid.api import push_record_with_orcid
from inspirehep.modules.orcid.utils import get_literature_recids_for_orcid


LOGGER = getStackTraceLogger(__name__)


def legacy_orcid_arrays():
    """
    Generator to fetch token data from redis.

    Note: this function consumes the queue populated by the legacy tasklet:
    inspire/bibtasklets/bst_orcidsync.py

    Yields:
        list: user data in the form of [orcid, token, email, name]
    """
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)

    key = 'legacy_orcid_tokens'
    token = r.lpop(key)
    while token:
        yield loads(token)
        token = r.lpop(key)


def _link_user_and_token(user, name, orcid, token):
    """Create a link between a user and token, if possible.

    Args:
        user (invenio_oauthclient.models.User): an existing user object to connect the token to
        orcid (string): user's ORCID identifier
        token (string): OAUTH token for the user

    Returns:
        str: the ORCID associated with the new token if we created one, or the
        ORCID associated with the token whose ``allow_push`` flag changed state.

    """
    result = None

    try:
        # Link user and ORCID
        oauth_link_external_id(user, {
            'id': orcid,
            'method': 'orcid'
        })
    except AlreadyLinkedError:
        # User already has their ORCID linked
        pass

    # Check whether there are already tokens associated with this
    # ORCID identifier.
    tokens = RemoteToken.query.join(RemoteAccount).join(User)\
        .join(UserIdentity).filter(UserIdentity.id == orcid).all()

    if tokens:
        # Force the allow_push.
        with db.session.begin_nested():
            for token in tokens:
                if not token.remote_account.extra_data['allow_push']:
                    result = orcid
                token.remote_account.extra_data['allow_push'] = True
    else:
        # If not, create and put the token entry
        with db.session.begin_nested():
            result = orcid
            RemoteToken.create(
                user_id=user.id,
                client_id=get_value(current_app.config, 'ORCID_APP_CREDENTIALS.consumer_key'),
                token=token,
                secret=None,
                extra_data={
                    'orcid': orcid,
                    'full_name': name,
                    'allow_push': True,
                }
            )

    return result


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

    Returns:
        str: the ORCID associated with the new user if we created one, or the
        ORCID associated with the user whose ``allow_push`` flag changed state.

    """

    # Try to find an existing user entry
    user = _find_user_matching(orcid, email)

    # Make the user if didn't find existing one
    if not user:
        with db.session.begin_nested():
            user = User()
            user.email = email
            db.session.add(user)

    return _link_user_and_token(user, name, orcid, token)


@shared_task(ignore_result=True)
def import_legacy_orcid_tokens():
    """Task to import OAUTH ORCID tokens from legacy."""
    if get_value(current_app.config, 'ORCID_APP_CREDENTIALS.consumer_key') is None:
        return

    for user_data in legacy_orcid_arrays():
        try:
            orcid, token, email, name = user_data
            orcid_to_push = _register_user(name, email, orcid, token)
            if orcid_to_push:
                LOGGER.info(
                    'allow_push now enabled on %s, will push all works now',
                    orcid_to_push
                )
                recids = get_literature_recids_for_orcid(orcid_to_push)
                for recid in recids:
                    orcid_push.apply_async(
                        queue='orcid_push_legacy_tokens',
                        kwargs={
                            'orcid': orcid_to_push,
                            'rec_id': recid,
                            'oauth_token': token,
                        },
                    )
        except SQLAlchemyError as ex:
            LOGGER.exception(ex)

    db.session.commit()


@shared_task(bind=True)
def orcid_push(self, orcid, rec_id, oauth_token):
    """Celery task to push a record to ORCID.

    Args:
        self(celery.Task): the task
        orcid(string): an orcid identifier.
        rec_id(int): inspire record's id to push to ORCID.
        oauth_token(string): orcid token.
    """
    if not re.match(current_app.config.get(
            'FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX', '^$'), orcid):
        return None

    try:
        LOGGER.info('Will attempt to push #%s onto %s', rec_id, orcid)
        push_record_with_orcid(
            recid=str(rec_id),
            orcid=orcid,
            oauth_token=oauth_token,
        )
    except Exception as exc:
        LOGGER.info('Orcid push attempt (celery task) for orcid={} and rec_id={}'
                    ' failed:\n{}'.format(orcid, rec_id, traceback.format_exc()))
        raise self.retry(max_retries=3, countdown=300, exc=exc)


def _find_user_matching(orcid, email):
    """Attempt to find a user in our DB on either ORCID or email."""
    user_identity = UserIdentity.query.filter_by(id=orcid, method='orcid').first()
    if user_identity:
        return user_identity.user
    return User.query.filter_by(email=email).one_or_none()
