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

import json

from mock import patch


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


@patch('inspirehep.modules.search.search_factory.current_app')
def test_search_logs(current_app_mock, api_client):
    def _debug(log_output):
        query = {
            "sort": [
                {
                    "earliest_date": {
                        "order": "desc"
                    }
                }
            ],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "match": {
                                "_collections": "Literature"
                            }
                        }
                    ],
                    "minimum_should_match": "0<1",
                    "must": [
                        {
                            "match_all": {}
                        }
                    ]
                }
            },
            "size": 10,
            "from": 0,
            "_source": {
                "includes": [
                    "$schema",
                    "abstracts.value",
                    "arxiv_eprints.value",
                    "arxiv_eprints.categories",
                    "authors.affiliations",
                    "authors.full_name",
                    "authors.control_number",
                    "collaborations",
                    "control_number",
                    "citation_count",
                    "dois.value",
                    "earliest_date",
                    "inspire_categories",
                    "number_of_references",
                    "publication_info",
                    "report_numbers",
                    "titles.title"
                ]
            }
        }
        assert query == json.loads(log_output)

    current_app_mock.logger.debug.side_effect = _debug
    api_client.get('/literature/')


@patch('inspirehep.modules.search.search_factory.current_app')
def test_search_facets_logs(current_app_mock, api_client):
    def _debug(log_output):
        query = {
            "_source": {
                "includes": [
                    "$schema",
                    "abstracts.value",
                    "arxiv_eprints.value",
                    "arxiv_eprints.categories",
                    "authors.affiliations",
                    "authors.full_name",
                    "authors.control_number",
                    "collaborations",
                    "control_number",
                    "citation_count",
                    "dois.value",
                    "earliest_date",
                    "inspire_categories",
                    "number_of_references",
                    "publication_info",
                    "report_numbers",
                    "titles.title"
                ]
            },
            "aggs": {
                "arxiv_categories": {
                    "meta": {
                        "order": 5,
                        "title": "arXiv Category"
                    },
                    "terms": {
                        "field": "facet_arxiv_categories",
                        "size": 20
                    }
                },
                "author": {
                    "meta": {
                        "order": 3,
                        "title": "Author"
                    },
                    "terms": {
                        "field": "facet_author_name",
                        "size": 20
                    }
                },
                "author_count": {
                    "meta": {
                        "order": 2,
                        "title": "Number of authors"
                    },
                    "range": {
                        "field": "author_count",
                        "ranges": [
                            {
                                "from": 1,
                                "key": "10 authors or less",
                                "to": 10
                            }
                        ]
                    }
                },
                "doc_type": {
                    "meta": {
                        "order": 7,
                        "title": "Document Type"
                    },
                    "terms": {
                        "field": "facet_inspire_doc_type",
                        "size": 20
                    }
                },
                "earliest_date": {
                    "date_histogram": {
                        "field": "earliest_date",
                        "format": "yyyy",
                        "interval": "year",
                        "min_doc_count": 1
                    },
                    "meta": {
                        "order": 1,
                        "title": "Date"
                    }
                },
                "experiment": {
                    "meta": {
                        "order": 6,
                        "title": "Experiment"
                    },
                    "terms": {
                        "field": "facet_experiment",
                        "size": 20
                    }
                },
                "subject": {
                    "meta": {
                        "order": 4,
                        "title": "Subject"
                    },
                    "terms": {
                        "field": "facet_inspire_categories",
                        "size": 20
                    }
                }
            },
            "query": {
                "bool": {
                    "filter": [
                        {
                            "match": {
                                "_collections": "Literature"
                            }
                        }
                    ],
                    "minimum_should_match": "0<1",
                    "must": [
                        {
                            "match_all": {}
                        }
                    ]
                }
            }
        }

        assert query == json.loads(log_output)

    current_app_mock.logger.debug.side_effect = _debug
    api_client.get('/literature/facets')


