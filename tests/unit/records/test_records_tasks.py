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

from flask import current_app
from mock import patch

from inspirehep.modules.records.tasks import update_links, batch_reindex


def test_update_links():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'record': {
                '$ref': 'http://localhost:5000/record/1',
            },
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'record': {
                '$ref': 'http://localhost:5000/record/2',
            },
        }


def test_update_links_handles_nested_paths():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foo.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {
                    '$ref': 'http://localhost:5000/record/1',
                },
            },
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {
                    '$ref': 'http://localhost:5000/record/2',
                },
            },
        }


def test_update_links_handles_lists():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foos.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foos': [
                {'record': {'$ref': 'http://localhost:5000/record/1'}},
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
            ],
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foos': [
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
            ],
        }


def test_update_links_ignores_non_whitelisted_paths():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foo.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            },
            'bar': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            }
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {'$ref': 'http://localhost:5000/record/2'},
            },
            'bar': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            }
        }


def record_generator(uuid):
    record = {
        '$schema': 'http://localhost:5000/schemas/record/hep.json',
    }
    if uuid.endswith("_deleted"):
        record['deleted'] = True
    return record


def mocked_bulk(es, records, **kwargs):
    count = 0
    for record in records:
        count += 1
    return (count, 0)


@patch('inspirehep.modules.records.tasks.InspireRecord.get_record', side_effect=record_generator)
@patch('inspirehep.modules.records.tasks.create_index_op', side_effect=None)
@patch('inspirehep.modules.records.tasks.bulk', side_effect=mocked_bulk)
def test_record_task_batch_logic_check_reindex_records_count(get_record, create_index_op, mocked_bulk):
    records = ['000', 'aaa', 'bbb', 'ccc']
    output = batch_reindex(uuids=records)
    assert create_index_op.call_count == 4
    assert output['success'] == 4
    assert output['failures'] == []


@patch('inspirehep.modules.records.tasks.InspireRecord.get_record', side_effect=record_generator)
@patch('inspirehep.modules.records.tasks.create_index_op', side_effect=None)
@patch('inspirehep.modules.records.tasks.bulk', side_effect=mocked_bulk)
def test_record_task_batch_logic_reindex_skips_deleted_records(get_record, create_index_op, mocked_bulk):
    records = ['000', 'aaa_deleted', 'bbb', 'ccc']
    output = batch_reindex(uuids=records)
    assert create_index_op.call_count == 3
    assert output['success'] == 3
    assert output['failures'] == []


@patch('inspirehep.modules.records.tasks.InspireRecord.get_record', side_effect=record_generator)
@patch('inspirehep.modules.records.tasks.create_index_op', side_effect=None)
@patch('inspirehep.modules.records.tasks.bulk', side_effect=mocked_bulk)
def test_record_task_batch_logic_reindex_only_deleted_records(get_record, create_index_op, mocked_bulk):
    records = ['000_deleted', 'aaa_deleted', 'bbb_deleted', 'ccc_deleted']
    output = batch_reindex(uuids=records)
    assert create_index_op.call_count == 0
    assert output['success'] == 0
    assert output['failures'] == []


@patch('inspirehep.modules.records.tasks.InspireRecord.get_record', side_effect=record_generator)
@patch('inspirehep.modules.records.tasks.create_index_op', side_effect=None)
@patch('inspirehep.modules.records.tasks.bulk', side_effect=mocked_bulk)
def test_record_task_batch_logic_nothing_to_reindex(get_record, create_index_op, mocked_bulk):
    records = []
    output = batch_reindex(uuids=records)
    assert create_index_op.call_count == 0
    assert output['success'] == 0
    assert output['failures'] == []
