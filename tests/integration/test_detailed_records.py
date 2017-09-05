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

from invenio_accounts.testutils import login_user_via_session
from invenio_records.models import RecordMetadata

from inspirehep.modules.migrator.models import InspireProdRecords


def test_all_records_were_loaded(app):
    records = [record.json for record in RecordMetadata.query.all()]

    expected = 43
    result = len(records)

    assert expected == result


def test_all_records_are_valid(app):
    invalid = InspireProdRecords.query.filter(InspireProdRecords.valid is False).values(InspireProdRecords.recid)
    recids = [el[0] for el in invalid]

    assert recids == []


def test_all_records_are_there(app_client):
    # Use superadmin user to ensure we can visit all records
    login_user_via_session(app_client, email='admin@inspirehep.net')

    failed = []
    for record in [record.json for record in RecordMetadata.query.all()]:
        try:
            absolute_url = record['self']['$ref']
            relative_url = absolute_url.partition('api')[2]
            response = app_client.get(relative_url)

            assert response.status_code == 200
        except Exception:
            failed.append(record['control_number'])

    assert failed == []
