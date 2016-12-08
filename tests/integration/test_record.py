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
import time
from elasticsearch import RequestError

from dojson.contrib.marc21.utils import create_record
from invenio_db import db
from invenio_search import current_search_client as es
from invenio_pidstore.models import PersistentIdentifier, Redirect

from inspirehep.dojson.hep import hep
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.migrator.tasks.records import record_upsert
from inspirehep.utils.record import get_value
from inspirehep.utils.record_getter import get_db_record, get_es_records


@pytest.fixture(scope='function')
def record_already_deleted_in_marcxml(app):
    snippet = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
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
            record_upsert(json_record)
        db.session.commit()

    yield

    with app.app_context():
        _delete_record_from_everywhere('lit', 222)


@pytest.fixture(scope='function')
def record_not_yet_deleted(app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 333,
        'self': {
            '$ref': 'http://localhost:5000/api/literature/333'
        },
    }

    with app.app_context():
        with db.session.begin_nested():
            record_upsert(record)
        db.session.commit()

    yield

    with app.app_context():
        _delete_record_from_everywhere('lit', 333)


@pytest.fixture(scope='function')
def records_already_merged_in_marcxml(app):
    snippet_merged = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '  <datafield tag="981" ind1=" " ind2=" ">'
        '    <subfield code="a">222</subfield>'
        '  </datafield>'
        '</record>'
    )

    snippet_deleted = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <datafield tag="970" ind1=" " ind2=" ">'
        '    <subfield code="d">111</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record_merged = hep.do(create_record(snippet_merged))
        json_record_merged['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        json_record_deleted = hep.do(create_record(snippet_deleted))
        json_record_deleted['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        merged_id = record_upsert(json_record_merged).id
        db.session.commit()
        record_upsert(json_record_deleted)
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records_from_everywhere(
            'lit',
            111,
            222,
            merged_id
        )


@pytest.fixture(scope='function')
def records_not_merged_in_marcxml(app):
    snippet_merged = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '  <datafield tag="981" ind1=" " ind2=" ">'
        '    <subfield code="a">222</subfield>'
        '  </datafield>'
        '</record>'
    )

    snippet_deleted = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '  <datafield tag="981" ind1=" " ind2=" ">'
        '    <subfield code="a">222</subfield>'
        '  </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record_merged = hep.do(create_record(snippet_merged))
        json_record_merged['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        json_record_deleted = hep.do(create_record(snippet_deleted))
        json_record_deleted['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            merged_id = record_upsert(json_record_merged).id
            deleted_id = record_upsert(json_record_deleted).id
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records_from_everywhere(
            'lit',
            111,
            222,
            merged_id,
            deleted_id
        )


@pytest.fixture(scope='function')
def records_to_be_merged(app):
    with app.app_context():

        record = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            'control_number': 111,
            'self': {
                '$ref': 'http://localhost:5000/api/literature/111'
            },
        }

        record_to_be_merged = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            'control_number': 222,
            'self': {
                '$ref': 'http://localhost:5000/api/literature/222'
            },
        }

        pointed_record = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            'control_number': 333,
            'accelerator_experiments': [
                {
                    'record': {
                        '$ref': 'http://localhost:5000/api/literature/222',
                    },
                },
            ],
        }

        with db.session.begin_nested():
            merged_id = record_upsert(record).id
            deleted_id = record_upsert(record_to_be_merged).id
            record_upsert(pointed_record)
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records_from_everywhere('lit', 111, 222, merged_id, deleted_id)
        _delete_record_from_everywhere('lit', 333)


def _delete_record_from_everywhere(pid_type, record_control_number):
    record = get_db_record(pid_type, record_control_number)

    record._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, record_control_number)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def _delete_merged_records_from_everywhere(pid_type,
                                           merged_record_control_number,
                                           deleted_record_control_number,
                                           merged_id,
                                           deleted_id=None):
    try:
        merged_id._delete(force=True)
        deleted_id._delete(force=True)
    except AttributeError:
        InspireRecord.get_record(merged_id)._delete(force=True)
        if deleted_id:
            InspireRecord.get_record(deleted_id)._delete(force=True)

    merged_pid = PersistentIdentifier.get(pid_type, merged_record_control_number)
    deleted_pid = PersistentIdentifier.get(pid_type, deleted_record_control_number)
    Redirect.query.filter(Redirect.id == deleted_pid.object_uuid).delete()
    db.session.delete(merged_pid)
    db.session.delete(deleted_pid)
    db.session.commit()


def test_deleted_record_stays_deleted(app, record_already_deleted_in_marcxml):
    with app.test_client() as client:
        assert client.get('/api/literature/222').status_code == 410


def test_record_can_be_deleted(app, record_not_yet_deleted):
    with app.test_client() as client:
        assert client.get('/api/literature/333').status_code == 200

    rec = get_db_record('lit', 333)
    rec.delete()
    db.session.commit()

    with app.test_client() as client:
        assert client.get('/api/literature/333').status_code == 410


def test_merged_records_stay_merged(app, records_already_merged_in_marcxml):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 301


def test_records_can_be_merged(app, records_not_merged_in_marcxml):
    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 200

    record = get_db_record('lit', 222)
    other = get_db_record('lit', 111)
    record.merge(other)
    db.session.commit()

    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 301


def test_records_propagate_links_when_merged(app, records_to_be_merged):
    record = get_db_record('lit', 222)
    other = get_db_record('lit', 111)

    record.merge(other)
    db.session.commit()
    es.indices.refresh('records-hep')

    rec_updated = get_db_record('lit', 333)
    result = get_value(rec_updated, 'accelerator_experiments[0].record.$ref')
    expected = 'http://localhost:5000/api/literature/111'
    assert expected == result


def test_get_es_records_raises_on_empty_list(app):
    with app.app_context():
        with pytest.raises(RequestError):
            get_es_records('lit', [])
