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

import copy
import pytest
import StringIO
from mock import patch, mock_open

from invenio_db import db
from invenio_pidstore.models import (
    PersistentIdentifier,
    Redirect,
    RecordIdentifier,
)
from invenio_search import current_search_client as es

from inspire_dojson import marcxml2record
from inspire_utils.record import get_value
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.tasks import merge_merged_records, update_refs
from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.utils.record_getter import get_db_record, get_es_records

from utils import _delete_record


def _delete_merged_records(pid_type, merged_pid_value, deleted_pid_value, merged_uuid, deleted_uuid):
    InspireRecord.get_record(merged_uuid)._delete(force=True)
    InspireRecord.get_record(deleted_uuid)._delete(force=True)

    merged_pid = PersistentIdentifier.get(pid_type, merged_pid_value)
    deleted_pid = PersistentIdentifier.get(pid_type, deleted_pid_value)
    merged_recid = RecordIdentifier.query.filter_by(
        recid=merged_pid_value,
    ).one_or_none()
    deleted_recid = RecordIdentifier.query.filter_by(
        recid=deleted_pid_value,
    ).one_or_none()

    Redirect.query.filter(Redirect.id == deleted_pid.object_uuid).delete()

    db.session.delete(merged_pid)
    db.session.delete(deleted_pid)
    if merged_recid:
        db.session.delete(merged_recid)
    if deleted_recid:
        db.session.delete(deleted_recid)

    db.session.commit()


@pytest.fixture(scope='function')
def deleted_record(app):
    snippet = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">deleted</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )

    record = marcxml2record(snippet)
    record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

    with db.session.begin_nested():
        record_insert_or_replace(record)
    db.session.commit()

    yield

    _delete_record('lit', 111)


@pytest.fixture(scope='function')
def not_yet_deleted_record(app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'deleted'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        },
        '_collections': ['Literature']
    }

    with db.session.begin_nested():
        record_insert_or_replace(record)
    db.session.commit()

    yield

    _delete_record('lit', 111)


@pytest.fixture(scope='function')
def merged_records(app):
    merged_snippet = (
        '<record>'
        '  <controlfield tag="001">111</controlfield>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">merged</subfield>'
        '  </datafield>'
        '  <datafield tag="981" ind1=" " ind2=" ">'
        '    <subfield code="a">222</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    deleted_snippet = (
        '<record>'
        '  <controlfield tag="001">222</controlfield>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">deleted</subfield>'
        '  </datafield>'
        '  <datafield tag="970" ind1=" " ind2=" ">'
        '    <subfield code="d">111</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )

    merged_record = marcxml2record(merged_snippet)
    merged_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

    deleted_record = marcxml2record(deleted_snippet)
    deleted_record['$schema'] = 'http://localhost:5000/schemas/records/hep.json'

    with db.session.begin_nested():
        merged_uuid = record_insert_or_replace(merged_record).id
        deleted_uuid = record_insert_or_replace(deleted_record).id
    db.session.commit()

    es.indices.refresh('records-hep')

    yield

    _delete_merged_records('lit', 111, 222, merged_uuid, deleted_uuid)


@pytest.fixture(scope='function')
def not_yet_merged_records(app):
    merged_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'merged'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/111',
        },
        '_collections': ['Literature'],
    }

    deleted_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 222,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'deleted'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/222',
        },
        '_collections': ['Literature'],
    }

    with db.session.begin_nested():
        merged_uuid = record_insert_or_replace(merged_record).id
        deleted_uuid = record_insert_or_replace(deleted_record).id
    db.session.commit()

    yield

    _delete_merged_records('lit', 111, 222, merged_uuid, deleted_uuid)


@pytest.fixture(scope='function')
def records_to_be_merged(app):
    merged_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'merged'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/111',
        },
        '_collections': ['Literature'],
    }

    deleted_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 222,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'deleted'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/222',
        },
        '_collections': ['Literature'],
    }

    pointing_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'accelerator_experiments': [
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/222',
                },
            },
        ],
        'control_number': 333,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'pointing'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/api/literature/333',
        },
        '_collections': ['Literature'],
    }

    with db.session.begin_nested():
        merged_uuid = record_insert_or_replace(merged_record).id
        deleted_uuid = record_insert_or_replace(deleted_record).id
        record_insert_or_replace(pointing_record)
    db.session.commit()

    es.indices.refresh('records-hep')

    yield

    _delete_merged_records('lit', 111, 222, merged_uuid, deleted_uuid)
    _delete_record('lit', 333)


