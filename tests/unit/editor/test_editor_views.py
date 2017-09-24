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

import os
import json

import pkg_resources
import requests_mock

from inspire_schemas.api import load_schema, validate
from inspire_utils.record import get_value


def test_authorlist_text(api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    response = api_client.post(
        '/editor/authorlist/text',
        content_type='application/json',
        data=json.dumps({
            'text': (
                'F. Lastname1, F.M. Otherlastname1,2\n'
                '\n'
                '1 CERN\n'
                '2 Otheraffiliation'
            )
        })
    )

    assert response.status_code == 200

    expected = {
        'authors': [
            {
                'full_name': 'Lastname, F.',
                'raw_affiliations': [
                    {'value': 'CERN'},
                ],
            },
            {
                'full_name': 'Otherlastname, F.M.',
                'raw_affiliations': [
                    {'value': 'CERN'},
                    {'value': 'Otheraffiliation'},
                ],
            },
        ],
    }
    result = json.loads(response.data)

    assert validate(result['authors'], subschema) is None
    assert expected == result


def test_authorlist_text_exception(api_client):
    response = api_client.post(
        '/editor/authorlist/text',
        content_type='application/json',
        data=json.dumps({
            'text': 'A. Einstein, N. Bohr2'
        })
    )

    assert response.status_code == 500

    expected = {
        'message': 'Could not find affiliations',
        'status': 500
    }
    result = json.loads(response.data)

    assert expected == result


def test_refextract_text(api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    response = api_client.post(
        '/editor/refextract/text',
        content_type='application/json',
        data=json.dumps({
            'text': (
                u'J. M. Maldacena. “The Large N Limit of Superconformal Field '
                u'Theories and Supergravity”. Adv. Theor. Math. Phys. 2 (1998), '
                u'pp. 231–252.'
            ),
        }),
    )
    references = json.loads(response.data)

    assert response.status_code == 200
    assert validate(references, subschema) is None
    assert get_value({'references': references}, 'references.reference.publication_info.journal_title')


def test_refextract_url(api_client):
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'https://arxiv.org/pdf/1612.06414.pdf',
            content=pkg_resources.resource_string(
              __name__, os.path.join('fixtures', '1612.06414.pdf')),
        )

        response = api_client.post(
            '/editor/refextract/url',
            content_type='application/json',
            data=json.dumps({
                'url': 'https://arxiv.org/pdf/1612.06414.pdf',
            }),
        )
        references = json.loads(response.data)

    assert response.status_code == 200
    assert validate(references, subschema) is None
    assert get_value({'references': references}, 'references.reference.publication_info.journal_title')
