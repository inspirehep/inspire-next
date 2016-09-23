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


"""Access rights dump functions."""

from __future__ import absolute_import, print_function

import json


def _get_run_sql():
    """Import ``run_sql``."""
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql
    return run_sql


def get_connected_actions(role_id):
    """Get roles connected to an action."""
    run_sql = _get_run_sql()

    actions = []
    res = run_sql('select a.id, a.name, a.description, a.allowedkeywords, a.optional '
                  'from accROLE as r, accACTION as a, accROLE_accACTION_accARGUMENT as ra'
                  'where ra.id_accROLE=%s and ra.id_accACTION=a.id group by a.id', (role_id, ))

    for r in res:
        actions.append(
            {
                'id': r[0],
                'name': r[1],
                'description': r[2],
                'allowedkeywords': r[3],
                'optional': r[4]
            }
        )

    return actions


def get(query, *args, **kwargs):
    """Get roles definitions to dump."""
    run_sql = _get_run_sql()
    roles = [
        dict(id=row[0],
             name=row[1],
             description=row[2])
        for row in run_sql(
            'select * from accROLE',
            run_on_slave=True)
    ]

    return len(roles), roles


def dump(role, *args, **kwargs):
    """Dump all roles connected with the action."""
    role['actions'] = list(get_connected_actions(role['id']))

    return role
