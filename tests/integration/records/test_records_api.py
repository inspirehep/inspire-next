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

import os

from tempfile import NamedTemporaryFile
import pytest

from invenio_pidstore.models import PersistentIdentifier, RecordIdentifier
from jsonschema import ValidationError
from six.moves.urllib.parse import quote

from inspirehep.modules.records.api import InspireRecord
from inspirehep.utils.record_getter import get_db_record
from factories.db.invenio_records import TestRecordMetadata


def test_validate_validates_format(app):
    article = get_db_record('lit', 4328)
    article.setdefault('acquisition_source', {})['email'] = 'not an email'
    with pytest.raises(ValidationError):
        article.commit()


def test_download_local_file(isolated_app):
    with NamedTemporaryFile(suffix=';1') as temp_file:
        file_location = 'file://{0}'.format(quote(temp_file.name))
        file_name = os.path.basename(temp_file.name)
        data = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            '_collections': [
                'Literature'
            ],
            'document_type': [
                'article'
            ],
            'titles': [
                {
                    'title': 'h'
                },
            ],
            'documents': [
                {
                    'key': file_name,
                    'url': file_location,
                },
            ],
        }

        record = InspireRecord.create(data)

        documents = record['documents']
        files = record['_files']

        assert 1 == len(documents)
        assert 1 == len(files)


def test_create_does_not_save_zombie_identifiers_if_record_creation_fails(isolated_app):
    invalid_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': [
            'Literature',
        ],
        'control_number': 1936477,
    }

    with pytest.raises(ValidationError):
        InspireRecord.create(invalid_record)

    record_identifier = RecordIdentifier.query.filter_by(recid=1936477).one_or_none()
    persistent_identifier = PersistentIdentifier.query.filter_by(pid_value='1936477').one_or_none()

    assert not record_identifier
    assert not persistent_identifier


def test_citations_count_equals_zero(isolated_app):
    record = TestRecordMetadata.create_from_kwargs().inspire_record
    assert record.get_citations_count() == 0L


def test_citations_count_non_zero(isolated_app):
    record_json = {
        'control_number': 321,
    }
    record_1 = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    ref = {'control_number': 4321, 'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)

    assert record_1.get_citations_count() == 1L

    ref2 = {'control_number': 43211, 'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref2)

    assert record_1.get_citations_count() == 2L

    ref3 = {'control_number': 43241, 'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref3)

    assert record_1.get_citations_count() == 3L


def test_doubled_citations_should_not_count_to_citation_count(isolated_app):
    record_json = {
        'control_number': 321,
    }
    record_1 = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    ref = {'control_number': 4321, 'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)
    TestRecordMetadata.create_from_kwargs(json=ref, disable_persistent_identifier=True)

    assert record_1.get_citations_count(show_duplicates=True) == 2
    assert record_1.get_citations_count() == 1


def test_deleted_citations_should_not_count_to_citation_count(isolated_app):
    record_json = {
        'control_number': 321,
    }
    record_1 = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record
    assert record_1.get_citations_count() == 0

    ref = {'control_number': 4321,
           'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)
    assert record_1.get_citations_count() == 1

    ref = {'control_number': 4322,
           'deleted': True,
           'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)
    assert record_1.get_citations_count() == 1

    ref = {'control_number': 4323,
           'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)

    assert record_1.get_citations_count() == 2


def test_not_count_citations_from_other_collections(isolated_app):
    record_json = {
        'control_number': 321,
    }
    record_1 = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record
    assert record_1.get_citations_count() == 0

    ref = {'control_number': 4321,
           'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)
    assert record_1.get_citations_count() == 1

    ref = {'_collections': ['HERMES Internal Notes'],
           'control_number': 4323,
           'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)

    assert record_1.get_citations_count() == 1
