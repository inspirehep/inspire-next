# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for author bibfield conversion to data model."""

import json
import os

import pytest
import pkg_resources

from inspirehep.dojson.bibfield import author_bibfield


@pytest.fixture
def bibfield():
    return json.loads(pkg_resources.resource_string(
        'tests',
        os.path.join(
            'fixtures',
            'test_author_bibfield.json')
    ))


@pytest.fixture
def author_json(bibfield):
    return author_bibfield.do(bibfield)


def test_status(bibfield, author_json):
    assert (
        bibfield['status'] ==
        author_json['status']
    )


def test_phd_advisors(bibfield, author_json):
    assert (
        bibfield['phd_advisors'][0]['degree_type'] ==
        author_json['phd_advisors'][0]['degree_type']
    )


def test_name(bibfield, author_json):
    assert (
        bibfield['name']['last'] + ', ' +
        bibfield['name']['first'] ==
        author_json['name']['value']
    )
    assert (
        bibfield['name']['status'] ==
        author_json['name']['status']
    )
    assert (
        bibfield['name']['preferred_name'] ==
        author_json['name']['preferred_name']
    )


def test_native_name(bibfield, author_json):
    assert (
        bibfield['native_name'] ==
        author_json['native_name']
    )


def test_positions(bibfield, author_json):
    assert (
        bibfield['positions'][0]['institution'] ==
        author_json['positions'][0]['institution']['name']
    )
    assert (
        bibfield['positions'][0]['rank'] ==
        author_json['positions'][0]['rank']
    )
    assert (
        bibfield['positions'][0]['start_date'] ==
        author_json['positions'][0]['start_date']
    )
    assert (
        bibfield['positions'][0]['end_date'] ==
        author_json['positions'][0]['end_date']
    )
    assert (
        bibfield['positions'][0]['status'] ==
        author_json['positions'][0]['status']
    )


def test_experiments(bibfield, author_json):
    assert (
        bibfield['experiments'][0]['status'] ==
        author_json['experiments'][0]['status']
    )
    assert (
        bibfield['experiments'][0]['start_year'] ==
        author_json['experiments'][0]['start_year']
    )
    assert (
        bibfield['experiments'][0]['end_year'] ==
        author_json['experiments'][0]['end_year']
    )
    assert (
        bibfield['experiments'][0]['name'] ==
        author_json['experiments'][0]['name']
    )


def test_acquisition_source(bibfield, author_json):
    assert (
        bibfield['acquisition_source']['date'] ==
        author_json['acquisition_source']['date']
    )
    assert (
        bibfield['acquisition_source']['method'] ==
        author_json['acquisition_source']['method']
    )
    assert (
        bibfield['acquisition_source']['email'] ==
        author_json['acquisition_source']['email']
    )
    assert (
        bibfield['acquisition_source']['submission_number'] ==
        author_json['acquisition_source']['submission_number']
    )
    assert (
        bibfield['acquisition_source']['source'][0] ==
        author_json['acquisition_source']['source']
    )


def test_ids(bibfield, author_json):
    assert (
        bibfield['ids'][0]['type'] ==
        author_json['ids'][0]['type']
    )
    assert (
        bibfield['ids'][0]['value'] ==
        author_json['ids'][0]['value']
    )


def test_field_categories(bibfield, author_json):
    assert (
        bibfield['field_categories'][0]['name'] ==
        author_json['field_categories'][0]
    )


def test_urls(bibfield, author_json):
    assert (
        bibfield['urls'][0]['value'] ==
        author_json['urls'][0]['value']
    )
    assert (
        bibfield['urls'][0]['description'] ==
        author_json['urls'][0]['description']
    )


def test_collections(bibfield, author_json):
    assert (
        bibfield['collections']['primary'] ==
        author_json['collections'][0]['primary']
    )
    assert (
        bibfield['urls'][0]['description'] ==
        author_json['urls'][0]['description']
    )