def test_deleted_record_stays_deleted(api_client, deleted_record):
    assert api_client.get('/literature/111').status_code == 410


def test_record_can_be_deleted(api_client, not_yet_deleted_record):
    assert api_client.get('/literature/111').status_code == 200

    record = get_db_record('lit', 111)
    record.delete()
    db.session.commit()

    assert api_client.get('/literature/111').status_code == 410


def test_merged_records_stay_merged(api_client, merged_records):
    merge_merged_records.delay()

    assert api_client.get('/literature/111').status_code == 200
    assert api_client.get('/literature/222').status_code == 301


def test_records_can_be_merged(api_client, not_yet_merged_records):
    assert api_client.get('/literature/111').status_code == 200
    assert api_client.get('/literature/222').status_code == 200

    merged_record = get_db_record('lit', 111)
    deleted_record = get_db_record('lit', 222)
    deleted_record['deleted'] = True
    deleted_record['new_record'] = {'$ref': 'http://localhost:5000/api/record/111'}
    deleted_record.merge(merged_record)
    db.session.commit()

    assert api_client.get('/literature/111').status_code == 200
    assert api_client.get('/literature/222').status_code == 301


def test_references_can_be_updated(app, records_to_be_merged):
    merged_record = get_db_record('lit', 111)
    deleted_record = get_db_record('lit', 222)

    deleted_record.merge(merged_record)
    update_refs.delay(
        'http://localhost:5000/api/literature/222',
        'http://localhost:5000/api/literature/111')

    pointing_record = get_db_record('lit', 333)

    expected = 'http://localhost:5000/api/literature/111'
    result = get_value(
        pointing_record, 'accelerator_experiments[0].record.$ref')

    assert expected == result


def test_get_es_records_handles_empty_lists(app):
    get_es_records('lit', [])  # Does not raise.


def test_get_es_records_accepts_lists_of_integers(app):
    records = get_es_records('lit', [4328])

    assert len(records) == 1


def test_get_es_records_accepts_lists_of_strings(app):
    records = get_es_records('lit', ['4328'])

    assert len(records) == 1


def test_records_files_attached_correctly(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ]
    }

    record = InspireRecord.create(record_json)
    record.files['fulltext.pdf'] = StringIO.StringIO()
    record.commit()

    assert 'fulltext.pdf' in record.files


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_handles_documents(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],
        'documents': [{
            'key': 'arXiv:1710.01187.pdf',
            'url': '/afs/cern.ch/project/inspire/PROD/var/data/files/g151/3037619/content.pdf;1',
        }]  # record/1628455/export/xme
    }

    record = InspireRecord.create(record_json)
    expected_file_content = 'dummy body'
    expected_key = '1_arXiv:1710.01187.pdf'

    assert expected_key in record.files.keys
    assert len(record.files) == 1
    assert len(record['documents']) == len(record_json['documents'])
    file_content = open(record.files[expected_key].obj.file.uri).read()
    assert file_content == expected_file_content


def test_update_handles_documents(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
    }

    update_to_record = {
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/pdf',
        }],
    }

    expected_file_content = 'dummy body'
    expected_key = '1_Fulltext.pdf'

    record = InspireRecord.create(record_json)
    assert not len(record.files)

    record.clear()
    updated_json = record_json
    updated_json.update(copy.deepcopy(update_to_record))

    with patch(
        'inspirehep.modules.records.api.fsopen',
        mock_open(read_data=expected_file_content),
    ):
        record.update(updated_json)

    assert expected_key in record.files.keys
    assert len(record.files) == len(update_to_record['documents'])
    assert len(record['documents']) == len(update_to_record['documents'])
    file_content = open(record.files[expected_key].obj.file.uri).read()
    assert file_content == expected_file_content


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_handles_figures(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],
        'figures': [{
            'key': 'graph.png',
            'url': '/afs/cern.ch/project/inspire/PROD/var/data/files/g151/3037619/graph.png;1',
        }]  # record/1628455/export/xme
    }

    record = InspireRecord.create(record_json)
    expected_file_content = 'dummy body'
    expected_key = '1_graph.png'

    assert expected_key in record.files.keys
    assert len(record.files) == 1
    assert len(record['figures']) == len(record_json['figures'])
    file_content = open(record.files[expected_key].obj.file.uri).read()
    assert file_content == expected_file_content