@patch('inspirehep.modules.search.search_factory.current_app')
def test_search_facets_logs_with_query(current_app_mock, api_client):
    def _debug(log_output):
        query = {
            "_source": {
                "includes": [
                    "$schema",
                    "abstracts.value",
                    "arxiv_eprints.value",
                    "arxiv_eprints.categories",
                    "authors.affiliations",
                    "authors.full_name",
                    "authors.control_number",
                    "collaborations",
                    "control_number",
                    "citation_count",
                    "dois.value",
                    "earliest_date",
                    "inspire_categories",
                    "number_of_references",
                    "publication_info",
                    "report_numbers",
                    "titles.title"
                ]
            },
            "aggs": {
                "arxiv_categories": {
                    "meta": {
                        "order": 5,
                        "title": "arXiv Category"
                    },
                    "terms": {
                        "field": "facet_arxiv_categories",
                        "size": 20
                    }
                },
                "author": {
                    "meta": {
                        "order": 3,
                        "title": "Author"
                    },
                    "terms": {
                        "field": "facet_author_name",
                        "size": 20
                    }
                },
                "author_count": {
                    "meta": {
                        "order": 2,
                        "title": "Number of authors"
                    },
                    "range": {
                        "field": "author_count",
                        "ranges": [
                            {
                                "from": 1,
                                "key": "10 authors or less",
                                "to": 10
                            }
                        ]
                    }
                },
                "doc_type": {
                    "meta": {
                        "order": 7,
                        "title": "Document Type"
                    },
                    "terms": {
                        "field": "facet_inspire_doc_type",
                        "size": 20
                    }
                },
                "earliest_date": {
                    "date_histogram": {
                        "field": "earliest_date",
                        "format": "yyyy",
                        "interval": "year",
                        "min_doc_count": 1
                    },
                    "meta": {
                        "order": 1,
                        "title": "Date"
                    }
                },
                "experiment": {
                    "meta": {
                        "order": 6,
                        "title": "Experiment"
                    },
                    "terms": {
                        "field": "facet_experiment",
                        "size": 20
                    }
                },
                "subject": {
                    "meta": {
                        "order": 4,
                        "title": "Subject"
                    },
                    "terms": {
                        "field": "facet_inspire_categories",
                        "size": 20
                    }
                }
            },
            "query": {
                "bool": {
                    "filter": [
                        {
                            "match": {
                                "_collections": "Literature"
                            }
                        }
                    ],
                    "minimum_should_match": "0<1",
                    "must": [
                        {
                            "match": {
                                "_all": {
                                    "operator": "and",
                                    "query": "test query"
                                }
                            }
                        }
                    ]
                }
            }
        }
        assert query == json.loads(log_output)

    current_app_mock.logger.debug.side_effect = _debug
    api_client.get('/literature/facets?q=test query')


def test_search_facets_with_facet_name(isolated_api):
    config = {
        'RECORDS_REST_FACETS': {
            'defenders': {
                'aggs': {
                    'jessica-jones': {
                        'terms': {
                            'field': 'defenders',
                            'size': 20,
                        },
                    },
                },
            },
        },
    }

    with isolated_api.test_client() as client, patch.dict(isolated_api.config, config):
        response = client.get('/literature/facets?facet=defenders')
        response_data = json.loads(response.data)
        assert 'jessica-jones' in response_data['aggregations']


def test_search_facets_without_facet_name(isolated_api):
    config = {
        'RECORDS_REST_FACETS': {
            'defenders': {
                'aggs': {
                    'jessica-jones': {
                        'terms': {
                            'field': 'defenders',
                            'size': 20,
                        },
                    },
                },
            },
        },
    }

    with isolated_api.test_client() as client, patch.dict(isolated_api.config, config):
        response = client.get('/literature/facets')
        response_data = json.loads(response.data)
        assert 'jessica-jones' not in response_data['aggregations']

