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

from __future__ import absolute_import, division, print_function

from invenio_workflows import start, workflow_object_class

from inspire_json_merger.api import get_head_source as merger_get_source
from inspirehep.modules.workflows.tasks.manual_merging import (
    halt_for_merge_approval,
    merge_records,
    save_roots,
    store_records,
)
from inspirehep.modules.workflows.tasks.merging import get_head_source
from inspirehep.utils.record import get_source
from inspirehep.utils.record_getter import get_db_record


class ManualMerge(object):
    name = 'MERGE'
    data_type = ''

    workflow = ([
        merge_records,
        halt_for_merge_approval,
        save_roots,
        store_records,
    ])


def start_merger(head_id, update_id, current_user_id=None):
    """Start a new ManualMerge workflow to merge two records manually.

    Args:
        head_id: the id of the first record to merge. This record is the one
            that will be updated with the new information.
        update_id: the id of the second record to merge. This record is the
            one that is going to be deleted and replaced by `head`.
        current_user_id: Id of the current user provided by the Flask app.

    Returns:
        (int): the current workflow object's id.
    """
    data = {
        'pid_type': 'lit',  # TODO: support
        'recid_head': head_id,
        'recid_update': update_id,
    }

    head = get_db_record('lit', head_id)
    update = get_db_record('lit', update_id)

    workflow_object = workflow_object_class.create(
        data=None,
        id_user=current_user_id,
        data_type='hep'
    )

    wf_id = workflow_object.id    # to retrieve it later
    workflow_object.extra_data.update(data)

    # preparing identifiers in order to do less requests possible later
    head_source = get_head_source(head.id) or merger_get_source(head)

    update_source = get_source(update)
    update_source = update_source if update_source else 'arxiv'

    workflow_object.extra_data['head_source'] = head_source.lower()
    workflow_object.extra_data['update_source'] = update_source.lower()

    workflow_object.extra_data['head_control_number'] = head_id
    workflow_object.extra_data['update_control_number'] = update_id

    workflow_object.extra_data['head_uuid'] = str(head.id)
    workflow_object.extra_data['update_uuid'] = str(update.id)

    workflow_object.extra_data['head'] = head
    workflow_object.extra_data['update'] = update

    workflow_object.save()

    start('manual_merge', object_id=wf_id)

    return wf_id
