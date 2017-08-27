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


def test_literature_is_there(app_client):
    assert app_client.get('/literature').status_code == 200
    assert app_client.get('/collection/literature').status_code == 200
    assert app_client.get('/').status_code == 200


def test_authors_is_there(app_client):
    assert app_client.get('/authors').status_code == 200
    assert app_client.get('/collection/authors').status_code == 200


def test_conferences_is_there(app_client):
    assert app_client.get('/conferences').status_code == 200


def test_jobs_redirects_to_search(app_client):
    response = app_client.get('/jobs')

    assert response.status_code == 302
    assert response.location == 'http://localhost:5000/search?cc=jobs'


def test_institutions_is_there(app_client):
    assert app_client.get('/institutions').status_code == 200


def test_experiments_is_there(app_client):
    assert app_client.get('/experiments').status_code == 200


def test_journals_is_there(app_client):
    assert app_client.get('/journals').status_code == 200


def test_data_is_there(app_client):
    assert app_client.get('/data').status_code == 200


def test_ping_responds_ok(app_client):
    assert app_client.get('/ping').data == 'OK'


def test_record_url_redirects_to_literature(app_client):
    response = app_client.get('/record/4328')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/literature/4328'


def test_record_url_redirects_to_authors(app_client):
    response = app_client.get('/record/993224')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/authors/993224'


def test_record_url_returns_404_when_there_is_no_corresponding_record(app_client):
    assert app_client.get('/record/0').status_code == 404


def test_author_new_form_redirects_without_bai(app_client):
    response = app_client.get('/author/new')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/authors/new'


def test_author_new_form_redirects_with_bai(app_client):
    response = app_client.get('/author/new?bai=foo')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/authors/new?bai=foo'


def test_author_update_form_redirects_to_new_without_recid(app_client):
    response = app_client.get('/author/update')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/authors/new'


def test_author_update_form_redirects_with_recid(app_client):
    response = app_client.get('/author/update?recid=123')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/authors/123/update'


def test_literature_new_form_redirects(app_client):
    response = app_client.get('/submit/literature/create')

    assert response.status_code == 301
    assert response.location == 'http://localhost:5000/literature/new'
