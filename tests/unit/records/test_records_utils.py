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

from inspire_schemas.api import load_schema, validate

from inspirehep.modules.records.utils import (
    get_endpoint_from_record,
    populate_earliest_date,
)


def test_get_endpoint_from_record():
    expected = 'literature'
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json'
    }
    result = get_endpoint_from_record(record)

    assert expected == result


def test_get_endpoint_from_record_supports_relative_urls():
    expected = 'authors'
    record = {
        '$schema': 'schemas/records/authors.json'
    }
    result = get_endpoint_from_record(record)

    assert expected == result


def test_populate_earliest_date_from_preprint_date():
    schema = load_schema('hep')
    subschema = schema['properties']['preprint_date']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'preprint_date': '2014-05-29',
    }
    assert validate(record['preprint_date'], subschema) is None

    populate_earliest_date(record)

    expected = '2014-05-29'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_thesis_info_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'thesis_info': {
            'date': '2008',
        },
    }
    assert validate(record['thesis_info'], subschema) is None

    populate_earliest_date(record)

    expected = '2008'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_thesis_info_defense_date():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'thesis_info': {
            'defense_date': '2012-06-01',
        },
    }
    assert validate(record['thesis_info'], subschema) is None

    populate_earliest_date(record)

    expected = '2012-06-01'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_publication_info_year():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'publication_info': [
            {'year': 2014},
        ],
    }
    assert validate(record['publication_info'], subschema) is None

    populate_earliest_date(record)

    expected = '2014'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_legacy_creation_date():
    schema = load_schema('hep')
    subschema = schema['properties']['legacy_creation_date']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'legacy_creation_date': '2015-11-04',
    }
    assert validate(record['legacy_creation_date'], subschema) is None

    populate_earliest_date(record)

    expected = '2015-11-04'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_from_imprints_date():
    schema = load_schema('hep')
    subschema = schema['properties']['imprints']

    record = {
        '$schema': 'http://localhost:5000/records/schemas/hep.json',
        'imprints': [
            {'date': '2014-09-26'},
        ],
    }
    assert validate(record['imprints'], subschema) is None

    populate_earliest_date(record)

    expected = '2014-09-26'
    result = record['earliest_date']

    assert expected == result


def test_populate_earliest_date_does_nothing_if_record_is_not_literature():
    record = {'$schema': 'http://localhost:5000/schemas/records/other.json'}

    populate_earliest_date(record)

    assert 'earliest_date' not in record
