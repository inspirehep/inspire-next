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

import json

from invenio_db import db
from invenio_search import current_search

from utils import _delete_record
from inspirehep.modules.records.api import InspireRecord
from factories.db.invenio_records import TestRecordMetadata


def test_search_conferences_is_there(app_client):
    assert app_client.get('/search?cc=conferences').status_code == 200


def test_search_authors_is_there(app_client):
    assert app_client.get('/search?cc=authors').status_code == 200


def test_search_data_is_there(app_client):
    assert app_client.get('/search?cc=data').status_code == 200


def test_search_experiments_is_there(app_client):
    assert app_client.get('/search?cc=experiments').status_code == 200


def test_search_institutions_is_there(app_client):
    assert app_client.get('/search?cc=institutions').status_code == 200


def test_search_journals_is_there(app_client):
    assert app_client.get('/search?cc=journals').status_code == 200


def test_search_jobs_is_there(app_client):
    assert app_client.get('/search?cc=jobs').status_code == 200


def test_search_falls_back_to_hep(app_client):
    assert app_client.get('/search').status_code == 200


def test_regression_author_count_10_does_not_display_zero_facet(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Article with 10 authors'}],
        '_collections': ['Literature'],
        'authors': []
    }
    for i in range(10):
        record_json['authors'].append({'full_name': 'Pincopallino' + str(i)})

    rec = InspireRecord.create(data=record_json)
    rec.commit()
    db.session.commit()
    current_search.flush_and_refresh('records-hep')

    response_facets = isolated_api_client.get('/literature/facets?q=ac%2010')
    response_records = isolated_api_client.get('/literature?q=ac%2010')
    # we don't have isolation on tests and are inconsistent between test
    # environments.
    data_facets = json.loads(response_facets.data)
    data_records = json.loads(response_records.data)

    assert data_facets['aggregations']['author_count']['buckets'][0]['doc_count'] == data_records['hits']['total']


def test_search_hep_author_publication(isolated_api_client):
    result = isolated_api_client.get('/literature/facets?facet_name=hep-author-publication')
    result_data = json.loads(result.get_data(as_text=True))

    expected_aggregations = [
        'earliest_date',
        'author',
        'author_count',
        'doc_type',
    ]
    result_aggregations = result_data['aggregations'].keys()

    for aggregation in expected_aggregations:
        assert aggregation in result_aggregations

    assert len(expected_aggregations) == len(result_aggregations)


def test_search_hep_author_publication_with_author_exclude(isolated_api_client):
    result = isolated_api_client.get('/literature/facets?facet_name=hep-author-publication&exclude_author_value=Jones, Jessica')
    result_data = json.loads(result.get_data(as_text=True))

    expected_aggregations = [
        'earliest_date',
        'author',
        'author_count',
        'doc_type',
    ]
    result_aggregations = result_data['aggregations'].keys()

    for aggregation in expected_aggregations:
        assert aggregation in result_aggregations

    assert len(expected_aggregations) == len(result_aggregations)


def test_search_hep_author_publication_with_not_existing_facet_name(isolated_api_client):
    result = isolated_api_client.get('/literature/facets?facet_name=not-existing-facet')
    result_data = json.loads(result.get_data(as_text=True))

    expected_aggregations = [
        'earliest_date',
        'author',
        'author_count',
        'doc_type',
        'subject',
        'arxiv_categories',
        'experiment',
    ]
    result_aggregations = result_data['aggregations'].keys()

    for aggregation in expected_aggregations:
        assert aggregation in result_aggregations

    assert len(expected_aggregations) == len(result_aggregations)


def test_selecting_2_facets_generates_search_with_must_query(api_client):
    record_json = {
        'control_number': 843386527,
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Article 1'}],
        '_collections': ['Literature'],
        'authors': [{'full_name': 'John Doe'}]
    }

    rec = InspireRecord.create(data=record_json)
    rec.commit()

    record_json2 = {
        'control_number': 843386521,
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Article 2'}],
        '_collections': ['Literature'],
        'authors': [{'full_name': 'John Doe'}, {'full_name': 'John Doe2'}]
    }

    rec2 = InspireRecord.create(data=record_json2)
    rec2.commit()

    db.session.commit()
    current_search.flush_and_refresh('records-hep')

    response = api_client.get('/literature?q=&author=BAI_John%20Doe')
    data = json.loads(response.data)
    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]
    assert rec['control_number'] in response_recids
    assert rec2['control_number'] in response_recids

    response = api_client.get('/literature?q=&author=BAI_John%20Doe&author=BAI_John%20Doe2')
    data = json.loads(response.data)
    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]
    assert rec['control_number'] not in response_recids
    assert rec2['control_number'] in response_recids

    _delete_record('lit', 843386527)
    _delete_record('lit', 843386521)
    db.session.commit()


def test_exact_author_bai_query(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Article 1'}],
        '_collections': ['Literature'],
        'authors': [{'full_name': 'John Doe',
                     "ids": [{
                         "schema": "INSPIRE BAI",
                         "value": "J.Doe.1"
                     }
                     ]}],
    }

    rec_factory = TestRecordMetadata.create_from_kwargs(json=record_json, index_name='records-hep')
    rec = rec_factory.record_metadata.json
    response = isolated_api_client.get('/literature?q=ea%20j.doe.1')
    data = json.loads(response.data)
    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]
    assert rec['control_number'] in response_recids

    response = isolated_api_client.get('/literature?q=ea%20J.Doe.1')
    data = json.loads(response.data)
    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]
    assert rec['control_number'] in response_recids

    response = isolated_api_client.get('/literature?q=ea%20j.Doe.1')
    data = json.loads(response.data)
    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]
    assert rec['control_number'] in response_recids


