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

import json


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


class ExtraDataEncoder(json.JSONEncoder):
    """Encoder for extra_data attribute."""

    def default(self, obj):
        import numpy
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, numpy.ndarray):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def get(*args, **kwargs):
    """Get workflow objects.

    :returns: count and list of items to dump.
    :rtype: tuple (count, list)
    """
    from sqlalchemy.orm import joinedload
    from invenio_ext.sqlalchemy import db
    from invenio_workflows.models import BibWorkflowObject, Workflow
    query = db.session.query(BibWorkflowObject) \
        .options(joinedload(BibWorkflowObject.workflow)) \
        .filter(BibWorkflowObject.id_workflow == Workflow.uuid) \
        .filter(Workflow.name.in_(WORKFLOWS_TO_KEEP)) \
        .order_by(BibWorkflowObject.id.desc())
    return 500, query.limit(500)
    # return query.count(), query.limit(500)


def dump(item, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the workflow object and associated workflow engine.

    :returns: User serialized to dictionary.
    :rtype: dict
    """
    from inspirehep.modules.workflows.models import Payload
    from invenio_deposit.models import Deposition

    eng = dict(
        uuid=item.workflow.uuid,
        name=item.workflow.name,
        created=item.workflow.created.isoformat(),
        modified=item.workflow.modified.isoformat(),
        id_user=item.workflow.id_user,
        status=item.workflow.status,
        extra_data=item.workflow.get_extra_data(),
    )
    data = {}
    old_data = item.get_data()
    extra_data = item.get_extra_data()
    if item.workflow.name == 'process_record_arxiv':
        data = _get_record(item, Payload)
        data['files'] = old_data.get('files')
    elif item.workflow.name == 'literature':
        data = _get_record(item, Deposition)
        data['files'] = old_data.get('files')
        extra_data['formdata'] = old_data['drafts']['default']['values']
    else:
        data = old_data

    obj = dict(
        extra_data=extra_data,
        data=data,
        id=item.id,
        created=item.created.isoformat(),
        modified=item.modified.isoformat(),
        status=item.version,
        data_type=item.data_type,
        id_workflow=item.id_workflow,
        id_parent=item.id_parent,
        id_user=item.id_user,
    )
    # Very silly, but just for now to clean the data
    dumps = json.dumps(dict(
        obj=obj,
        eng=eng
    ), cls=ExtraDataEncoder)
    return json.loads(dumps)
