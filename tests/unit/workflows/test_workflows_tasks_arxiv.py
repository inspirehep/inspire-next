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

import httpretty
import pkg_resources
import pytest
from mock import patch
from shutil import rmtree
from tempfile import mkdtemp
from wand.exceptions import DelegateError

from inspire_dojson.utils import validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_derive_inspire_categories,
    arxiv_fulltext_download,
    arxiv_package_download,
    arxiv_plot_extract,
)
from inspirehep.modules.workflows.errors import DownloadError
from plotextractor.errors import InvalidTarball

from mocks import AttrDict, MockEng, MockFiles, MockObj


@pytest.mark.httpretty
def test_arxiv_fulltext_download_logs_on_success():
    httpretty.register_uri(
        httpretty.GET, 'http://export.arxiv.org/pdf/1605.03844',
        body=pkg_resources.resource_string(
            __name__, os.path.join('fixtures', '1605.03844.pdf')))

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'physics.ins-det',
                ],
                'value': '1605.03844',
            },
        ],
    }  # literature/1458302
    extra_data = {}
    files = MockFiles({})
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_fulltext_download(obj, eng) is None

    expected = 'PDF retrieved from arXiv for 1605.03844'
    result = obj.log._info.getvalue()

    assert expected == result


@pytest.mark.httpretty
def test_arxiv_fulltext_download_logs_on_error():
    httpretty.register_uri(
        httpretty.GET, 'http://export.arxiv.org/pdf/1605.03814', status=500)

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '1605.03814',
            },
        ],
    }  # literature/1458270
    extra_data = {}
    files = MockFiles({})
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    with pytest.raises(DownloadError) as excinfo:
        arxiv_fulltext_download(obj, eng)

    expected = 'http://export.arxiv.org/pdf/1605.03814 is not serving a PDF file.'
    result = str(excinfo.value)

    assert expected == result


@pytest.mark.httpretty
def test_arxiv_package_download_logs_on_success():
    httpretty.register_uri(
        httpretty.GET, 'http://export.arxiv.org/e-print/1605.03959',
        body=pkg_resources.resource_string(
            __name__, os.path.join('fixtures', '1605.03959.tar.gz')))

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                    'cond-mat.stat-mech',
                    'cond-mat.str-el',
                ],
                'value': '1605.03959',
            },
        ],
    }  # literature/1458968
    extra_data = {}
    files = MockFiles({})
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_package_download(obj, eng) is None

    expected = 'Tarball retrieved from arXiv for 1605.03959'
    result = obj.log._info.getvalue()

    assert expected == result


@pytest.mark.httpretty
def test_arxiv_package_download_logs_on_error():
    httpretty.register_uri(
        httpretty.GET, 'http://export.arxiv.org/e-print/1605.03951', status=500)

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.HE',
                ],
                'value': '1605.03951',
            },
        ],
    }  # literature/1458254
    extra_data = {}
    files = MockFiles({})
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_package_download(obj, eng) is None

    expected = 'Cannot retrieve tarball from arXiv for 1605.03951'
    result = obj.log._error.getvalue()

    assert expected == result


@patch('plotextractor.api.os')
def test_arxiv_plot_extract_populates_files_with_plots(mock_os):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '0804.1873.tar.gz'))

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'nucl-ex',
                ],
                'value': '0804.1873',
            },
        ],
    }  # literature/783246
    extra_data = {}
    files = MockFiles({
        '0804.1873.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            }),
        }),
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    try:
        temporary_dir = mkdtemp()
        mock_os.path.abspath.return_value = temporary_dir

        assert arxiv_plot_extract(obj, eng) is None

        expected = obj.files['figure1']['description']
        result = (
            '00000 Difference (in MeV) between the theoretical and '
            'experimental masses for the 2027 selected nuclei as a '
            'function of the mass number.'
        )

        assert expected == result

        expected = 'Added 1 plots.'
        result = obj.log._info.getvalue()

        assert expected == result
    finally:
        rmtree(temporary_dir)


@patch('inspirehep.modules.workflows.tasks.arxiv.process_tarball')
def test_arxiv_plot_extract_logs_when_tarball_is_invalid(mock_process_tarball):
    mock_process_tarball.side_effect = InvalidTarball

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'physics.ins-det',
                ],
                'value': '1612.00626',
            },
        ],
    }  # synthetic data
    extra_data = {}
    files = MockFiles({
        '1612.00626.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': 'http://export.arxiv.org/e-print/1612.00626',
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_plot_extract(obj, eng) is None

    expected = 'Invalid tarball http://export.arxiv.org/e-print/1612.00626'
    result = obj.log._error.getvalue()

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.arxiv.process_tarball')
def test_arxiv_plot_extract_logs_when_images_are_invalid(mock_process_tarball):
    mock_process_tarball.side_effect = DelegateError

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'physics.ins-det',
                ],
                'value': '1612.00624',
            },
        ],
    }  # synthetic data
    extra_data = {}
    files = MockFiles({
        '1612.00624.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': 'http://export.arxiv.org/e-print/1612.00624',
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_plot_extract(obj, eng) is None

    expected = 'Error extracting plots. Report and skip.'
    result = obj.log._error.getvalue()

    assert expected == result


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

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    try:
        temporary_dir = mkdtemp()
        mock_os.path.abspath.return_value = temporary_dir

        assert default_arxiv_author_list(obj, eng) is None
    finally:
        rmtree(temporary_dir)


@patch('inspirehep.modules.workflows.tasks.arxiv.untar')
@patch('inspirehep.modules.workflows.tasks.arxiv.os')
def test_arxiv_author_list_logs_on_error(mock_os, mock_untar):
    mock_untar.side_effect = InvalidTarball

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': '1605.07707',
            },
        ],
    }  # synthethic data
    extra_data = {}
    files = MockFiles({
        '1605.07707.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': 'http://export.arxiv.org/e-print/1605.07707',
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    try:
        temporary_dir = mkdtemp()
        mock_os.path.abspath.return_value = temporary_dir

        assert default_arxiv_author_list(obj, eng) is None

        expected = 'Invalid tarball http://export.arxiv.org/e-print/1605.07707'
        result = obj.log._error.getvalue()

        assert expected == result
    finally:
        rmtree(temporary_dir)
