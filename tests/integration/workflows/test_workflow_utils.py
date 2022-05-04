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

from time import sleep

from invenio_db import db

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import (
    insert_wf_record_source,
    read_wf_record_source,
    timeout_with_config,
    TimeoutError
)
from utils import override_config


@pytest.fixture()
def dummy_record(workflow_app):
    record = InspireRecord.create({
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['thesis'],
        'titles': [{'title': 'foo'}],
    })

    yield record

    record._delete(force=True)


def test_wf_record_source_read_and_write(dummy_record):
    insert_wf_record_source(
        json=dummy_record,
        record_uuid=dummy_record.id,
        source='arxiv'
    )
    db.session.commit()

    retrieved_root = read_wf_record_source(
        record_uuid=dummy_record.id, source='arxiv')

    assert dummy_record == retrieved_root.json
    assert 'arxiv' == retrieved_root.source


def test_wf_record_with_desy_source_read_and_write(dummy_record):
    insert_wf_record_source(
        json=dummy_record,
        record_uuid=dummy_record.id,
        source='desy'
    )
    db.session.commit()

    retrieved_root = read_wf_record_source(
        record_uuid=dummy_record.id, source='desy')

    assert dummy_record == retrieved_root.json
    assert 'publisher' == retrieved_root.source


def test_wf_record_with_submitter_source_read_and_write(dummy_record):
    insert_wf_record_source(
        json=dummy_record,
        record_uuid=dummy_record.id,
        source='submitter'
    )
    db.session.commit()
    retrieved_root = read_wf_record_source(
        record_uuid=dummy_record.id, source='submitter')

    assert dummy_record == retrieved_root.json
    assert 'submitter' == retrieved_root.source


def test_test_wf_record_source_update(dummy_record):
    insert_wf_record_source(
        json=dummy_record,
        record_uuid=dummy_record.id,
        source='arxiv'
    )
    db.session.commit()

    # update the content
    dummy_record['document_type'] = ['article']
    insert_wf_record_source(
        json=dummy_record,
        record_uuid=dummy_record.id,
        source='arxiv'
    )
    db.session.commit()

    retrieved_root = read_wf_record_source(record_uuid=dummy_record.id, source='arxiv')
    assert dummy_record == retrieved_root.json


def test_empty_root(dummy_record):
    record_uuid = dummy_record.id
    retrieved_root = read_wf_record_source(record_uuid=record_uuid, source='publisher')
    assert retrieved_root is None


def test_wf_record_source_does_not_match_db_content(dummy_record):
    dummy_record.commit()
    db.session.commit()  # write in the db
    retrieved_root = read_wf_record_source(record_uuid=dummy_record.id, source='publisher')
    assert retrieved_root is None


# def test_read_all_wf_record_sources(dummy_record):
#     insert_wf_record_source(
#         json=dummy_record,
#         record_uuid=dummy_record.id,
#         source='arxiv'
#     )

#     insert_wf_record_source(
#         json=dummy_record,
#         record_uuid=dummy_record.id,
#         source='publisher'
#     )
#     db.session.commit()

#     entries = read_all_wf_record_sources(dummy_record.id)
#     assert len(entries) == 2


def test_timeout_with_config(workflow_app):
    @timeout_with_config('MAX_NAP_TIME')
    def long_nap():
        sleep(5)

    with override_config(MAX_NAP_TIME=1), pytest.raises(TimeoutError):
        long_nap()
