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

from invenio_db import db

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import (
    store_root_json,
    retrieve_root_json,
)


@pytest.fixture()
def dummy_record(workflow_app):
    record = InspireRecord.create({
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "titles": [{
            "title": "foo"
        }],
        "document_type": ["thesis"]
    })
    yield record
    record._delete(force=True)


def test_store_and_retrieve_of_root_json(dummy_record):
    record_uuid = dummy_record.id
    original_root = {"title": "baz"}
    store_root_json(record_uuid=record_uuid, source='arXiv', json=original_root)
    db.session.commit()
    retrieved_root = retrieve_root_json(record_uuid=record_uuid, source='arXiv')

    assert original_root == retrieved_root

    updated_root = {"title": "bar"}
    store_root_json(record_uuid=record_uuid, source='arXiv', json=updated_root)
    db.session.commit()
    retrieved_root = retrieve_root_json(record_uuid=record_uuid, source='arXiv')

    assert updated_root == retrieved_root

    retrieved_root = retrieve_root_json(record_uuid=record_uuid, source='Elsevier')
    expected_root = {}

    assert expected_root == {}
