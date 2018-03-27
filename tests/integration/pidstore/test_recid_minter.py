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

from mock import Mock, patch
import pytest

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore import minters
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
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    return record


def test_recid_minter_happy(isolated_app, record):
    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 0
    minters.inspire_recid_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()
    assert len(pids) == 1
    for pid in pids:
        assert pid.pid_type == 'lit'
        assert pid.object_type == 'rec'
        assert pid.object_uuid == record.id
        assert pid.status == PIDStatus.REGISTERED


def test_recid_minter_happy_all_minters(isolated_app, record):
    minter1 = Mock()
    minter2 = Mock()

    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 0

    with patch('inspirehep.modules.pidstore.minters.MINTERS',
               [minter1, minter2, minters.inspire_recid_minter]):
        minters.inspire_recid_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()
    assert len(pids) == 1

    minter1.assert_called_once_with(str(record.id), record)
    minter2.assert_called_once_with(str(record.id), record)


def test_recid_minter_happy_not_all_minters(isolated_app, record):
    minter1 = Mock()
    minter2 = Mock()

    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 0
    with patch('inspirehep.modules.pidstore.minters.MINTERS',
               [minter1, minter2]):
        minters.inspire_recid_minter(str(record.id), record, False)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()
    assert len(pids) == 1

    minter1.assert_not_called()
    minter2.assert_not_called()


@pytest.fixture(scope='function')
def record_w_control_number():
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
        'control_number': 123,
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    return record


def test_recid_minter_happy_w_control_num(isolated_app, record_w_control_number):
    record = record_w_control_number
    assert PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).count() == 0
    minters.inspire_recid_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()
    assert len(pids) == 1
    for pid in pids:
        assert pid.pid_type == 'lit'
        assert pid.pid_value == '123'
        assert pid.object_type == 'rec'
        assert pid.object_uuid == record.id
        assert pid.status == PIDStatus.REGISTERED
