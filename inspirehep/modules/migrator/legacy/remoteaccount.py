# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""RemoteAccount dump functions."""

from __future__ import absolute_import, print_function

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


def get(*args, **kwargs):
    """Get remoteaccounts."""
    from invenio_accounts.models import User
    q = User.query
    return q.count(), q.all()


def dump(u, from_date, **kwargs):
    """Dump the remoteaccounts as a list of dictionaries."""
    from invenio_oauthclient.models import RemoteAccount
    from invenio_accounts.models import UserEXT

    # First fetch all the remote account information
    remoteaccount = {}
    try:
        result = RemoteAccount.query.filter_by(user_id=u.id).one()
        remoteaccount = dict(id=result.id,
                             user_id=result.user_id,
                             client_id=result.client_id,
                             extra_data=result.extra_data)
    except NoResultFound:
        print(
            'INFO: user id {} has no remote account'.format(u.id))
    except MultipleResultsFound:
        print(
            'WARN: user id {} has multiple remote account'.format(u.id))

    # And then fetch the user ext information
    userext = {}
    try:
        result = UserEXT.query.filter_by(id_user=u.id).one()
        userext = dict(id=result.id,
                       id_user=result.id_user,
                       method=result.method)
    except NoResultFound:
        print('INFO: user id {} has no userext entry'.format(u.id))
    except MultipleResultsFound:
        print(
            'WARN: user id {} has multiple userext entries'.format(u.id))

    return {
        'remoteaccount': remoteaccount,
        'userext': userext
    }
