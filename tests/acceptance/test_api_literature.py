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

"""Tests for the Literature API.

The Literature API has a single endpoint:

    /api/literature/<N>

where <N> is the id of the record you want to query. By sending the appropriate
Accept HTTP header you can obtain the different representations of the record.
We currently support the following content-types:

    application/json (default)
    application/x-bibtex
    application/x-latexeu
    application/x-latexus
    application/x-cvformatlatex
    application/x-cvformathtml
    application/x-cvformattext

"""

from __future__ import absolute_import, division, print_function

import json

import requests


def test_api_literature_json(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/json'},
    )

    expected = 'Partial Symmetries of Weak Interactions'
    result = json.loads(response.data)

    assert expected == result['titles'][0]['title']


def test_api_literature_bibtex(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-bibtex'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


def test_api_literature_latexeu(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-latexeu'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


def test_api_literature_latexus(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-latexus'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


def test_api_literature_cvformatlatex(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-cvformatlatex'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


def test_api_literature_cvformathtml(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-cvformathtml'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


def test_api_literature_cvformattext(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-cvformattext'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result


#
# Private APIs
#

def test_api_literature_impactgraph_json(live_server):
    """TODO."""
    response = requests.get(
        '/api/literature/4328',
        headers={'Accept': 'application/x-impact.graph+json'},
    )

    expected = 'TODO'
    result = json.loads(response.data)

    assert expected == result
