# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""Users roles dump functions."""

from __future__ import absolute_import, print_function

from invenio_access.models import UserAccROLE

import json


def get(query, *args, **kwargs):
    """Get roles definitions to dump."""
    user_roles = UserAccROLE.query.all()
    users = [
        dict(user_id=row.id_user,
             role_id=row.id_accROLE)
        for row in user_roles
    ]


    return len(users), users


def dump(user, *args, **kwargs):
    """Dump all user roles."""
    return user
