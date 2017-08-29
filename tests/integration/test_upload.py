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

import mock
import pytest

from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier

from integration_mocks import MockObj
from inspirehep.modules.workflows.tasks.upload import store_record
from inspirehep.modules.migrator.tasks.records import record_insert_or_replace


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
def test_store_record_store_in_the_pid_table(mock_random_letters, app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'authors': [
            {
                'full_name': 'Cox, Brian',
            }, {
                'full_name': 'Dan, Brown'
            }
        ],
        'document_type': [
            'article'
        ],
        'titles': [
            {'title': 'sample'}
        ],
    }

    obj = MockObj(record, {})
    store_record(obj)

    expected_texkey = 'Cox:2017xyz'
    expected_texkeys = [
            'Cox:2017xyz'
        ]

    pid = PersistentIdentifier.get('tex', expected_texkey)

    assert pid.pid_value == 'Cox:2017xyz'
    assert pid.pid_type == 'tex'
    assert obj.data['texkeys'] == expected_texkeys


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    side_effect=['xyz', 'xyz', 'abc'],
)
def test_store_record_store_duplicate_in_the_pid_table(mock_random_letters, app):
    first_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'authors': [
            {
                'full_name': 'Carl, Brian',
            }, {
                'full_name': 'Dan, Brown'
            }
        ],
        'document_type': [
            'article'
        ],
        'titles': [
            {'title': 'sample'}
        ],
    }
    second_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'authors': [
            {
                'full_name': 'Carl, Brian',
            }
        ],
        'document_type': [
            'article'
        ],
        'titles': [
            {'title': 'sample'}
        ],
    }

    first_obj = MockObj(first_record, {})
    second_obj = MockObj(second_record, {})

    store_record(first_obj)
    store_record(second_obj)

    expected_first_texkey = 'Carl:2017xyz'
    expected_first_texkeys = [
        'Carl:2017xyz'
    ]

    pid = PersistentIdentifier.get('tex', expected_first_texkey)

    assert pid.pid_value == 'Carl:2017xyz'
    assert pid.pid_type == 'tex'
    assert first_obj.data['texkeys'] == expected_first_texkeys

    expected_second_texkey = 'Carl:2017abc'
    expected_second_texkeys = [
            'Carl:2017abc'
        ]

    pid = PersistentIdentifier.get('tex', expected_second_texkey)

    assert pid.pid_value == 'Carl:2017abc'
    assert pid.pid_type == 'tex'
    assert second_obj.data['texkeys'] == expected_second_texkeys


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
def test_migration_texkeys(mock_random_letters, app):
    control_number = '613135'
    old_texkey = 'Spergel:2003cb'

    pid = PersistentIdentifier.get('lit', control_number)
    assert [record.pid_value for record in PersistentIdentifier.query.filter_by(
        object_uuid=str(pid.object_uuid),
        pid_type='tex',
        pid_value=old_texkey
    ).all()]
