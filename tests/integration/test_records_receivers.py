# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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
from elasticsearch import NotFoundError

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.record import get_title


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
