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

from inspire_dojson.utils import get_record_ref
from inspire_json_merger.api import merge
from invenio_db import db

from inspirehep.modules.workflows.utils import insert_wf_record_source
from inspirehep.modules.workflows.utils import with_debug_logging
from inspirehep.utils.record_getter import get_db_record


@with_debug_logging
def merge_records(obj, eng):
    """Perform a manual merge operation.

    Merge two records, ``head`` and ``update``, defined in the given
    workflow, and replace its payload with the merged record.
    Since this is used in the 'manual'merge' use case, we assume that there
    is not sa common ancestor for these two records, so ``root`` is empty.
    """
    head = obj.extra_data['head']
    update = obj.extra_data['update']

    merged, conflicts = merge(
        root={},
        head=head,
        update=update,
        head_source=obj.extra_data['head_source']
    )
    obj.data = merged
    obj.extra_data['conflicts'] = [json.loads(c.to_json()) for c in conflicts]
    obj.save()


@with_debug_logging
def halt_for_approval(obj, eng):
    """Stop the Workflow engine.

    This pause the workflow using the custom action `merge_approval`, that is
    used every time there are merging conflicts to solve.
    """
    eng.halt(
        action="merge_approval",
        msg='Manual Merge halted for curator approval.'
    )


@with_debug_logging
def edit_metadata_and_store(obj, eng):
    """Store the records involved in the manual merging process.

    Delete the ``update``, redirecting it to the merged record. Add a
    reference in the merged record to the deleted one, and store them in the db.
    """
    head = get_db_record('lit', obj.extra_data['head_control_number'])
    update = get_db_record('lit', obj.extra_data['update_control_number'])

    head.clear()
    head.update(obj.data)    # head's content will be replaced by merged
    update.merge(head)       # update's uuid will point to head's uuid
    update.delete()          # mark update record as deleted

    # add schema contents to refer deleted record to the merged one
    update['new_record'] = get_record_ref(
        head['control_number'],
        endpoint='record'
    )

    ref = get_record_ref(update['control_number'], 'record')
    head.setdefault('deleted_records', []).append(ref)

    head.commit()
    update.commit()
    db.session.commit()


def save_roots(obj, eng):
    """Save `head` and `update` in the ``WorkflowRecordSource`` table.

    Important: ``update`` is saved only if it has a different source from
    ``head``, because there has to be only one "root" per source for a given
    record.
    """
    head = obj.extra_data['head']
    update = obj.extra_data['update']
    head_source = obj.extra_data['head_source']
    update_source = obj.extra_data['update_source']

    obj.save()

    insert_wf_record_source(
        json=head,
        source=head_source,
        record_uuid=obj.extra_data['head_uuid'],
    )

    if update_source != head_source:  # need to save just one root per source
        insert_wf_record_source(
            json=update,
            source=update_source.lower(),
            record_uuid=obj.extra_data['update_uuid'],
        )
