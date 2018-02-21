# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
from elasticsearch import NotFoundError

from invenio_db import db
from invenio_search.api import current_search_client as es

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.receivers import update_related_records_successor_relations
from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.record import get_title
from inspirehep.utils.record_getter import get_db_record


@pytest.fixture(scope='function')
def mock_hep_records_in_db(isolated_app):
    """Temporarily add a few hep records in the DB"""
    from inspirehep.modules.migrator.tasks import record_insert_or_replace  # imported here because it is a Celery task

    related_record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936475,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936475"},
        "related_records": [
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936476"}
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936477"},
                "relation": "predecessor"
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936478"},
                "relation": "parent"
            },
        ],
        "titles": [
            {"title": "Related Record"}
        ]
    }

    already_existing_record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936476,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936476"},
        "titles": [
            {"title": "Existing Record"}
        ]
    }

    record_insert_or_replace(related_record)
    record_insert_or_replace(already_existing_record)
    db.session.commit()
    es.indices.refresh('records-hep')

    yield

    es.indices.refresh('records-hep')


def test_that_db_changes_are_mirrored_in_es(app):
    search = LiteratureSearch()
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': ['Literature']
    }

    # When a record is created in the DB, it is also created in ES.

    record = InspireRecord.create(json)
    es_record = search.get_source(record.id)

    assert get_title(es_record) == 'foo'

    # When a record is updated in the DB, is is also updated in ES.

    record['titles'][0]['title'] = 'bar'
    record.commit()
    es_record = search.get_source(record.id)

    assert get_title(es_record) == 'bar'

    # When a record is deleted in the DB, it is also deleted in ES.

    record._delete(force=True)

    with pytest.raises(NotFoundError):
        es_record = search.get_source(record.id)


def test_update_related_records_successor_relations_new_record_with_wrong_relation_value(isolated_app, mock_hep_records_in_db):
    new_record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936478,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936478"},
        "related_records": [
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936475"},
                "relation": "predecessor"
            }
        ],
        "titles": [
            {"title": "New Record"}
        ]
    }

    update_related_records_successor_relations(None, new_record)

    result = get_db_record('lit', 1936475)

    expected = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936475,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936475"},
        "related_records": [
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936476"}
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936477"},
                "relation": "predecessor"
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936478"},
                "relation": "successor"  # successfully updated relation - originally wrong value : 'parent'
            },
        ],
        "titles": [
            {"title": "Related Record"}
        ]
    }

    assert result == expected


def test_update_related_records_successor_relations_existing_record_with_no_relation_field(isolated_app, mock_hep_records_in_db):
    updated_already_existing_record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936476,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936476"},
        "related_records": [
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936475"},
                "relation": "predecessor"
            }
        ],
        "titles": [
            {"title": "Existing Record"}
        ]
    }

    update_related_records_successor_relations(None, updated_already_existing_record)

    result = get_db_record('lit', 1936475)

    expected = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "control_number": 1936475,
        "_collections": [
            "Literature"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "self": {"$ref": "http://localhost:5000/api/hep/1936475"},
        "related_records": [
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936476"},
                "relation": "successor"  # successfully updated relation - originally non-existent field
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936477"},
                "relation": "predecessor"
            },
            {
                "record": {"$ref": "http://localhost:5000/api/hep/1936478"},
                "relation": "parent"
            },
        ],
        "titles": [
            {"title": "Related Record"}
        ]
    }

    assert expected == result
