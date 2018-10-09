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

import mock
import pytest

from flask import current_app

from invenio_db import db
from invenio_oauthclient.errors import AlreadyLinkedError
from invenio_oauthclient.models import RemoteToken, User, UserIdentity

from inspirehep.modules.orcid.tasks import RemoteTokenOrcidMismatch, _link_user_and_token


@pytest.mark.usefixtures('isolated_app')
class TestLinkUserAndToken(object):
    def setup(self):
        with db.session.begin_nested():
            self.user = User()
            self.user.email = 'email@foo.bar'
            db.session.add(self.user)
        self.orcid = 'myorcid'
        self.token = 'mytoken'
        self.name = 'myname'

    def _assert_remote_account_and_remote_token_and_user_identity(self):
        assert len(self.user.remote_accounts) == 1
        remote_account = self.user.remote_accounts[0]
        assert remote_account.extra_data['orcid'] == self.orcid
        assert remote_account.extra_data['allow_push']
        assert remote_account.extra_data['full_name'] == self.name
        assert len(remote_account.remote_tokens) == 1
        remote_token = remote_account.remote_tokens[0]
        assert remote_token.access_token == self.token
        identity = UserIdentity.query.filter_by(id_user=self.user.id).one()
        assert identity.id == self.orcid
        assert identity.method == 'orcid'

    def test_new_user_new_token(self):
        _link_user_and_token(self.user, self.name, self.orcid, self.token)

        self._assert_remote_account_and_remote_token_and_user_identity

    def test_existent_token(self):
        # Create existing token: RemoteToken, RemoteAccount, UserIdentity.
        with db.session.begin_nested():
            # Create RemoteToken and RemoteAccount.
            RemoteToken.create(
                user_id=self.user.id,
                client_id=current_app.config['ORCID_APP_CREDENTIALS']['consumer_key'],
                token=self.token,
                secret=None,
                extra_data={
                    'orcid': self.orcid,
                    'full_name': self.name,
                    'allow_push': True,
                }
            )
            user_identity = UserIdentity(
                id=self.orcid,
                method='orcid',
                id_user=self.user.id
            )
            db.session.add(user_identity)

        with mock.patch('inspirehep.modules.orcid.tasks.oauth_link_external_id') as mock_oauth_link_external_id:
            # Mocking `oauth_link_external_id` is necessary because when running
            # with `isolated_app` it raises
            # "FlushError: New instance ... with identity key (...) conflicts with persistent instance ..."
            # rather than the standard and expected `IntegrityError` (which
            # is raised instead when run without `isolated_app`).
            mock_oauth_link_external_id.side_effect = AlreadyLinkedError(self.user, self.orcid)
            _link_user_and_token(self.user, self.name, self.orcid, self.token)

        self._assert_remote_account_and_remote_token_and_user_identity()

    def test_existent_token_for_same_user_but_different_orcid(self):
        # Create existing token: RemoteToken, RemoteAccount, UserIdentity.
        other_orcid = 'otherorcid'
        with db.session.begin_nested():
            # Create RemoteToken and RemoteAccount.
            RemoteToken.create(
                user_id=self.user.id,
                client_id=current_app.config['ORCID_APP_CREDENTIALS']['consumer_key'],
                token=self.token,
                secret=None,
                extra_data={
                    'orcid': other_orcid,
                    'full_name': self.name,
                    'allow_push': True,
                }
            )
            user_identity = UserIdentity(
                id=other_orcid,
                method='orcid',
                id_user=self.user.id
            )
            db.session.add(user_identity)

        with pytest.raises(RemoteTokenOrcidMismatch):
            _link_user_and_token(self.user, self.name, self.orcid, self.token)
