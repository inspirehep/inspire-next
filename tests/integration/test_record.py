# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import pytest

from dojson.contrib.marc21.utils import create_record
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es

from inspirehep.dojson.hep import hep
from inspirehep.modules.migrator.tasks.records import record_upsert
from inspirehep.utils.record_getter import get_db_record


@pytest.fixture(scope='function')
def record_already_deleted_in_marcxml(app):
    snippet = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <controlfield tag="005">20160913214552.0</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record = hep.do(create_record(snippet))
        json_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            record = record_upsert(json_record)
            if record:
                r = RecordIndexer()
                r.index(record)

        db.session.commit()

    yield

    with app.app_context():
        _delete_record_from_everywhere('literature', 222)


@pytest.fixture(scope='function')
def record_not_yet_deleted(app):
    snippet = (
        '<record>'
        '  <controlfield tag="001">333</controlfield>'
        '  <controlfield tag="005">20160913214552.0</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record = hep.do(create_record(snippet))
        json_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            record = record_upsert(json_record)
            if record:
                ri = RecordIndexer()
                ri.index(record)

        db.session.commit()

    yield

    with app.app_context():
        _delete_record_from_everywhere('literature', 333)


def _delete_record_from_everywhere(collection, record_control_number):
    record = get_db_record(collection, record_control_number)

    ri = RecordIndexer()
    ri.delete(record)
    record.delete(force=True)

    pid = PersistentIdentifier.get(collection, record_control_number)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def test_deleted_record_stays_deleted(app, record_already_deleted_in_marcxml):
    with app.test_client() as client:
        assert client.get('/api/literature/222').status_code == 410


def test_record_can_be_deleted(app, record_not_yet_deleted):
    with app.test_client() as client:
        assert client.get('/api/literature/333').status_code == 200

        record = get_db_record('literature', 333)
        record['deleted'] = True
        record.commit()
        if record:
            ri = RecordIndexer()
            ri.index(record)
        db.session.commit()

        assert client.get('/api/literature/333').status_code == 410
