# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""ORCID util tests."""

from __future__ import absolute_import, division, print_function

import pytest

from inspire_dojson.utils import get_record_ref
from inspire_schemas.api import validate
from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.modules.orcid.utils import _get_api_url_for_recid, get_orcids_for_push


@pytest.fixture(scope='function')
def author_in_isolated_app(isolated_app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        '_collections': ['Authors'],
        'control_number': 123456789,  # FIXME remove when there is an easy way to insert new records
        'ids': [
            {
                'schema': 'INSPIRE BAI',
                'value': 'J.Smith.1',
            },
            {
                'schema': 'ORCID',
                'value': '0000-0002-1825-0097',
            },
        ],
        'name': {'value': 'Smith, John'},
    }

    assert validate(record, 'authors') is None

    yield record_insert_or_replace(record)['control_number']


@pytest.mark.parametrize(
    'server_name,api_endpoint,recid,expected',
    [
        ('inspirehep.net', '/api/literature/', '123', 'http://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net', '/api/literature/', '123', 'http://inspirehep.net/api/literature/123'),
        ('https://inspirehep.net', '/api/literature/', '123', 'https://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net', 'api/literature', '123', 'http://inspirehep.net/api/literature/123'),
        ('http://inspirehep.net/', '/api/literature', '123', 'http://inspirehep.net/api/literature/123'),
    ]
)
def test_get_api_url_for_recid(server_name, api_endpoint, recid, expected):
    result = _get_api_url_for_recid(server_name, api_endpoint, recid)
    assert expected == result


def test_orcids_for_push_no_authors(isolated_app):
    record = {
        '_collections': ['Literature'],
        'corporate_author': ['Corporate Author'],
        'document_type': ['article'],
        'titles': [
            {'title': 'A paper with no authors'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_no_orcids(isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_orcid_in_paper(isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                    {
                        'schema': 'ORCID',
                        'value': '0000-0002-1825-0097',
                    },
                ],
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == ['0000-0002-1825-0097']


def test_orcids_for_push_orcid_in_author_no_claim(author_in_isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
                'record': get_record_ref(author_in_isolated_app, 'authors'),
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_orcid_in_author_with_claim(author_in_isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
                'record': get_record_ref(author_in_isolated_app, 'authors'),
                'curated_relation': True,
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == ['0000-0002-1825-0097']
