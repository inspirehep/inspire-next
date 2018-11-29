# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from uuid import uuid4

from inspirehep.modules.records.tasks import batch_reindex
from inspirehep.utils.record_getter import get_es_record, RecordGetterError


def test_batch_reindex_no_records(
    app,
    celery_app_with_context,
    celery_session_worker
):
    task = batch_reindex.apply_async(kwargs={'uuids': [str(uuid4())]})

    result = task.get(timeout=10)
    expected = {'failures': [], 'success': 0}

    assert result == expected


def test_batch_reindex_one_record(
    app,
    create_records,
    celery_app_with_context,
    celery_session_worker
):
    records = create_records(n=1)
    uuid = str(records[0].id)

    task = batch_reindex.apply_async(kwargs={'uuids': [uuid]})

    result = task.get(timeout=10)
    expected = {'failures': [], 'success': 1}
    assert result == expected

    control_number = records[0].json['control_number']
    assert get_es_record('lit', control_number)


def test_batch_reindex_one_deleted_record(
    app,
    create_records,
    celery_app_with_context,
    celery_session_worker
):
    records = create_records(n=1, additional_props={'deleted': True})
    uuid = str(records[0].id)

    task = batch_reindex.apply_async(kwargs={'uuids': [uuid]})

    result = task.get(timeout=10)
    expected = {'failures': [], 'success': 0}
    assert result == expected

    control_number = records[0].json['control_number']

    with pytest.raises(RecordGetterError):
        get_es_record('lit', control_number)


def test_batch_reindex_two_records(
    app,
    create_records,
    celery_app_with_context,
    celery_session_worker
):
    records = create_records(n=2)
    uuids = [str(r.id) for r in records]

    task = batch_reindex.apply_async(kwargs={'uuids': uuids})

    result = task.get(timeout=10)
    expected = {'failures': [], 'success': 2}
    assert result == expected

    control_number = records[0].json['control_number']
    assert get_es_record('lit', control_number)

    control_number = records[1].json['control_number']
    assert get_es_record('lit', control_number)


@pytest.mark.xfail
def test_batch_reindex_two_records_and_one_fails(
    app,
    create_records,
    celery_app_with_context,
    celery_session_worker
):
    records = create_records(n=2)
    uuids = [str(r.id) for r in records]

    failing_record = create_records(n=1, additional_props={'broken': True})[0]
    uuids.append(failing_record.id)

    task = batch_reindex.apply_async(kwargs={'uuids': uuids})

    result = task.get(timeout=10)
    expected = {'failures': [failing_record.id], 'success': 2}
    assert result == expected

    control_number = records[0].json['control_number']
    assert get_es_record('lit', control_number)

    control_number = failing_record.json['control_number']
    with pytest.raises(RecordGetterError):
        get_es_record('lit', control_number)


def test_batch_reindex_one_records_and_skips_one_deleted(
    app,
    create_records,
    celery_app_with_context,
    celery_session_worker
):
    records = create_records(n=1)
    uuids = [str(r.id) for r in records]

    failing_record = create_records(n=1, additional_props={'deleted': True})[0]
    uuids.append(failing_record.id)

    task = batch_reindex.apply_async(kwargs={'uuids': uuids})

    result = task.get(timeout=10)
    expected = {'failures': [], 'success': 1}
    assert result == expected

    control_number = records[0].json['control_number']
    assert get_es_record('lit', control_number)

    control_number = failing_record.json['control_number']
    with pytest.raises(RecordGetterError):
        get_es_record('lit', control_number)
