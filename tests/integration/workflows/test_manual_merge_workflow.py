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

import json
import os
import pytest

from invenio_workflows import ObjectStatus, workflow_object_class

from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.modules.workflows.tasks.merging import read_wf_record_source
from inspirehep.modules.workflows.workflows.manual_merge import start_merger
from inspirehep.utils.record import get_source
from inspirehep.utils.record_getter import get_db_record, RecordGetterError


def read_file(test_dir, file_name):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(base_dir, test_dir, file_name)) as f:
        return json.loads(f.read())


def test_manual_merge_existing_records(workflow_app):
    head = record_insert_or_replace(read_file('fixtures', 'manual_merge_record.json'))
    update = record_insert_or_replace(read_file('fixtures', 'manual_merge_record_2.json'))
    head_id = head.id
    update_id = update.id

    obj_id, merged, conflicts = start_merger(
        head_id=head['control_number'],
        update_id=update['control_number'],
        current_user_id=1,
        pid_type='lit'
    )

    obj = workflow_object_class.get(obj_id)
    obj.continue_workflow('continue_next')

    # retrieve it again, otherwise Detached Instance Error
    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.COMPLETED

    last_root = read_wf_record_source(head_id, get_source(head))
    assert last_root.json == head

    assert get_source(head) == get_source(update)
    # since head and update have the same source, only head is saved as root
    root_update = read_wf_record_source(update_id, get_source(update))
    assert root_update is None

    # check that head's content has been replaced by merged
    latest_record = get_db_record('lit', head['control_number'])
    deleted_rec_ref = {
        '$ref': 'http://localhost:5000/api/record/{}'.format(
            update['control_number']
        )
    }
    assert deleted_rec_ref in latest_record['deleted_records']

    del latest_record['deleted_records']
    assert latest_record == obj.data  # -> resulted merged record


def test_manual_merge_with_none_record(workflow_app):
    head = record_insert_or_replace(read_file('fixtures', 'manual_merge_record.json'))
    non_existing_id = 123456789

    with pytest.raises(RecordGetterError):
        start_merger(
            head_id=head['control_number'],
            update_id=non_existing_id,
            current_user_id=1,
            pid_type='lit'
        )
