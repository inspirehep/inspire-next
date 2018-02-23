# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from invenio_workflows import (
    ObjectStatus,
    start,
    workflow_object_class,
)

from jsonschema import ValidationError


def test_authors_workflow_stops_when_record_is_not_valid(workflow_app):
    invalid_record = {
        'name': {
            'preferred_name': 'John Smith',
            'value': 'Smith, John'
        }
    }

    obj = workflow_object_class.create(
        data=invalid_record,
        data_type='authors',
        id_user=1,
    )
    obj_id = obj.id

    with pytest.raises(ValidationError):
        start('author', invalid_record, obj_id)

    obj = workflow_object_class.get(obj_id)

    assert obj.status == ObjectStatus.ERROR
    assert '_error_msg' in obj.extra_data
    assert 'required' in obj.extra_data['_error_msg']


def test_authors_workflow_continues_when_record_is_valid(workflow_app, mocked_external_services):
    valid_record = {
        '_collections': ['Authors'],
        'name': {
            'preferred_name': 'John Smith',
            'value': 'Smith, John'
        }
    }

    obj = workflow_object_class.create(
        data=valid_record,
        data_type='authors',
        id_user=1,
    )

    start('author', valid_record, obj.id)

    obj = workflow_object_class.get(obj.id)

    assert obj.status == ObjectStatus.HALTED
    assert '_error_msg' not in obj.extra_data
