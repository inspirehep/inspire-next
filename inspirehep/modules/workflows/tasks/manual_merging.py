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

from invenio_db import db

from inspire_dojson.utils import get_record_ref
from inspire_json_merger.api import merge
from inspirehep.modules.workflows.utils import (
    with_debug_logging,
    read_all_wf_record_sources
)
from inspirehep.modules.workflows.models import WorkflowsRecordSources
from inspirehep.utils.record_getter import get_db_record


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
def store_records(obj, eng):
    """Store the records involved in the manual merge.

    Performs the following steps:

        1. Updates the ``head`` so that it contains the result of the merge.
        2. Marks the ``update`` as merged with the ``head`` and deletes it.
        3. Populates the ``deleted_records`` and ``new_record`` keys in,
           respectively, ``head`` and ``update`` so that they contain a JSON
           reference to each other.

    Todo:
        The last step should be performed by the ``merge`` method itself.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    head_control_number = obj.extra_data['head_control_number']
    update_control_number = obj.extra_data['update_control_number']

    head = get_db_record('lit', head_control_number)
    update = get_db_record('lit', update_control_number)

    # 1. Updates the head so that it contains the result of the merge.
    head.clear()
    head.update(obj.data)
    # 2. Marks the update as merged with the head and deletes it.
    update.merge(head)
    update.delete()
    # 3. Populates the deleted_records and new_record keys.
    update['new_record'] = get_record_ref(head_control_number, 'literature')
    update_ref = get_record_ref(update_control_number, 'literature')
    head.setdefault('deleted_records', []).append(update_ref)

    head.commit()
    update.commit()
    db.session.commit()
