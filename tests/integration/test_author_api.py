# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

import six


def test_author_main_path(app):
    """This test checks only if the status cod and author profile are correct.
    The functionality is provided by invenio-records-rest, which is not the
    subject of these tests.
    """
    with app.test_client() as client:
        assert client.get(
            '/api/authors/983220').status_code == 200

        request = json.loads(
            client.get('/api/authors/983220').data)

        assert request['id'] == 983220


def test_author_citations_endpoint(app):
    """This test checks for the total count of objects and the availability
    of required keys and their type.
    """
    with app.test_client() as client:
        assert client.get(
            '/api/authors/983220/citations').status_code == 200

        request = json.loads(
            client.get('/api/authors/983220/citations').data)

        assert len(request) == 197
        assert isinstance(request[0]['date'], six.string_types)
        assert isinstance(request[0]['self_citation'], bool)
        assert isinstance(request[0]['citee']['record']['$ref'],
                          six.string_types)
        assert isinstance(request[0]['citer']['record']['$ref'],
                          six.string_types)
        assert isinstance(request[0]['published_paper'], bool)


def test_author_coauthors_endpoint(app):
    """This test checks for the total count of objects and the availability
    of required keys and their type.
    """
    with app.test_client() as client:
        assert client.get(
            '/api/authors/983220/coauthors').status_code == 200

        request = json.loads(
            client.get('/api/authors/983220/coauthors').data)

        assert len(request) == 100
        assert isinstance(request[0]['count'], int)
        assert isinstance(request[0]['record']['$ref'], six.string_types)
        assert isinstance(request[0]['id'], int)
        assert isinstance(request[0]['full_name'], six.string_types)


def test_author_publications_endpoint(app):
    """This test checks for the total count of objects and the availability
    of required keys and their type.
    """
    with app.test_client() as client:
        assert client.get(
            '/api/authors/983220/publications').status_code == 200

        request = json.loads(
            client.get('/api/authors/983220/publications').data)

        assert len(request) == 30
        assert isinstance(request[0]['title'], six.string_types)
        assert isinstance(request[0]['collaborations'][0], six.string_types)
        assert isinstance(request[0]['journal']['record']['$ref'],
                          six.string_types)
        assert isinstance(request[0]['citations'], int)
        assert isinstance(request[0]['date'], six.string_types)
        assert isinstance(request[0]['type'], six.string_types)
        assert isinstance(request[0]['id'], int)


def test_author_stats_endpoint(app):
    """This test checks for the total count of objects and the availability
    of required keys and their type.
    """
    with app.test_client() as client:
        assert client.get(
            '/api/authors/983220/stats').status_code == 200

        request = json.loads(
            client.get('/api/authors/983220/stats').data)

        assert isinstance(request['fields'][0], six.string_types)
        assert isinstance(request['hindex'], int)
        assert isinstance(request['i10index'], int)
        assert isinstance(request['citations'], int)
        assert isinstance(request['publications'], int)

        assert len(request['keywords']) == 25
        assert isinstance(request['keywords'][0]['count'], int)
        assert isinstance(request['keywords'][0]['keyword'], six.string_types)

        assert isinstance(request['types'], dict)
