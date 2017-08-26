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

import pytest
from flask import url_for
from flask_security.utils import hash_password

from invenio_access.models import ActionUsers
from invenio_accounts.models import User
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db


@pytest.fixture(scope='function')
def users(app):
    """Create user fixtures."""
    hashed_password = hash_password('123456')
    user = User(
        email='user@inspirehep.net',
        password=hashed_password,
        active=True
    )
    user_allowed = User(
        email='user_allowed@inspirehep.net',
        password=hashed_password,
        active=True
    )

    db.session.add_all([user, user_allowed])
    db.session.commit()

    author_admin = ActionUsers(
        action='admin-holdingpen-authors',
        user_id=user_allowed.id
    )

    db.session.add(author_admin)
    db.session.commit()

    yield

    ActionUsers.query.filter_by(action='admin-holdingpen-authors').delete()
    User.query.filter_by(email='user@inspirehep.net').delete()
    User.query.filter_by(email='user_allowed@inspirehep.net').delete()
    db.session.commit()


def test_holdingpen_author_views_access(app, app_client, users):
    """Check permissions of author related views."""
    # An anonymous user is redirected to login page
    res = app_client.get(url_for('inspirehep_authors.newreview'))
    assert res.status_code == 302
    assert 'login' in res.location

    res = app_client.post(
        url_for('inspirehep_authors.reviewhandler'))
    assert res.status_code == 302
    assert 'login' in res.location

    res = app_client.get(
        url_for('inspirehep_authors.holdingpenreview'))
    assert res.status_code == 302
    assert 'login' in res.location

    # Logged-in user with no permission should receive 403
    login_user_via_session(app_client, email='user@inspirehep.net')

    res = app_client.get(url_for('inspirehep_authors.newreview'))
    assert res.status_code == 403

    res = app_client.post(
        url_for('inspirehep_authors.reviewhandler'))
    assert res.status_code == 403

    res = app_client.get(
        url_for('inspirehep_authors.holdingpenreview'))
    assert res.status_code == 403

    # User with admin-holdingpen-authors action allowed can access
    # XXX: 400 is returned because no object id is passed to the views
    login_user_via_session(app_client, email='user_allowed@inspirehep.net')

    res = app_client.get(url_for('inspirehep_authors.newreview'))
    assert res.status_code == 400

    res = app_client.post(
        url_for('inspirehep_authors.reviewhandler'))
    assert res.status_code == 400

    res = app_client.get(
        url_for('inspirehep_authors.holdingpenreview'))
    assert res.status_code == 400
