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

"""Tasks related to manual merge generic record."""

from __future__ import absolute_import, division, print_function

import json

from inspire_json_merger.inspire_json_merger import inspire_json_merge
from inspire_dojson.utils import get_record_ref
from inspirehep.modules.workflows.tasks.merging import insert_wf_record_source
from inspirehep.utils.record import get_source
from inspirehep.utils.record_getter import get_db_record
from inspirehep.modules.workflows.utils import with_debug_logging
from invenio_db import db


def _check_sources(wf_obj, head, update):
    # Many records in Inspire don't have an acquisition_source.
    # If the records to merge also don't, they are treated as arxiv records.
    # We expect the `manual_merge` workflow to work on arxiv-publisher or
    # publisher-arxiv records. In other cases, the arxive-arxiv strategy
    # will be used, enforcing acquisition_source field to arxiv.
    source_head = wf_obj.extra_data.get('head_source')
    source_updated = wf_obj.extra_data.get('update_source')

    if not head.get('acquisition_source'):
        head['acquisition_source'] = {'source': source_head or 'arxiv'}

    if not update.get('acquisition_source'):
        update['acquisition_source'] = {'source': source_updated or 'arxiv'}


def _get_head_and_update(obj):
    """Retrieve from the database the records defined by their id in the
    workflow object, in according to the pid_type value in `obj`.

    Arguments:
        obj(WorkflowObject): the current workflow object

    Returns:
        tuple(InspireRecord): the two records to merge

    Raise:
        RecordGetterError in case head or update does not exist
    """
    pid_type = obj.extra_data.get('pid_type')
    recid_head = obj.extra_data.get('recid_head')
    recid_update = obj.extra_data.get('recid_update')

    head = get_db_record(pid_type, recid_head)
    update = get_db_record(pid_type, recid_update)

    return head, update


@with_debug_logging
def merge_records(obj, eng):
    """Merge the records which ids are defined in the `obj` parameter and store
    the merged record and relative conflicts in `obj.data` and
    `obj.extra_data['conflicts']`.
    """
    head, update = _get_head_and_update(obj)
    _check_sources(obj, head, update)

    merged, conflicts = inspire_json_merge(
        {},
        head,
        update,
        # TODO: pass pid_type when it will be able to merge other collections
    )
    obj.data = merged
    obj.extra_data['conflicts'] = json.dumps(conflicts)


@with_debug_logging
def ask_for_approval(obj, eng):
    """Stop the Workflow engine"""
    eng.halt(
        action="HALTED",
        msg='Manual Merge halted for curator approval.'
    )


@with_debug_logging
def edit_metadata_and_store(obj, eng):
    """Replace the `head` record with the previously merged record and updates
    some reference in order to delete the `update` record, linking it to the
    new `head`.
    """

    head_rec, update_rec = _get_head_and_update(obj)

    head_rec.clear()
    head_rec.update(obj.data)     # head's content will be replaced by merged
    update_rec.merge(head_rec)   # update's uuid will point to head's uuid
    update_rec.delete()          # mark update record as deleted

    # add schema contents to refer deleted record to the merged one
    update_rec['new_record'] = get_record_ref(
        head_rec['control_number'],
        'record'
    )
    _add_deleted_records(head_rec, update_rec)

    head_rec.commit()
    update_rec.commit()
    db.session.commit()


def _add_deleted_records(new_rec, deleted_rec):
    """Mark `deleted_rec` as replaced by `new_rec` by adding its id to the
    deleted_record list property.
    """
    ref = get_record_ref(deleted_rec['control_number'], 'record')
    new_rec.setdefault('deleted_records', []).append(ref)


def save_records_as_roots(obj, eng):
    """Save `head` and `update` records in the Root table in the db if they
    have different `acquisition_source`, otherwise the only `head` is saved.
    """
    head_rec, update_rec = _get_head_and_update(obj)

    uuid = head_rec.id
    source = get_source(head_rec)
    content = head_rec.dumps()

    insert_wf_record_source(json=content, source=source, record_uuid=uuid)

    # need to save just one root per source
    if get_source(update_rec) != get_source(head_rec):
        insert_wf_record_source(
            update_rec.id,
            get_source(update_rec),
            update_rec.dumps()
        )
    obj.save()
    db.session.commit()
