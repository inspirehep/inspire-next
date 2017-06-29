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

"""Tests for manual merge workflows."""

from __future__ import absolute_import, division, print_function

import json
import os
import pytest

from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.records import InspireRecord
from inspirehep.modules.workflows.utils import retrieve_root_json
from inspirehep.modules.workflows.workflows.manual_merge import start_merger
from inspirehep.utils.record import get_source
from inspirehep.utils.record_getter import get_db_record, RecordGetterError


def read_file(test_dir, file_name):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(base_dir, test_dir, file_name)) as f:
        return json.loads(f.read())


def create_test_record(file_name):
    rec = read_file('fixtures', file_name)
    record = InspireRecord.create(rec)
    inspire_recid_minter(str(record.id), record)
    return record


def _remove_uuid_authors(record):
    for author in record['authors']:
        if author.get('uuid'):
            del author['uuid']
    return record


def test_manual_merge_existing_records(workflow_app):
    head = create_test_record('manual_merge_head.json')
    update = create_test_record('manual_merge_update.json')

    head_id = str(head.id)
    update_id = str(update.id)

    obj_id, merged, conflicts = start_merger(
        head_id=head['control_number'],
        update_id=update['control_number'],
        current_user_id=1,
        pid_type='lit'
    )

    # continue the workflow
    wkf_obj = workflow_object_class.get(obj_id)

    wkf_obj.continue_workflow('continue_next')

    # retrieve it again because it has finished is job
    wkf_obj = workflow_object_class.get(obj_id)
    merged = wkf_obj.data
    conflicts = wkf_obj.extra_data['conflicts']

    expected_result = read_file('fixtures', 'manual_merge_expected_merged.json')
    expected_conflicts = read_file('fixtures', 'manual_merge_conflicts.json')

    # since head and update have different acquisition sources
    # they will be saved both as root
    head_root = retrieve_root_json(str(head_id), get_source(head))
    update_root = retrieve_root_json(str(update_id), get_source(update))

    assert head_root == head
    assert update_root == update

    # check that head's content has been replaced by merged
    new_head = get_db_record('lit', head['control_number'])
    # new_head has a deleted_record field which is absent in merged var
    del new_head['deleted_records']
    assert new_head == merged

    _remove_uuid_authors(merged)
    _remove_uuid_authors(expected_result)

    assert merged == expected_result
    assert json.loads(conflicts) == expected_conflicts


def test_manual_merge_with_none_record(workflow_app):
    head = create_test_record('manual_merge_head.json')
    non_existing_id = 123456789

    with pytest.raises(RecordGetterError):
        start_merger(
            head_id=head['control_number'],
            update_id=non_existing_id,
            current_user_id=1,
            pid_type='lit'
        )
