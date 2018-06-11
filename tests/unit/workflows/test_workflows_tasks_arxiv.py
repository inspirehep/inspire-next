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
import requests_mock
from mock import patch
from wand.exceptions import DelegateError

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_derive_inspire_categories,
    arxiv_package_download,
    arxiv_plot_extract,
    populate_arxiv_document,
)
from plotextractor.errors import InvalidTarball

from mocks import AttrDict, MockEng, MockFiles, MockObj


def test_populate_arxiv_document():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

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

        assert populate_arxiv_document(obj, eng) is None

        expected = [
            {
                'key': '1605.03844.pdf',
                'fulltext': True,
                'hidden': True,
                'material': 'preprint',
                'original_url': 'http://export.arxiv.org/pdf/1605.03844',
                'url': 'http://export.arxiv.org/pdf/1605.03844',
                'source': 'arxiv',
            },
        ]
        result = obj.data['documents']

        assert expected == result


def test_populate_arxiv_document_does_not_duplicate_files_if_called_multiple_times():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

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

        assert populate_arxiv_document(obj, eng) is None
        assert populate_arxiv_document(obj, eng) is None

        expected = [
            {
                'key': '1605.03844.pdf',
                'fulltext': True,
                'hidden': True,
                'material': 'preprint',
                'original_url': 'http://export.arxiv.org/pdf/1605.03844',
                'url': 'http://export.arxiv.org/pdf/1605.03844',
                'source': 'arxiv',
            },
        ]
        result = obj.data['documents']

        assert expected == result


def test_populate_arxiv_document_logs_on_pdf_not_existing():
    response500 = {'content': '', 'status_code': 500}
    response200 = {
        'content': pkg_resources.resource_string(
            __name__, os.path.join('fixtures', '1707.02785.html')),
        'status_code': 200,
    }
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(
            'http://export.arxiv.org/pdf/1707.02785',
            (response200,),
        )
        requests_mocker.get(
            'http://arxiv.org/pdf/1707.02785',
            (response500,),
        )
        schema = load_schema('hep')
        subschema = schema['properties']['arxiv_eprints']

        data = {
            'arxiv_eprints': [
                {
                    'categories': [
                        'cs.CV',
                    ],
                    'value': '1707.02785',
                },
            ],
        }  # literature/1458302
        extra_data = {}
        files = MockFiles({})
        assert validate(data['arxiv_eprints'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert populate_arxiv_document(obj, eng) is None

        expected = 'No PDF is available for 1707.02785'
        result = obj.log._info.getvalue()

        assert expected == result


def test_populate_arxiv_document_alternative_url():
    response500 = {'content': '', 'status_code': 500}
    response200 = {
        'content': pkg_resources.resource_string(
            __name__, os.path.join('fixtures', '1605.03814.pdf')),
        'status_code': 200,
    }
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(
            'http://export.arxiv.org/pdf/1605.03814',
            (response500,),
        )
        requests_mocker.get(
            'http://arxiv.org/pdf/1605.03814',
            (response200,)
        )
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

        assert populate_arxiv_document(obj, eng) is None

        expected_url = 'http://arxiv.org/pdf/1605.03814'
        expected_documents = [
            {
                'key': '1605.03814.pdf',
                'fulltext': True,
                'hidden': True,
                'material': 'preprint',
                'original_url': expected_url,
                'url': expected_url,
                'source': 'arxiv',
            }
        ]
        documents = obj.data['documents']
        assert expected_documents == documents


def test_populate_arxiv_document_retries_on_error():
    response500 = {'content': '', 'status_code': 500}
    response200 = {
        'content': pkg_resources.resource_string(
            __name__, os.path.join('fixtures', '1605.03814.pdf')),
        'status_code': 200,
    }
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(
            'http://export.arxiv.org/pdf/1605.03814',
            (response500, response200),
        )
        requests_mocker.get(
            'http://arxiv.org/pdf/1605.03814',
            (response500,)
        )
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

        assert populate_arxiv_document(obj, eng) is None

        expected_url = 'http://export.arxiv.org/pdf/1605.03814'
        expected_documents = [
            {
                'key': '1605.03814.pdf',
                'fulltext': True,
                'hidden': True,
                'material': 'preprint',
                'original_url': expected_url,
                'url': expected_url,
                'source': 'arxiv',
            }
        ]
        documents = obj.data['documents']
        assert expected_documents == documents


def test_arxiv_package_download_logs_on_success():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/e-print/1605.03959',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03959.tar.gz')),
        )

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


def test_arxiv_package_download_logs_on_error():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/e-print/1605.03951',
            status_code=500,
        )

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
def test_arxiv_plot_extract_populates_files_with_plots(mock_os, tmpdir):
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

    temporary_dir = tmpdir.mkdir('plots')
    mock_os.path.abspath.return_value = str(temporary_dir)

    assert arxiv_plot_extract(obj, eng) is None

    expected = [{
        'url': '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/figure1.png',
        'source': 'arxiv',
        'material': 'preprint',
        'key': 'figure1.png',
        'caption': 'Difference (in MeV) between the theoretical and experimental masses for the 2027 selected nuclei as a function of the mass number.'
    }]
    result = obj.data['figures']

    assert expected == result

    expected = 'Added 1 plots.'
    result = obj.log._info.getvalue()

    assert expected == result


