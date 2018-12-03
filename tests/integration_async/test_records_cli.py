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

import json
import os

import pytest

from mock import patch

from inspirehep.modules.records.api import RecordMetadata
from inspirehep.modules.records.cli import (
    get_query_records_to_index,
    simpleindex,
)


def test_simpleindex_no_records_to_index(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert not result.exception
    assert '0 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def test_simpleindex_one_record_ok(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    create_records()
    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert '1 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def test_simpleindex_does_not_index_deleted_record(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    create_records(additional_props={'deleted': True})
    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert '0 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def test_simpleindex_does_fails_invalid_record(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
    tmpdir,
):
    log_path = str(tmpdir)
    broken_field = {
        '_desy_bookkeeping': {
            'date': '"2013-01-14_final'
        }
    }
    with patch('inspirehep.modules.records.receivers.RecordIndexer'):
        create_records(additional_props=broken_field)

    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', '', '-l', log_path],
    )
    assert result.exit_code == 0
    assert '0 succeeded' in result.output_bytes
    assert '1 failed' in result.output_bytes
    assert '0 batches errored' in result.output_bytes

    with open(os.path.join(log_path, 'records_index_failures.log')) as log_file:
        content = json.loads(log_file.read())
        assert len(content) == 1
        assert content[0]['id']  # the task failed
        assert 'Invalid format: ""2013-01-14_final"' in content[0]['error']['caused_by']['reason']


def test_simpleindex_does_fails_invalid_field(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
    tmpdir,
):
    log_path = str(tmpdir)
    invalid_field = {
        'preprint_date': 'i am not a date'
    }

    with patch('inspirehep.modules.records.receivers.RecordIndexer'):
        create_records(additional_props=invalid_field)

    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', '', '-l', log_path],
    )
    assert result.exit_code == 0
    assert '0 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes
    assert '1 batches errored' in result.output_bytes

    with open(os.path.join(log_path, 'records_index_errors.log')) as log_file:
        content = json.loads(log_file.read())
        assert len(content) == 1
        assert content[0]['ids']  # the task failed
        assert 'i am not a date' in content[0]['error']


@pytest.mark.xfail
def test_simpleindex_does_one_fails_and_two_ok(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
    tmpdir,
):
    log_path = str(tmpdir)
    invalid_field = {
        'preprint_date': 'i am not a date'
    }

    create_records(n=2)
    with patch('inspirehep.modules.records.receivers.RecordIndexer'):
        create_records(additional_props=invalid_field)

    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '--queue-name', '', '-l', log_path],
    )
    # this fails because right now the whole batch fails
    assert result.exit_code == 0
    assert '2 succeeded' in result.output_bytes
    assert '1 failed' in result.output_bytes
    assert '0 batches errored' in result.output_bytes

    with open(os.path.join(log_path, 'records_index_errors.log')) as log_file:
        content = json.loads(log_file.read())
        assert len(content) == 1
        assert content[0]['ids']  # the task failed
        assert 'i am not a date' in content[0]['error']


def test_simpleindex_indexes_correct_pidtype(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    create_records()
    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'aut', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert '0 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def test_simpleindex_using_multiple_batches(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    create_records(n=5)
    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'lit', '-s', '1', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert '5 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def test_simpleindex_only_authors(
    app_cli,
    celery_app_with_context,
    celery_session_worker,
    create_records,
):
    create_records(n=1)
    create_records(n=2, pid_type='aut')

    result = app_cli.invoke(
        simpleindex,
        ['--yes-i-know', '-t', 'aut', '-s', '1', '--queue-name', ''],
    )
    assert result.exit_code == 0
    assert '2 succeeded' in result.output_bytes
    assert '0 failed' in result.output_bytes


def _get_deleted_records_by_uuids(uuids):
    records = RecordMetadata.query.filter(RecordMetadata.id.in_(uuids)).all()
    return [r for r in records if r.json.get('deleted')]


def test_get_query_records_to_index_ok_different_pids(
    app,
    create_records
):
    create_records(n=2)
    create_records(n=2, pid_type='job')
    create_records(n=2, pid_type='ins')

    pids = ['lit', 'con', 'exp', 'jou', 'aut', 'job', 'ins']
    query = get_query_records_to_index(pids)

    expected_count = 6
    result_count = query.count()
    assert result_count == expected_count

    uuids = [str(item[0]) for item in query.all()]
    deleted_records = _get_deleted_records_by_uuids(uuids)
    assert deleted_records == []


def test_get_query_records_to_index_only_lit(app, create_records):
    create_records(n=2)
    create_records(n=2, pid_type='aut')

    pids = ['lit']
    query = get_query_records_to_index(pids)

    expected_count = 2
    result_count = query.count()
    assert result_count == expected_count

    uuids = [str(item[0]) for item in query.all()]
    deleted_records = _get_deleted_records_by_uuids(uuids)
    assert deleted_records == []


def test_get_query_records_to_index_only_lit_adding_record(
    app,
    create_records
):
    create_records(additional_props={'deleted': True})

    pids = ['lit']
    query = get_query_records_to_index(pids)

    expected_count = 0  # does not take deleted record
    result_count = query.count()
    assert result_count == expected_count


def test_get_query_records_to_index_only_lit_adding_record_deleted(
    app,
    create_records,
):
    create_records()
    create_records(additional_props={'deleted': True})

    pids = ['lit']
    query = get_query_records_to_index(pids)

    expected_count = 1
    result_count = query.count()
    assert result_count == expected_count
