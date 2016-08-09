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

"""INSPIRE migrator load/dump workflow object."""

from __future__ import absolute_import, print_function

import six


WORKFLOWS_TO_KEEP = [
    'literature',
    'authornew',
    'authorupdate',
    'process_record_arxiv'
]


def _get_record(obj, model):
    from inspirehep.utils.helpers import get_record_from_model

    model = model(obj)
    record = get_record_from_model(model)
    if record:
        return record.dumps()
    return {}


def get(*args, **kwargs):
    """Get workflow objects.

    :returns: count and list of items to dump.
    :rtype: tuple (count, list)
    """
    from invenio_ext.sqlalchemy import db
    from invenio_workflows.models import BibWorkflowObject, Workflow
    query = db.session.query(BibWorkflowObject).filter(
        BibWorkflowObject.id_workflow == Workflow.uuid
    ).filter(
        Workflow.name.in_(WORKFLOWS_TO_KEEP)
    ).limit(5)
    all_obj = []
    for obj in query:
        if obj.workflow.name in WORKFLOWS_TO_KEEP:
            all_obj.append(obj)
    return len(all_obj), all_obj


def dump(obj, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the workflow object and associated workflow engine.

    :returns: User serialized to dictionary.
    :rtype: dict
    """
    from inspirehep.modules.workflows.models import Payload
    from invenio_deposit.models import Deposition

    eng = dict(
        uuid=obj.workflow.uuid,
        name=obj.workflow.name,
        created=obj.workflow.created.isoformat(),
        modified=obj.workflow.modified.isoformat(),
        id_user=obj.workflow.id_user,
        status=obj.workflow.status,
        extra_data=obj.workflow.get_extra_data(),
    )
    data = {}
    old_data = obj.get_data()
    extra_data = obj.get_extra_data()
    if obj.workflow.name == 'process_record_arxiv':
        data = _get_record(obj, Payload)
        data['files'] = old_data.get('files')
    elif obj.workflow.name == 'literature':
        data = _get_record(obj, Deposition)
        data['files'] = old_data.get('files')
        extra_data['formdata'] = old_data['drafts']['default']['values']
    else:
        data = old_data

    obj = dict(
        extra_data=extra_data,
        data=data,
        id=obj.id,
        created=obj.created.isoformat(),
        modified=obj.modified.isoformat(),
        status=obj.version,
        data_type=obj.data_type,
        id_workflow=obj.id_workflow,
        id_parent=obj.id_parent,
        id_user=obj.id_user,
    )
    return dict(
        obj=obj,
        eng=eng
    )
