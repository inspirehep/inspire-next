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

import pytest
from calls import do_resolve_manual_merge_wf
from invenio_workflows import ObjectStatus, workflow_object_class

from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.modules.workflows.utils import read_wf_record_source
from inspirehep.modules.workflows.workflows.manual_merge import start_merger
from inspirehep.utils.record import get_source
from inspirehep.utils.record_getter import get_db_record, RecordGetterError


def fake_record(title, rec_id):
    return {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'titles':  [{'title': title}],
        '_collections': ['Literature'],
        'document_type': ['article'],
        'acquisition_source': {'source': 'arxiv'},
        'arxiv_eprints': [{'value': '1701.01431', 'categories': ['cs']}],
        'control_number': rec_id
    }


def test_manual_merge_existing_records(workflow_app):

    json_head = fake_record('This is the HEAD', 1)
    json_update = fake_record('While this is the update', 2)

    head = record_insert_or_replace(json_head)
    update = record_insert_or_replace(json_update)
    head_id = head.id
    update_id = update.id

    obj_id = start_merger(
        head_id=1,
        update_id=2,
        current_user_id=1,
    )

    do_resolve_manual_merge_wf(workflow_app, obj_id)

    # retrieve it again, otherwise Detached Instance Error
    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.COMPLETED
    assert obj.extra_data['approved'] is True
    assert obj.extra_data['auto-approved'] is False

    last_root = read_wf_record_source(head_id, 'arxiv')
    assert last_root.json == head

    head_source = obj.extra_data['head_source']
    update_source = obj.extra_data['update_source']

    assert head_source == update_source
    # since head and update have the same source, only head is saved as root
    root_update = read_wf_record_source(update_id, get_source(update))
    assert root_update is None

    # check that head's content has been replaced by merged
    from inspirehep.modules.records import RecordMetadata
    deleted_record = RecordMetadata.query.filter_by(id=update_id).one()

    latest_record = get_db_record('lit', 1)

    assert deleted_record.json['deleted'] is True

    # check deleted record is linked in the latest one
    deleted_rec_ref = {'$ref': 'http://localhost:5000/api/record/2'}
    assert [deleted_rec_ref] == latest_record['deleted_records']

    # check the merged record is linked in the deleted one
    new_record_metadata = {'$ref': 'http://localhost:5000/api/record/1'}
    assert new_record_metadata == deleted_record.json['new_record']

    del latest_record['deleted_records']
    assert latest_record == obj.data  # -> resulted merged record


def test_manual_merge_with_none_record(workflow_app):
    json_head = fake_record('This is the HEAD', 1)

    record_insert_or_replace(json_head)
    non_existing_id = 123456789

    with pytest.raises(RecordGetterError):
        start_merger(
            head_id=1,
            update_id=non_existing_id,
            current_user_id=1,
        )
