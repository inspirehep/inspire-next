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
from elasticsearch import RequestError

from dojson.contrib.marc21.utils import create_record
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, Redirect

from inspirehep.dojson.hep import hep
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.migrator.tasks.records import record_upsert
from inspirehep.utils.record_getter import get_db_record, get_es_records


def _delete_record(pid_type, pid_value):
    get_db_record(pid_type, pid_value)._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, pid_value)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def _delete_merged_records(pid_type, merged_pid_value, deleted_pid_value, merged_uuid, deleted_uuid):
    InspireRecord.get_record(merged_uuid)._delete(force=True)
    InspireRecord.get_record(deleted_uuid)._delete(force=True)

    merged_pid = PersistentIdentifier.get(pid_type, merged_pid_value)
    deleted_pid = PersistentIdentifier.get(pid_type, deleted_pid_value)

    Redirect.query.filter(Redirect.id == deleted_pid.object_uuid).delete()

    db.session.delete(merged_pid)
    db.session.delete(deleted_pid)

    db.session.commit()


@pytest.fixture(scope='function')
def deleted_record(app):
    snippet = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        record = hep.do(create_record(snippet))
        record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            record_upsert(record)
        db.session.commit()

    yield

    with app.app_context():
        _delete_record('lit', 111)


@pytest.fixture(scope='function')
def not_yet_deleted_record(app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        }
    }

    with app.app_context():
        with db.session.begin_nested():
            record_upsert(record)
        db.session.commit()

    yield

    with app.app_context():
        _delete_record('lit', 111)


@pytest.fixture(scope='function')
def merged_records(app):
    merged_snippet = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="981" ind1=" " ind2=" ">'
        '    <subfield code="a">222</subfield>'
        '  </datafield>'
        '</record>'
    )

    deleted_snippet = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <datafield tag="970" ind1=" " ind2=" ">'
        '    <subfield code="d">111</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        merged_record = hep.do(create_record(merged_snippet))
        merged_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        deleted_record = hep.do(create_record(deleted_snippet))
        deleted_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            merged_uuid = record_upsert(merged_record).id
            deleted_uuid = record_upsert(deleted_record).id
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records('lit', 111, 222, merged_uuid, deleted_uuid)


@pytest.fixture(scope='function')
def not_yet_merged_records(app):
    merged_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'self': {
            '$ref': 'http://localhost:5000/api/literature/111',
        },
    }

    deleted_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 222,
        'self': {
            '$ref': 'http://localhost:5000/api/literature/222',
        },
    }

    with app.app_context():
        with db.session.begin_nested():
            merged_uuid = record_upsert(merged_record).id
            deleted_uuid = record_upsert(deleted_record).id
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records('lit', 111, 222, merged_uuid, deleted_uuid)


def test_deleted_record_stays_deleted(app, deleted_record):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 410


def test_record_can_be_deleted(app, not_yet_deleted_record):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200

    record = get_db_record('lit', 111)
    record.delete()
    db.session.commit()

    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 410


def test_merged_records_stay_merged(app, merged_records):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 301


def test_records_can_be_merged(app, not_yet_merged_records):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 200

    merged_record = get_db_record('lit', 111)
    deleted_record = get_db_record('lit', 222)
    deleted_record['deleted'] = True
    deleted_record['new_record'] = {'$ref': 'http://localhost:5000/api/record/111'}
    deleted_record.merge(merged_record)
    db.session.commit()

    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 301


def test_get_es_records_raises_on_empty_list(app):
    with app.app_context():
        with pytest.raises(RequestError):
            get_es_records('lit', [])
