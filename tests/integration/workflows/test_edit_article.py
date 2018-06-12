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

"""Tests for workflow views."""

from factories.db.invenio_records import TestRecordMetadata


def test_view_edit_lit(api_client):
    factory = TestRecordMetadata.create_from_kwargs(json={})
    control_number =  factory.record_metadata.json['control_number']
    endpoint_url = "/callback/workflows/edit_lit/{}".format(control_number)

    response = api_client.get(endpoint_url)
    assert response.status_code == 302
    assert "/editor/holdingpen/" in response.data


def test_view_edit_lit_wrong_recid(api_client):
    response = api_client.get("/callback/workflows/edit_lit/1")
    assert response.status_code == 500