def test_update_handles_figures(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
    }

    update_to_record = {
        'figures': [{
            'key': 'graph.png',
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/png',
        }],
    }

    expected_file_content = 'dummy body'
    expected_key = '1_graph.png'

    record = InspireRecord.create(record_json)
    assert not len(record.files)

    record.clear()
    updated_json = record_json
    updated_json.update(copy.deepcopy(update_to_record))

    with patch(
        'inspirehep.modules.records.api.fsopen',
        mock_open(read_data=expected_file_content),
    ):
        record.update(updated_json)

    assert expected_key in record.files.keys
    assert len(record.files) == len(update_to_record['figures'])
    assert len(record['figures']) == len(update_to_record['figures'])
    file_content = open(record.files[expected_key].obj.file.uri).read()
    assert file_content == expected_file_content


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='doc1 body'),
)
def test_update_with_only_new(app):
    doc1_expected_file_content = 'doc1 body'
    doc1_expected_key = '1_Fulltext.pdf'
    doc2_expected_file_content = 'doc2 body'
    doc2_expected_key = '1_Fulltext.pdf_1'

    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': '/some/non/existing/path.pdf',
        }],
    }

    update_to_record = {
        'documents': [
            {
                'key': doc1_expected_key,
                'url': '/api/files/somebucket/somefile',
            },
            {
                'key': 'Fulltext.pdf',
                'url': 'http://www.mdpi.com/2218-1997/3/1/24/pdf',
            },
        ],
    }

    record = InspireRecord.create(record_json)

    assert doc1_expected_key in record.files.keys
    assert len(record.files) == len(record_json['documents'])
    assert len(record['documents']) == len(record_json['documents'])
    file_content = open(record.files[doc1_expected_key].obj.file.uri).read()
    assert file_content == doc1_expected_file_content

    doc1_old_api_url = record['documents'][0]['url']
    record.clear()
    record_json.update(copy.deepcopy(update_to_record))

    with patch(
        'inspirehep.modules.records.api.fsopen',
        mock_open(read_data=doc2_expected_file_content),
    ):
        record.update(record_json, only_new=True)

    assert len(record['documents']) == len(update_to_record['documents'])
    for document in record['documents']:
        assert document['key'] in [doc1_expected_key, doc2_expected_key]
        if document['key'] == doc1_expected_key:
            file_content = open(
                record.files[doc1_expected_key].obj.file.uri
            ).read()
            assert file_content == doc1_expected_file_content
            assert document['url'] == doc1_old_api_url

        elif document['key'] == doc2_expected_key:
            file_content = open(
                record.files[doc2_expected_key].obj.file.uri
            ).read()
            assert file_content == doc2_expected_file_content


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_with_source_record_with_same_control_number(app):
    expected_file_content = 'dummy body'
    expected_key = '1_Fulltext.pdf'

    record1_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': '/some/non/existing/path.pdf',
        }],
    }

    record2_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
    }

    record1 = InspireRecord.create(record1_json)
    rec1_file_content = open(record1.files[expected_key].obj.file.uri).read()
    assert rec1_file_content == expected_file_content

    record2_json['documents'] = copy.deepcopy(record1['documents'])

    record2 = InspireRecord.create(record2_json, files_src_records=[record1])

    assert len(record2.files) == len(record2_json['documents'])
    assert len(record2['documents']) == len(record2_json['documents'])
    assert record2['documents'][0]['url'] != record1['documents'][0]['url']
    rec2_file_content = open(record2.files[expected_key].obj.file.uri).read()
    assert rec2_file_content == expected_file_content


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_with_source_record_with_different_control_number(app):
    expected_file_content = 'dummy body'
    rec1_expected_key = '1_Fulltext.pdf'
    rec2_expected_key = '2_Fulltext.pdf'

    record1_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': '/some/non/existing/path.pdf',
        }],
    }

    record2_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 2,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
    }

    record1 = InspireRecord.create(record1_json)
    rec1_file_content = open(
        record1.files[rec1_expected_key].obj.file.uri
    ).read()
    assert rec1_file_content == expected_file_content

    record2_json['documents'] = copy.deepcopy(record1['documents'])

    record2 = InspireRecord.create(record2_json, files_src_records=[record1])

    assert len(record2.files) == len(record2_json['documents'])
    assert len(record2['documents']) == len(record2_json['documents'])
    assert record2['documents'][0]['url'] != record1['documents'][0]['url']
    rec2_file_content = open(
        record2.files[rec2_expected_key].obj.file.uri
    ).read()
    assert rec2_file_content == expected_file_content


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_with_multiple_source_records(app):
    expected_file_content = 'dummy body'
    rec1_expected_key = '1_Fulltext.pdf'
    rec2_expected_key = '2_Fulltext.pdf'
    rec3_expected_keys = [
        '3_Fulltext.pdf',
        '3_Fulltext.pdf_1',
    ]

    record1_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': '/some/non/existing/path.pdf',
            'description': 'record1 document',
        }],
    }

    record2_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 2,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
        'documents': [{
            'key': 'Fulltext.pdf',
            'url': '/some/non/existing/path.pdf',
            'description': 'record2 document',
        }],
    }

    record3_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 3,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],  # DESY harvest
    }

    record1 = InspireRecord.create(record1_json)
    rec1_file_content = open(
        record1.files[rec1_expected_key].obj.file.uri
    ).read()
    assert rec1_file_content == expected_file_content

    record2 = InspireRecord.create(record2_json)
    rec2_file_content = open(
        record2.files[rec2_expected_key].obj.file.uri
    ).read()
    assert rec2_file_content == expected_file_content

    record3_json['documents'] = copy.deepcopy(record1['documents'])
    record3_json['documents'].extend(copy.deepcopy(record2['documents']))
    record3 = InspireRecord.create(
        record3_json,
        files_src_records=[record1, record2],
    )

    assert len(record3.files) == (
        len(record1_json['documents']) +
        len(record2_json['documents'])
    )
    assert rec3_expected_keys == record3.files.keys
    for file_key in record3.files.keys:
        rec3_file_content = open(
            record3.files[file_key].obj.file.uri
        ).read()
        assert rec3_file_content == expected_file_content

    expected_descs = [
        orig_doc['description'] for orig_doc in record3_json['documents']
    ]
    current_descs = [
        doc['description'] for doc in record3['documents']
    ]
    assert current_descs == expected_descs


