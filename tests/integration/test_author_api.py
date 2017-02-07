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

import json

from jsonschema import validate


def test_api_authors_root(app):
    with app.test_client() as client:
        response = client.get('/api/authors/983220')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json['id'] == 983220


def test_api_authors_citations(app):
    schema = {
        'items': {
            'properties': {
                'citee': {
                    'properties': {
                        'id': {'type': 'integer'},
                        'record': {
                            'properties': {'$ref': {'type': 'string'}},
                            'type': 'object'
                        }
                    },
                    'type': 'object'
                },
                'citers': {
                    'items': {
                        'properties': {
                            'citer': {
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'record': {
                                        'properties': {'$ref': {'type': 'string'}},
                                        'type': 'object'
                                    }
                                },
                                'type': 'object'
                            },
                            'date': {
                                'format': 'date',
                                'type': 'string'
                            },
                            'published_paper': {'type': 'boolean'},
                            'self_citation': {'type': 'boolean'}
                        },
                        'type': 'object'
                    },
                    'type': 'array'
                }
            },
            'type': 'object'
        },
        'type': 'array'
    }

    with app.test_client() as client:
        response = client.get('/api/authors/1061000/citations')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert validate(response_json, schema) is None
        assert len(response_json) == 2


def test_api_authors_coauthors(app):
    schema = {
        'items': {
            'properties': {
                'count': {'type': 'integer'},
                'full_name': {'type': 'string'},
                'id': {'type': 'integer'},
                'record': {
                    'properties': {'$ref': {'type': 'string'}},
                    'type': 'object'
                }
            },
            'type': 'object'
        },
        'type': 'array'
    }

    with app.test_client() as client:
        response = client.get('/api/authors/1061000/coauthors')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert validate(response_json, schema) is None
        assert len(response_json) == 10


def test_api_authors_publications(app):
    schema = {
        'items': {
            'properties': {
                'collaborations': {
                    'items': {'type': 'string'},
                    'type': 'array'
                },
                'citations': {'type': 'integer'},
                'date': {
                    'format': 'date',
                    'type': 'string'
                },
                'id': {'type': 'integer'},
                'journal': {
                    'properties': {
                        'id': {'type': 'integer'},
                        'record': {
                            'properties': {'$ref': {'type': 'string'}},
                            'type': 'object'
                        },
                        'title': {'type': 'string'}
                    },
                    'type': 'object'
                },
                'title': {'type': 'string'},
                'type': {'type': 'string'}
            },
            'type': 'object'
        },
        'type': 'array'
    }

    with app.test_client() as client:
        response = client.get('/api/authors/1061000/publications')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert validate(response_json, schema) is None
        assert len(response_json) == 2


def test_api_author_stats(app):
    schema = {
        'properties': {
            'citations': {'type': 'integer'},
            'fields': {
                'items': {'type': 'string'},
                'type': 'array',
            },
            'hindex': {'type': 'integer'},
            'i10index': {'type': 'integer'},
            'keywords': {
                'items': {
                    'properties': {
                        'count': {'type': 'integer'},
                        'keyword': {'type': 'string'}
                    },
                    'type': 'object'
                },
                'type': 'array'
            },
            'publications': {'type': 'integer'},
            'types': {'type': 'object'},
        },
        'type': 'object'
    }

    with app.test_client() as client:
        response = client.get('/api/authors/1061000/stats')

        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert validate(response_json, schema) is None
        assert len(response_json['keywords']) == 12
