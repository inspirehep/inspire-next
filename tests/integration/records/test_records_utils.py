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

from factories.db.invenio_records import TestRecordMetadata

from inspirehep.modules.records.utils import get_linked_records_in_field


def test_get_linked_records_in_field_handles_empty_field(isolated_app):
    results = get_linked_records_in_field({}, 'foo')
    assert list(results) == []


def test_get_linked_records_in_field_with_missing_link(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '29177.json')
    record = {
        'references': [
            {'record': {'$ref': 'https://labs.inspirehep.net/api/literature/1234'}},
        ],
    }
    results = get_linked_records_in_field(record, 'references.record')
    expected = []

    assert expected == list(results)


def test_get_linked_records_in_field_finds_existing_link(isolated_app):
    instance = TestRecordMetadata.create_from_file(__name__, '29177.json')

    record = {
        'references': [
            {'record': {'$ref': 'https://labs.inspirehep.net/api/literature/29177'}},
        ],
    }

    results = get_linked_records_in_field(record, 'references.record')
    expected = [instance.record_metadata.json]
    result = list(results)
    assert expected == result


def test_get_linked_records_in_field_handles_multiple_pid_types(isolated_app):
    instances = [
        TestRecordMetadata.create_from_file(__name__, '29177.json'),
        TestRecordMetadata.create_from_file(__name__, '1575134.json', pid_type='dat'),
    ]

    record = {
        'references': [
            {'record': {'$ref': 'https://labs.inspirehep.net/api/literature/29177'}},
            {'record': {'$ref': 'https://labs.inspirehep.net/api/data/1575134'}},
        ],
    }
    results = get_linked_records_in_field(record, 'references.record')
    expected = list(sorted(instance.record_metadata.json for instance in instances))
    result = list(sorted(results))  # FIXME: order is not preserved!
    assert expected == result
