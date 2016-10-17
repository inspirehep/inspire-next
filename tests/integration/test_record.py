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
from invenio_pidstore.models import PersistentIdentifier, Redirect
from invenio_search import current_search_client as es
from inspirehep.modules.search.api import LiteratureSearch

from inspirehep.dojson.hep import hep
from inspirehep.modules.migrator.tasks.records import record_upsert
from inspirehep.utils.record_getter import get_db_record, get_es_record


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


@pytest.fixture(scope='function')
def records_already_merged_in_marcxml(app):
    snippet_merged = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <controlfield tag="005">20160922232729.0</controlfield>'
        ' <datafield tag="024" ind1="7" ind2=" ">'
        '   <subfield code="2">DOI</subfield>'
        '   <subfield code="a">10.11588/heidok.00021652</subfield>'
        ' </datafield>'
        ' <datafield tag="100" ind1=" " ind2=" ">'
        '   <subfield code="a">Humbert, Pascal</subfield>'
        '   <subfield code="u">Inst. Appl. Math., Heidelberg</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">HEP</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">THESIS</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">CORE</subfield>'
        ' </datafield>'
        ' <datafield tag="981" ind1=" " ind2=" ">'
        '   <subfield code="a">222</subfield>'
        ' </datafield>'
        '</record>'
    )

    snippet_deleted = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <controlfield tag="005">20160914115512.0</controlfield>'
        '  <datafield tag="100" ind1=" " ind2=" ">'
        '    <subfield code="a">Humbert, Pascal</subfield>'
        '  </datafield>'
        ' <datafield tag="970" ind1=" " ind2=" ">'
        '   <subfield code="d">111</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">THESIS</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">CORE</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="c">DELETED</subfield>'
        ' </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record_merged = hep.do(create_record(snippet_merged))
        json_record_merged['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        json_record_deleted = hep.do(create_record(snippet_deleted))
        json_record_deleted['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            record_merged = record_upsert(json_record_merged)
            record_deleted = record_upsert(json_record_deleted)
            if record_deleted:
                if record_merged:
                    r = RecordIndexer()
                    r.index(record_merged)
                    r.index(record_deleted)
                    es.indices.refresh('records-hep')
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records_from_everywhere('literature', 111, 222)


@pytest.fixture(scope='function')
def records_not_merged_in_marcxml(app):
    snippet_merged = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <controlfield tag="005">20160922232729.0</controlfield>'
        ' <datafield tag="024" ind1="7" ind2=" ">'
        '   <subfield code="2">DOI</subfield>'
        '   <subfield code="a">10.11588/heidok.00021652</subfield>'
        ' </datafield>'
        ' <datafield tag="100" ind1=" " ind2=" ">'
        '   <subfield code="a">Humbert, Pascal</subfield>'
        '   <subfield code="u">Inst. Appl. Math., Heidelberg</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">HEP</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">THESIS</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">CORE</subfield>'
        ' </datafield>'
        ' <datafield tag="981" ind1=" " ind2=" ">'
        '   <subfield code="a">222</subfield>'
        ' </datafield>'
        '</record>'
    )

    snippet_deleted = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <controlfield tag="005">20160922232729.0</controlfield>'
        ' <datafield tag="024" ind1="7" ind2=" ">'
        '   <subfield code="2">DOI</subfield>'
        '   <subfield code="a">10.11588/heidok.00021652</subfield>'
        ' </datafield>'
        ' <datafield tag="100" ind1=" " ind2=" ">'
        '   <subfield code="a">Humbert, Pascal</subfield>'
        '   <subfield code="u">Inst. Appl. Math., Heidelberg</subfield>'
        ' </datafield>'
        ' <datafield tag="701" ind1=" " ind2=" ">'
        '   <subfield code="a">Lindner, Manfred</subfield>'
        ' </datafield>'
        ' <datafield tag="856" ind1="4" ind2=" ">'
        '   <subfield code="u">http://www.ub.uni-heidelberg.de/archiv/21652</subfield>'
        '   <subfield code="y">U. Heidelberg</subfield>'
        ' </datafield>'
        ' <datafield tag="909" ind1="C" ind2="O">'
        '   <subfield code="o">oai:inspirehep.net:222</subfield>'
        '   <subfield code="p">INSPIRE:HEP</subfield>'
        ' </datafield>'
        ' <datafield tag="980" ind1=" " ind2=" ">'
        '   <subfield code="a">HEP</subfield>'
        ' </datafield>'
        ' <datafield tag="981" ind1=" " ind2=" ">'
        '   <subfield code="a">222</subfield>'
        ' </datafield>'
        '</record>'
    )

    with app.app_context():
        json_record_merged = hep.do(create_record(snippet_merged))
        json_record_merged['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        json_record_deleted = hep.do(create_record(snippet_deleted))
        json_record_deleted['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

        with db.session.begin_nested():
            record_merged = record_upsert(json_record_merged)
            record_deleted = record_upsert(json_record_deleted)
            if record_deleted:
                if record_merged:
                    r = RecordIndexer()
                    r.index(record_merged)
                    r.index(record_deleted)
                    es.indices.refresh('records-hep')
        db.session.commit()

    yield

    with app.app_context():
        _delete_merged_records_from_everywhere('literature', 111, 222)


def _delete_record_from_everywhere(pid_type, record_control_number):
    record = get_db_record(pid_type, record_control_number)

    ri = RecordIndexer()
    ri.delete(record)
    record.delete(force=True)

    pid = PersistentIdentifier.get(pid_type, record_control_number)
    PersistentIdentifier.delete(pid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


def _delete_merged_records_from_everywhere(pid_type, merged_record_control_number, deleted_record_control_number):
    def _delete_es_records(index, doc_type, merged_uuid, deleted_uuid):
        es.delete(index=index, doc_type=doc_type, id=merged_uuid)
        es.delete(index=index, doc_type=doc_type, id=deleted_uuid)

    control_num_str = 'control_number:{}'.format(deleted_record_control_number)
    es_deleted_record = LiteratureSearch().query_from_iq(control_num_str).execute()
    deleted_object_uuid = es_deleted_record[0].meta.id

    deleted = PersistentIdentifier.get(pid_type, deleted_record_control_number)
    merged = PersistentIdentifier.get(pid_type, merged_record_control_number)

    _delete_es_records('records-hep', 'hep', merged.object_uuid, deleted_object_uuid)

    Redirect.query.filter(Redirect.id == deleted.object_uuid).delete()
    PersistentIdentifier.delete(merged)
    PersistentIdentifier.delete(deleted)

    db.session.delete(merged)
    db.session.delete(deleted)

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

    record = get_db_record('literature', 222)
    record['deleted'] = True
    record['new_record'] = {'$ref': 'http://localhost:5000/api/record/111'}
    record.commit()
    if record:
        ri = RecordIndexer()
        ri.index(record)
    db.session.commit()

    with app.test_client() as client:
        assert client.get('/api/literature/111').status_code == 200
        assert client.get('/api/literature/222').status_code == 301
