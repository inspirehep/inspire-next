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

"""INSPIRE migrator load/dump audit."""

from __future__ import absolute_import, print_function

import json

from sqlalchemy.orm.exc import NoResultFound

from inspirehep.modules.audit.models import Audit

from .workflows import WORKFLOWS_TO_KEEP


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def get(*args, **kwargs):
    """Get audits."""
    q = Audit.query
    return q.count(), q.all()


def dump(record, from_date, **kwargs):
    """Dump the audits as a list of dictionaries."""
    from invenio_workflows.models import BibWorkflowObject
    associated_object = BibWorkflowObject.query.filter_by(id=record.object_id).first()

    if associated_object.name in WORKFLOWS_TO_KEEP:
        return dict(id=record.id,
                    created=json.dumps(record.created, default=date_handler),
                    user_id=record.user_id,
                    object_id=record.object_id,
                    score=record.score,
                    user_action=record.user_action,
                    decision=record.decision,
                    source=record.source,
                    action=record.action)
