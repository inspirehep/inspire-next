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
import uuid

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.exceptions import DuplicatedPIDMinterException
from inspirehep.modules.pidstore.minters import HdlMinter
from inspirehep.modules.records.api import InspireRecord


@pytest.fixture(scope='function')
def record():
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        '_collections': ['Literature'],
        'titles': [
            {'title': 'merged'},
        ],
        'persistent_identifiers': [
            {
                'value': 'hdl1',
                'schema': 'HDL',
            },
            {
                'value': 'hdl2',
                'schema': 'HDL',
            },
        ],
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    return record


def test_hdl_minter_happy(isolated_app, record):
    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 0
    minter = HdlMinter()
    minter.mint(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()
    assert len(pids) == 2
    for pid in pids:
        assert pid.pid_type == 'hdl'
        assert pid.object_type == 'rec'
        assert pid.object_uuid == record.id
        assert pid.status == PIDStatus.RESERVED
    assert sorted([pid.pid_value for pid in pids]) == ['hdl1', 'hdl2']


def test_hdl_minter_duplicated(isolated_app, record):
    # Mint a PID.
    minter = HdlMinter()
    minter.mint(str(record.id), record)

    # Mint the same PID again.
    with pytest.raises(DuplicatedPIDMinterException) as exc:
        minter.mint(str(record.id), record)

    # Mint the same PID but related to a different record.
    with pytest.raises(DuplicatedPIDMinterException) as exc:
        minter.mint(str(uuid.uuid4()), record)

    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 2


@pytest.fixture(scope='function')
def record_w_existent_pids(record):
    for pid_value in ('val1', 'hdl1'):
        PersistentIdentifier.create(
            pid_type='hdl',
            pid_value=pid_value,
            object_type='rec',
            object_uuid=record.id,
            status=PIDStatus.RESERVED
        )
    return record


def test_hdl_minter_with_existent_pids(isolated_app, record_w_existent_pids):
    record = record_w_existent_pids
    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 2

    minter = HdlMinter()
    minter.mint(
        str(record.id),
        record,
        PersistentIdentifier.query.filter_by(object_uuid=str(record.id))
    )

    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), status=PIDStatus.RESERVED).all()
    assert len(pids) == 2
    for pid in pids:
        assert pid.pid_type == 'hdl'
        assert pid.object_type == 'rec'
        assert pid.object_uuid == record.id
        assert pid.status == PIDStatus.RESERVED
    assert sorted([pid.pid_value for pid in pids]) == ['hdl1', 'hdl2']
    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), status=PIDStatus.DELETED).count() == 1