def test_create_with_records_skip_files_conf_does_not_add_documents_or_figures(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],
        'figures': [{
            'key': 'graph.png',
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/png',
        }],
        'documents': [{
            'key': 'arXiv:1710.01187.pdf',
            'url': '/afs/cern.ch/project/inspire/PROD/var/data/files/g151/3037619/content.pdf;1',
        }]  # record/1628455/export/xme -- with some modification
    }

    with patch.dict(app.config, {'RECORDS_SKIP_FILES': True}):
        record = InspireRecord.create(record_json)

    assert len(record.files) == 0
    assert record['documents'] == record_json['documents']
    assert record['figures'] == record_json['figures']


@patch(
    'inspirehep.modules.records.api.fsopen',
    mock_open(read_data='dummy body'),
)
def test_create_with_skip_files_param_overrides_records_skip_files_conf_and_does_add_documents_or_figures(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],
        'figures': [{
            'key': 'graph.png',
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/png',
        }],
        'documents': [{
            'key': 'arXiv:1710.01187.pdf',
            'url': '/afs/cern.ch/project/inspire/PROD/var/data/files/g151/3037619/content.pdf;1',
        }]  # record/1628455/export/xme -- with some modification
    }
    expected_document_file_content = 'dummy body'
    expected_document_key = '1_graph.png'

    expected_figure_file_content = 'dummy body'
    expected_figure_key = '1_graph.png'

    with patch.dict(app.config, {'RECORDS_SKIP_FILES': True}):
        with patch(
            'inspirehep.modules.records.api.fsopen',
            mock_open(read_data=expected_figure_file_content),
        ):
            record = InspireRecord.create(record_json, skip_files=False)

    assert len(record.files) == 2

    assert expected_document_key in record.files.keys
    assert len(record['documents']) == len(record_json['documents'])
    document_file_content = open(
        record.files[expected_document_key].obj.file.uri
    ).read()
    assert document_file_content == expected_document_file_content

    assert expected_figure_key in record.files.keys
    assert len(record['figures']) == len(record_json['figures'])
    figure_file_content = open(
        record.files[expected_figure_key].obj.file.uri
    ).read()
    assert figure_file_content == expected_figure_file_content


def test_create_with_skip_files_param_overrides_records_skip_files_conf_and_does_not_add_documents_or_figures(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 1,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': [
            'Literature'
        ],
        'figures': [{
            'key': 'graph.png',
            'url': 'http://www.mdpi.com/2218-1997/3/1/24/png',
        }],
        'documents': [{
            'key': 'arXiv:1710.01187.pdf',
            'url': '/afs/cern.ch/project/inspire/PROD/var/data/files/g151/3037619/content.pdf;1',
        }]  # record/1628455/export/xme -- with some modification
    }

    with patch.dict(app.config, {'RECORDS_SKIP_FILES': False}):
        record = InspireRecord.create(record_json, skip_files=True)

    assert len(record.files) == 0
    assert record['documents'] == record_json['documents']
    assert record['figures'] == record_json['figures']
