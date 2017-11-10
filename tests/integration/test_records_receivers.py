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
from elasticsearch import NotFoundError

from invenio_db import db

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.record import get_title
from inspirehep.utils.record_getter import get_es_record


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


def test_match_references_when_reference_matches(app):
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 123,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': ['Literature'],
        'references': [{
            'reference': {
                'dois': ['10.1007/978-3-319-15001-7']
            }
        }]
    }

    record = InspireRecord.create(json)
    db.session.commit()

    assert record['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/1373790'

    referred_record = get_es_record('lit', 1373790)
    assert referred_record['citation_count'] == 1

    record._delete(force=True)
    db.session.commit()


def test_match_references_when_record_matches_external_reference(app):
    from inspirehep.modules.migrator.tasks import record_insert_or_replace

    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 456,
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        'dois': [
            {
                'value': '10.1016/j.physletb.2012.08.020'
            }
        ],
        '_collections': ['Literature']
    }

    #FIXME Need to create PID
    # record = InspireRecord.create(json)
    import pytest; pytest.set_trace()
    with db.session.begin_nested():
        record = record_insert_or_replace(json)
    db.session.commit()

    import pytest; pytest.set_trace()

    referred_record = get_es_record('lit', 456)

    assert referred_record['citation_count'] == 1

    record._delete(force=True)
    db.session.commit()
