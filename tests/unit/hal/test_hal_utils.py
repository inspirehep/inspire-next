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

from mock import patch

from inspire_dojson.utils import validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.hal.utils import (
    get_abstract,
    get_conference_city,
    get_conference_country,
    get_conference_date,
    get_conference_record,
    get_conference_title,
    get_divulgation,
    get_document_types,
    get_doi,
    get_domain,
    get_journal_title,
    get_language,
    get_peer_reviewed,
    get_publication_date,
    is_published,
)


def test_get_abstract():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    record = {
        'abstracts': [
            {'value': 'Probably not.'},
        ],
    }
    assert validate(record['abstracts'], subschema) is None

    expected = 'Probably not.'
    result = get_abstract(record)

    assert expected == result


def test_get_conference_city():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    record = {
        'address': [
            {
                'cities': [
                    'Tokyo',
                ],
            },
        ],
    }
    assert validate(record['address'], subschema) is None

    expected = 'Tokyo'
    result = get_conference_city(record)

    assert expected == result


def test_get_conference_country():
    schema = load_schema('conferences')
    subschema = schema['properties']['address']

    record = {
        'address': [
            {'country_code': 'JP'},
        ],
    }
    assert validate(record['address'], subschema) is None

    expected = 'jp'
    result = get_conference_country(record)

    assert expected == result


def test_get_conference_date():
    schema = load_schema('conferences')
    subschema = schema['properties']['opening_date']

    record = {'opening_date': '1999-11-16'}
    assert validate(record['opening_date'], subschema) is None

    expected = '1999-11-16'
    result = get_conference_date(record)

    assert expected == result


@patch('inspirehep.modules.hal.utils.replace_refs')
def test_get_conference_record(replace_refs):
    schema = load_schema('hep')
    control_number_schema = schema['properties']['control_number']
    publication_info_schema = schema['properties']['publication_info']

    conference_record = {'control_number': 972464}
    assert validate(conference_record['control_number'], control_number_schema) is None

    record = {
        'publication_info': [
            {
                'conference_record': {
                    '$ref': '/api/conferences/972464',
                },
            },
        ],
    }
    assert validate(record['publication_info'], publication_info_schema) is None

    replace_refs.return_value = conference_record

    expected = 972464
    result = get_conference_record(record)

    assert expected == result['control_number']


def test_get_conference_title():
    schema = load_schema('conferences')
    subschema = schema['properties']['titles']

    record = {
        'titles': [
            {'title': 'Workshop on Neutrino Physics'},
        ],
    }
    assert validate(record['titles'], subschema) is None

    expected = 'Workshop on Neutrino Physics'
    result = get_conference_title(record)

    assert expected == result


def test_get_divulgation():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_type']

    record = {
        'publication_type': [
            'introductory',
        ],
    }
    assert validate(record['publication_type'], subschema) is None

    expected = 1
    result = get_divulgation(record)

    assert expected == result


def test_get_document_types():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    record = {
        'document_type': [
            'article',
        ],
    }
    assert validate(record['document_type'], subschema) is None

    expected = [
        'article',
    ]
    result = get_document_types(record)

    assert expected == result


def test_get_doi():
    schema = load_schema('hep')
    subschema = schema['properties']['dois']

    record = {
        'dois': [
            {'value': '10.1016/0029-5582(61)90469-2'},
        ],
    }
    assert validate(record['dois'], subschema) is None

    expected = '10.1016/0029-5582(61)90469-2'
    result = get_doi(record)

    assert expected == result


def test_get_domain():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    record = {
        'inspire_categories': [
            {'term': 'Experiment-HEP'},
        ],
    }
    assert validate(record['inspire_categories'], subschema) is None

    expected = 'phys.hexp'
    result = get_domain(record)

    assert expected == result


def test_get_journal_title():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        'publication_info': [
            {'journal_title': 'Phys.Part.Nucl.Lett.'},
        ],
    }
    assert validate(record['publication_info'], subschema) is None

    expected = 'Phys.Part.Nucl.Lett.'
    result = get_journal_title(record)

    assert expected == result


def test_get_language():
    schema = load_schema('hep')
    subschema = schema['properties']['languages']

    record = {
        'languages': [
            'it',
        ],
    }
    assert validate(record['languages'], subschema) is None

    expected = 'it'
    result = get_language(record)

    assert expected == result


def test_get_language_falls_back_to_english():
    record = {}

    expected = 'en'
    result = get_language(record)

    assert expected == result


def test_get_peer_reviewed():
    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    record = {'refereed': True}
    assert validate(record['refereed'], subschema) is None

    expected = 1
    result = get_peer_reviewed(record)

    assert expected == result


def test_get_publication_date():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    record = {
        'publication_info': [
            {'year': 2017},
        ],
    }
    assert validate(record['publication_info'], subschema) is None

    expected = '2017'
    result = get_publication_date(record)

    assert expected == result


def test_is_published():
    schema = load_schema('hep')
    dois_schema = schema['properties']['dois']
    publication_info_schema = schema['properties']['publication_info']

    record = {
        'dois': [
            {'value': '10.1016/0029-5582(61)90469-2'},
        ],
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'},
        ],
    }
    assert validate(record['dois'], dois_schema) is None
    assert validate(record['publication_info'], publication_info_schema) is None

    assert is_published(record)
