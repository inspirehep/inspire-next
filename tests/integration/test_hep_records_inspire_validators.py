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

from invenio_db import db

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.validators.helpers import (
    FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE
)
from inspirehep.modules.records.validators.rules import (
    check_if_isbn_exist_in_other_records
)


@pytest.fixture(scope='function')
def test_record(app):
    sample_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 111,
        'document_type': [
            'article',
        ],
        'isbns': [
            {'value': '9783598215001'},
        ],
        'report_numbers': [
            {'value': '11111'}
        ],
        'titles': [
            {'title': 'sample'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        }
    }
    dupl_isbn_sample_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 222,
        'document_type': [
            'article',
        ],
        'isbns': [
            {'value': '9783598215001'},
        ],
        'report_numbers': [
            {'value': '11111'}
        ],
        'titles': [
            {'title': 'another_sample'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        }
    }

    record_id = InspireRecord.create(sample_record).id
    dupl_record_id = InspireRecord.create(dupl_isbn_sample_record).id

    db.session.commit()

    yield

    InspireRecord.get_record(record_id)._delete(force=True)
    InspireRecord.get_record(dupl_record_id)._delete(force=True)

    db.session.commit()


def format_error(_error):
    path = '/' + '/'.join(str(el) for el in _error.path)
    if path == '/':
        path = 'globalErrors'
    return {
        path: [{
            'message': _error.message,
            'type': _error.cause or 'Error'
        }]
    }


def test_check_if_isbn_exist_in_other_records(app, test_record):
    sample_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': 333,
        'document_type': [
            'book',
        ],
        'isbns': [
            {'value': '9783598215001'},
        ],
        'titles': [
            {'title': 'sample_record_title'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        }
    }

    expected = [{
        '/isbns/0/value': [{
            'message': FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE.format(
                field='isbns',
                value='9783598215001'
            ),
            'type': 'Error'
        }]
    }]

    result = [format_error(e) for e in check_if_isbn_exist_in_other_records(sample_record)]
    assert expected == result