@patch('plotextractor.api.os')
def test_arxiv_plot_extract_is_safe_to_rerun(mock_os, tmpdir):
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

    temporary_dir = tmpdir.mkdir('plots')
    mock_os.path.abspath.return_value = str(temporary_dir)

    for _ in range(2):
        assert arxiv_plot_extract(obj, eng) is None

        expected_figures = [{
            'url': '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/figure1.png',
            'source': 'arxiv',
            'material': 'preprint',
            'key': 'figure1.png',
            'caption': 'Difference (in MeV) between the theoretical and experimental masses for the 2027 selected nuclei as a function of the mass number.'
        }]
        result = obj.data['figures']

        assert expected_figures == result

        expected_files = ['0804.1873.tar.gz', 'figure1.png']

        assert expected_files == obj.files.keys


@patch('plotextractor.api.os')
def test_arxiv_plot_extract_handles_duplicate_plot_names(mock_os, tmpdir):
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1711.10662.tar.gz'))

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'cs.CV',
                ],
                'value': '1711.10662',
            },
        ],
    }  # holdingpen/807096
    extra_data = {}
    files = MockFiles({
        '1711.10662.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            }),
        }),
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    temporary_dir = tmpdir.mkdir('plots')
    mock_os.path.abspath.return_value = str(temporary_dir)

    assert arxiv_plot_extract(obj, eng) is None

    assert len(obj.data['figures']) == 66
    assert len(obj.files.keys) == 67


@patch('inspirehep.modules.workflows.tasks.arxiv.process_tarball')
def test_arxiv_plot_extract_logs_when_tarball_is_invalid(mock_process_tarball):
    mock_process_tarball.side_effect = InvalidTarball

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1612.00626'))

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
                'uri': filename,
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_plot_extract(obj, eng) is None
    assert '1612.00626' in obj.log._info.getvalue()


@patch('inspirehep.modules.workflows.tasks.arxiv.process_tarball')
def test_arxiv_plot_extract_logs_when_images_are_invalid(mock_process_tarball):
    mock_process_tarball.side_effect = DelegateError

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1612.00624'))

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
                'uri': filename,
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_plot_extract(obj, eng) is None
    assert '1612.00624' in obj.log._error.getvalue()


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


def test_arxiv_author_list_handles_auto_ignore_comment():
    schema = load_schema('hep')

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1703.09986.tar.gz'))

    eprints_subschema = schema['properties']['arxiv_eprints']
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
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '1703.09986.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [{'value': 'Yerevan Phys. Inst.'}],
            'ids': [
                {'value': 'INSPIRE-00312131', 'schema': 'INSPIRE ID'},
                {'value': 'CERN-432142', 'schema': 'CERN'},
            ],
            'full_name': 'Sirunyan, Albert M',
        },
    ]
    validate(expected_authors, authors_subschema)

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    assert default_arxiv_author_list(obj, eng) is None
    assert obj.data.get('authors') == expected_authors


def test_arxiv_author_list_only_overrides_authors():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1703.09986.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '1703.09986',
            },
        ],
    }  # record/1519995
    validate(data['arxiv_eprints'], subschema)

    extra_data = {}
    files = MockFiles({
        '1703.09986.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()
    default_arxiv_author_list(obj, eng)

    assert 'arxiv_eprints' in obj.data
    assert obj.data['arxiv_eprints'] == data['arxiv_eprints']
    assert '$schema' in obj.data
    assert obj.data['$schema'] == data['$schema']


@patch('inspirehep.modules.workflows.tasks.arxiv.untar')
def test_arxiv_author_list_logs_on_error(mock_untar):
    mock_untar.side_effect = InvalidTarball

    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1605.07707'))

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
                'uri': filename,
            })
        })
    })
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    assert default_arxiv_author_list(obj, eng) is None
    assert '1605.07707' in obj.log._info.getvalue()


def test_arxiv_author_list_handles_multiple_author_xml_files():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1703.09986.multiple_author_lists.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '1703.09986',
            },
        ],
    }  # record/1519995
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '1703.09986.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()
    default_arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [{'value': 'Yerevan Phys. Inst.'}],
            'ids': [
                {'value': 'INSPIRE-00312131', 'schema': 'INSPIRE ID'},
                {'value': 'CERN-432142', 'schema': 'CERN'},
            ],
            'full_name': 'Sirunyan, Albert M',
        },
        {
            'affiliations': [{'value': 'Yerevan Phys. Inst.'}],
            'ids': [
                {'value': 'INSPIRE-00312132', 'schema': 'INSPIRE ID'},
                {'value': 'CERN-432143', 'schema': 'CERN'},
            ],
            'full_name': 'Weary, Jake',
        }
    ]
    validate(expected_authors, authors_subschema)

    assert obj.data.get('authors') == expected_authors


def test_arxiv_author_list_does_not_produce_latex():
    schema = load_schema('hep')

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1802.03388.tar.gz'))

    eprints_subschema = schema['properties']['arxiv_eprints']
    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '1802.03388',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '1802.03388.tar.gz': AttrDict({'file': AttrDict({'uri': filename})})
    })

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [{'value': 'Lund U.'}],
            'ids': [
                {
                    'value': 'INSPIRE-00061248',
                    'schema': 'INSPIRE ID'
                }
            ],
            'full_name': u'Åkesson, Torsten Paul Ake'
        },
    ]
    validate(expected_authors, authors_subschema)

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    default_arxiv_author_list = arxiv_author_list()

    assert default_arxiv_author_list(obj, eng) is None
    assert obj.data.get('authors') == expected_authors
