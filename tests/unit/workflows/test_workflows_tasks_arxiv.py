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

import pkg_resources
from mock import patch
from shutil import rmtree
from tempfile import mkdtemp

from inspire_schemas.utils import load_schema
from inspirehep.dojson.utils import validate
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_derive_inspire_categories
)

from mocks import AttrDict, MockEng, MockFiles, MockObj


def test_arxiv_derive_inspire_categories():
    schema = load_schema('hep')
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']
    inspire_categories_schema = schema['properties']['inspire_categories']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-th',
                ],
                'value': '1605.03898',
            },
        ],
    }  # literature/1458300
    extra_data = {}
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert arxiv_derive_inspire_categories(obj, eng) is None

    expected = [
        {
            'source': 'arxiv',
            'term': 'Theory-Nucl',
        },
    ]
    result = obj.data['inspire_categories']

    assert validate(result, inspire_categories_schema) is None
    assert expected == result


def test_arxiv_derive_inspire_categories_appends_categories_with_different_source():
    schema = load_schema('hep')
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']
    inspire_categories_schema = schema['properties']['inspire_categories']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-th',
                ],
                'value': '1605.03898',
            },
        ],
        'inspire_categories': [
            {
                'source': 'undefined',
                'term': 'Theory-Nucl',
            },
        ],
    }  # literature/1458300
    extra_data = {}
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None
    assert validate(data['inspire_categories'], inspire_categories_schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert arxiv_derive_inspire_categories(obj, eng) is None

    expected = [
        {
            'source': 'undefined',
            'term': 'Theory-Nucl',
        },
        {
            'source': 'arxiv',
            'term': 'Theory-Nucl',
        },
    ]
    result = obj.data['inspire_categories']

    assert validate(result, inspire_categories_schema) is None
    assert expected == result


def test_arxiv_derive_inspire_categories_does_nothing_with_existing_categories():
    schema = load_schema('hep')
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']
    inspire_categories_schema = schema['properties']['inspire_categories']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-th',
                ],
                'value': '1605.03898',
            },
        ],
        'inspire_categories': [
            {
                'source': 'arxiv',
                'term': 'Theory-Nucl',
            },
        ],
    }  # synthetic data
    extra_data = {}
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None
    assert validate(data['inspire_categories'], inspire_categories_schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert arxiv_derive_inspire_categories(obj, eng) is None

    expected = [
        {
            'source': 'arxiv',
            'term': 'Theory-Nucl',
        },
    ]
    result = obj.data['inspire_categories']

    assert validate(result, inspire_categories_schema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.arxiv.os')
def test_arxiv_author_list_handles_auto_ignore_comment(mock_os):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1703.09986.tar.gz'))

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '1703.09986',
            },
        ],
    }  # record/1519995
    extra_data = {}
    files = MockFiles({
        '1703.09986.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    try:
        temporary_dir = mkdtemp()
        mock_os.path.abspath.return_value = temporary_dir

        assert default_arxiv_author_list(obj, eng) is None
    finally:
        rmtree(temporary_dir)
