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

"""Tasks related to manual merging."""

from __future__ import absolute_import, division, print_function

import requests
from invenio_db import db

import backoff
from inspire_dojson.utils import get_record_ref
from inspire_json_merger.api import merge
from inspirehep.modules.workflows.utils import (
    get_resolve_merge_conflicts_callback_url,
    with_debug_logging,
    read_all_wf_record_sources
)
from inspirehep.modules.workflows.models import WorkflowsRecordSources
from inspirehep.modules.workflows.utils import put_record_to_hep
from inspirehep.modules.records.api import InspireRecord


@with_debug_logging
def merge_records(obj, eng):
    """Perform a manual merge.

    Merges two records stored in the workflow object as the content of the
    ``head`` and ``update`` keys, and stores the result in ``obj.data``.
    Also stores the eventual conflicts in ``obj.extra_data['conflicts']``.

    Because this is a manual merge we assume that the two records have no
    common ancestor, so ``root`` is the empty dictionary.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    head, update = obj.extra_data['head'], obj.extra_data['update']

    merged, conflicts = merge(
        root={},
        head=head,
        update=update,
    )

    obj.data = merged
    obj.extra_data['conflicts'] = conflicts
    obj.save()


@with_debug_logging
def halt_for_merge_approval(obj, eng):
    """Wait for curator approval.

    Pauses the workflow using the ``merge_approval`` action, which is resolved
    whenever the curator says that the conflicts have been solved.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    eng.halt(
        action='merge_approval',
        msg='Manual Merge halted for curator approval.',
    )


@with_debug_logging
def save_roots(obj, eng):
    """Save and update the head roots and delete the update roots from the db.

    If both head and update have a root from a given source, then the older one is
    removed and the newer one is assigned tot the head. Otherwise, assign the update
    roots from sources that are missing among the head roots to the head.
    i.e. it is an union-like operation.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    def _merge_roots(new_uuid, head_roots, update_roots):
        """Return the new roots to link to head."""
        head_sources = {h.source: h for h in head_roots}
        for update_root in update_roots:
            if update_root.source not in head_sources:
                head_roots.append(
                    WorkflowsRecordSources(
                        source=update_root.source,
                        record_uuid=new_uuid,
                        json=update_root.json
                    )
                )
            elif head_sources[update_root.source].updated < update_root.updated:
                head_roots.remove(head_sources[update_root.source])
                head_roots.append(
                    WorkflowsRecordSources(
                        source=update_root.source,
                        record_uuid=new_uuid,
                        json=update_root.json
                    )
                )
            db.session.delete(update_root)
        return head_roots

    head_uuid, update_uuid = obj.extra_data['head_uuid'], obj.extra_data['update_uuid']
    obj.save()  # XXX: otherwise obj.extra_data will be wiped by a db session commit below.

    head_roots = read_all_wf_record_sources(head_uuid)
    update_roots = read_all_wf_record_sources(update_uuid)

    updated_head_rooots = _merge_roots(head_uuid, head_roots, update_roots)
    for head_root in updated_head_rooots:
        db.session.merge(head_root)
    db.session.commit()


@with_debug_logging
def store_head_version(obj, eng):
    head_uuid = obj.extra_data['head_uuid']
    head_record = InspireRecord.get_record(head_uuid)
    obj.extra_data['head_version_id'] = head_record.model.version_id
    obj.extra_data['callback_url'] = get_resolve_merge_conflicts_callback_url()
    obj.save()


@with_debug_logging
@backoff.on_exception(backoff.expo, (requests.exceptions.ConnectionError), base=4, max_tries=5)
def store_records(obj, eng):
    """Store the records involved in the manual merge.

    Update the head with the deleted record and send it to hep.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    head_control_number = obj.extra_data['head_control_number']
    update_control_number = obj.extra_data['update_control_number']
    head = dict(obj.data)

    update_ref = get_record_ref(update_control_number, 'literature')
    head.setdefault('deleted_records', []).append(update_ref)

    head_version_id = obj.extra_data['head_version_id']
    headers = {
        'If-Match': '"{0}"'.format(head_version_id - 1)
    }

    put_record_to_hep(
        'lit',
        head_control_number,
        data=obj.data,
        headers=headers
    )
