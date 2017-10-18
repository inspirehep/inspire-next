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
from StringIO import StringIO

# from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.api import InspireRecord


@pytest.fixture
def json():
    return {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": [
            "Literature"
        ],
        "document_type": ["article"],
        "titles": [
            {
                "title": "foo"
            }
        ],
        "control_number": 1,
        "documents": [
        ],
        "figures": [
        ]
    }


def test_attach_file_to_documents(app, json):
    json['documents'].append({"key": "my_doc"})
    rec = InspireRecord.create(json)

    file_to_attach = StringIO()
    new_key = rec.attach_file('my_doc', file_to_attach)

    expected_url = '/api/files/{bucket}/{key}'.format(
        bucket=rec.files[new_key].bucket_id,
        key=new_key
    )

    assert new_key == '{}_my_doc'.format(rec['control_number'])
    assert rec['documents'][0]['key'] == new_key
    assert rec['documents'][0]['url'] == expected_url
    assert new_key in rec.files


def test_attach_file_to_figure(app, json):
    json['figures'].append({"key": "picture1.png"})
    rec = InspireRecord.create(json)

    file_to_attach = StringIO()
    new_key = rec.attach_file('picture1.png', file_to_attach)

    expected_url = '/api/files/{bucket}/{key}'.format(
        bucket=rec.files[new_key].bucket_id,
        key=new_key
    )

    assert new_key == '{}_picture1.png'.format(rec['control_number'])
    assert rec['figures'][0]['key'] == new_key
    assert rec['figures'][0]['url'] == expected_url
    assert new_key in rec.files


def test_attach_file_key_not_in_documents_and_figures(app, json):
    rec = InspireRecord.create(json)
    file_to_attach = StringIO()
    assert rec.attach_file('my_file', file_to_attach) is None