def test_affiliations_exact_search(isolated_api_client):
    record_json_1 = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "document_type": ["article"],
        "titles": [{"title": "Article 1"}],
        "_collections": ["Literature"],
        "authors": [
            {"full_name": "John Doe", "affiliations": [{"value": "Harvard U."}]}
        ],
    }

    record_json_2 = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "document_type": ["article"],
        "titles": [{"title": "Article 2"}],
        "_collections": ["Literature"],
        "authors": [
            {
                "full_name": "John Doe 2",
                "affiliations": [{"value": "Harvard U., Phys. Dept."}],
            }
        ],
    }

    record_factory_1 = TestRecordMetadata.create_from_kwargs(json=record_json_1, index_name='records-hep')
    record_1 = record_factory_1.record_metadata.json

    record_factory_2 = TestRecordMetadata.create_from_kwargs(json=record_json_2, index_name='records-hep')
    record_2 = record_factory_2.record_metadata.json

    response = isolated_api_client.get('/literature?q=authors.affiliations.value%3AHarvard%20U.')
    data = json.loads(response.data)

    response_recids = [record['metadata']['control_number'] for record in data['hits']['hits']]

    assert record_1['control_number'] in response_recids
    assert record_2['control_number'] not in response_recids


def check_lit_query(query, isolated_api_client, expected_record=None,
                    hits_count=None, not_expected=None):
    response = json.loads(isolated_api_client.get('/literature?q=%s' % query).data)
    if expected_record:
        assert expected_record in [r['metadata'] for r in response['hits']['hits']]
    if hits_count:
        assert len(response['hits']['hits']) == hits_count
    if not_expected:
        assert expected_record not in [r['metadata'] for r in response['hits']['hits']]


def test_default_search_without_keywords(isolated_api_client):
    record_json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "document_type": ["article"],
        "titles": [{"title": "Article2"}],
        "_collections": ["Literature"],
        "authors": [
            {
                "full_name": "Qwerty Azerty",
                "affiliations": [{"value": "Some strange name XXYYZZ"}],
            }
        ],
        'dois': [{
            'value': '10.1007/978-3-319-15001-7'
        }],
        'inspire_categories': [{
            'term': 'Experiment-HEP'
        }],
        'isbns': [
            {'value': '9783319150000'},
            {'value': '9783319150017'}
        ],
        'persistent_identifiers': [{
            'source': 'SOME_SOURCE',
            'value': 'SOME_VALUE',
        }]

    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json, index_name='records-hep')
    expected_record = {
        u'$schema': u'http://localhost:5000/schemas/records/hep.json',
        u'control_number': record.record_metadata.json['control_number'],
        u'authors': [{
            u'affiliations': [{
                u'value': u'Some strange name XXYYZZ'
            }],
            u'full_name': u'Qwerty Azerty'
        }],
        u'titles': [{
            u'title': u'Article2'
        }],
        u'dois': [{
            u'value': u'10.1007/978-3-319-15001-7'
        }],
        u'inspire_categories': [{
            u'term': u'Experiment-HEP'
        }],
    }

    # Test default query with title
    check_lit_query("Article2", isolated_api_client,
                    expected_record=expected_record)

    # Test default query with part of author name
    check_lit_query("Qwerty", isolated_api_client,
                    expected_record=expected_record)

    # Test default query with full author name
    check_lit_query("Qwerty Azerty", isolated_api_client,
                    expected_record=expected_record)

    # Test default query with authors affiliation
    check_lit_query("XXYYZZ", isolated_api_client,
                    expected_record=expected_record)

    # Test default query with control_number
    check_lit_query(record.record_metadata.json['control_number'],
                    isolated_api_client,
                    expected_record=expected_record)

    # Test default query with DOI number
    check_lit_query('10.1007/978-3-319-15001-7', isolated_api_client,
                    expected_record=expected_record)

    # Test default query with inspire isbns
    check_lit_query("9783319150017", isolated_api_client,
                    expected_record=expected_record)

    # Test default query with persistent_identifier.value
    check_lit_query("SOME_VALUE", isolated_api_client,
                    expected_record=expected_record)


def test_default_search_without_keywords_on_not_searched_fields(isolated_api_client):
    record_json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "document_type": ["article"],
        "titles": [{"title": "Article2"}],
        "_collections": ["Literature"],
        "authors": [
            {
                "full_name": "Qwerty Azerty",
                "affiliations": [{"value": "Some strange name XXYYZZ"}],
            }
        ],
        'dois': [{
            'value': '10.1007/978-3-319-15001-7'
        }],
        'inspire_categories': [{
            'term': 'Experiment-HEP'
        }],
        'isbns': [
            {'value': '9783319150000'},
            {'value': '9783319150017'}
        ],
        'texkeys': ['Schorner-Sadenius:27015cga'],
        'persistent_identifiers': [{
            'source': 'SOME_SOURCE',
            'value': 'SOME_VALUE',
        }]

    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json, index_name='records-hep')

    not_expected_record = {
        u'$schema': u'http://localhost:5000/schemas/records/hep.json',
        u'control_number': record.record_metadata.json['control_number'],
        u'authors': [{
            u'affiliations': [{
                u'value': u'Some strange name XXYYZZ'
            }],
            u'full_name': u'Qwerty Azerty'
        }],
        u'titles': [{
            u'title': u'Article2'
        }],
        u'dois': [{
            u'value': u'10.1007/978-3-319-15001-7'
        }],
        u'inspire_categories': [{
            u'term': u'Experiment-HEP'
        }],
    }

    # Test default query with persistent_identifier.value
    check_lit_query("SOME_SOURCE", isolated_api_client,
                    not_expected=not_expected_record)

    # Test default query with inspire categories
    check_lit_query("Experiment-HEP", isolated_api_client,
                    not_expected=not_expected_record)
