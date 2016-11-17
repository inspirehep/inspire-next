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


"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

from celery import shared_task


@shared_task()
def import_access(obj):
    from invenio_accounts.models import Role
    from invenio_db import db
    role = Role(
        id=obj.get('id'),
        name=obj.get('name'),
        description=obj.get('description')
    )

    db.session.merge(role)
    db.session.commit()

    from invenio_access.models import ActionRoles
    for acc in obj['actions']:
        action = ActionRoles(
            id=acc.get('id'),
            action=acc.get('name'),
            exclude=False,
            role_id=obj.get('id')
        )

        db.session.merge(action)
    db.session.commit()


@shared_task()
def import_userrole(obj):
    from invenio_accounts.models import userrole
    from invenio_db import db
    urole = userrole(
        user_id=obj.get('user_id'),
        role_id=obj.get('role_id')
    )

    db.session.merge(urole)
    db.session.commit
