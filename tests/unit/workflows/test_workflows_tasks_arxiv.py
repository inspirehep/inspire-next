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
import requests

import pytest
import pkg_resources
import requests_mock
from mock import patch
from wand.exceptions import DelegateError

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_package_download,
    arxiv_plot_extract,
    populate_arxiv_document,
    extract_authors_from_xml
)
from plotextractor.errors import InvalidTarball
from inspirehep.modules.workflows.errors import DownloadError

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


def side_effect_requests_get(url, params=None, **kwargs):
    raise requests.exceptions.ConnectionError()


@patch('inspirehep.modules.workflows.tasks.arxiv.requests.get')
def test_populate_arxiv_document_retries_on_connection_error(mock_requests_get):
    mock_requests_get.side_effect = side_effect_requests_get

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

    with pytest.raises(DownloadError):
        populate_arxiv_document(obj, eng)

    assert mock_requests_get.call_count == 10


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


def side_effect_open(name, mode=None, buffering=None):
    raise IOError()


@patch('plotextractor.api.os')
def test_arxiv_plot_extract_retries_on_io_error(mock_os, tmpdir):
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

    with pytest.raises(IOError):
        with patch('inspirehep.modules.workflows.tasks.arxiv.open') as mock_open:
            mock_open.side_effect = side_effect_open
            arxiv_plot_extract(obj, eng)
            assert mock_open.call_count == 5


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


@patch('inspirehep.modules.workflows.tasks.arxiv.process_tarball')
def test_arxiv_plot_extract_no_file(mock_process_tarball):

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
    files = MockFiles({})
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_plot_extract(obj, eng) is None
    assert 'No file named=' in obj.log._info.getvalue()
    mock_process_tarball.assert_not_called()


def test_arxiv_author_list_with_missing_tarball():
    schema = load_schema('hep')

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
        'jessica.jones.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': 'alias.investigations',
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    expected_message = \
        'Skipping author list extraction, no tarball with name "1703.09986.tar.gz" found'

    assert arxiv_author_list(obj, eng) is None
    assert expected_message in obj.log._info.getvalue()


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
            'full_name': 'Sirunyan, Albert M.',
        },
    ]
    validate(expected_authors, authors_subschema)

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    assert arxiv_author_list(obj, eng) is None
    assert obj.data['authors'] == expected_authors


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

    arxiv_author_list(obj, eng)

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

    assert arxiv_author_list(obj, eng) is None
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

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [{'value': 'Yerevan Phys. Inst.'}],
            'ids': [
                {'value': 'INSPIRE-00312131', 'schema': 'INSPIRE ID'},
                {'value': 'CERN-432142', 'schema': 'CERN'},
            ],
            'full_name': 'Sirunyan, Albert M.',
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

    assert obj.data['authors'] == expected_authors


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
            'affiliations': [{'value': u'Lund U.'}],
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

    assert arxiv_author_list(obj, eng) is None
    assert obj.data['authors'] == expected_authors


def test_arxiv_author_test_identifiers():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2203.01808.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2203.01808',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2203.01808.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [{'value': u'Marseille, CPPM'}],
            'ids': [
                {'value': 'INSPIRE-00210391', 'schema': u'INSPIRE ID'},
                {'value': '0000-0002-6665-4934', 'schema': 'ORCID'},
            ],
            'full_name': u'Aad, Georges',
            'affiliations_identifiers': [
                {'value': 'https://ror.org/00fw8bp86', 'schema': 'ROR'},
                {'value': 'grid.470046.1', 'schema': 'GRID'},
            ]
        },
        {
            'affiliations': [{'value': 'Oklahoma U.'}],
            'ids': [
                {'value': 'INSPIRE-00060668', 'schema': 'INSPIRE ID'},
                {'value': '0000-0002-5888-2734', 'schema': 'ORCID'},
            ],
            'full_name': 'Abbott, Braden Keim',
            'affiliations_identifiers': [
                {'value': 'https://ror.org/02aqsxs83', 'schema': 'ROR'},
                {'value': 'grid.266900.b', 'schema': 'GRID'},
            ]
        }
    ]
    validate(expected_authors, authors_subschema)
    assert expected_authors[0] == obj.data['authors'][0]
    assert expected_authors[1] == obj.data['authors'][1]


def test_arxiv_author_test_institutional_namespace():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2203.17053.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2203.17053',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2203.17053.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [
                {'value': u'Liverpool U.'},
                {'value': u'CERN'}
            ],
            'ids': [
                {'value': 'INSPIRE-00657132', 'schema': u'INSPIRE ID'},
            ],
            'full_name': u'Abed Abud, Adam',
        },
        {
            'affiliations': [{'value': 'Oxford U.'}],
            'ids': [
                {'value': '0000-0001-7036-9645', 'schema': 'ORCID'},
                {'value': 'INSPIRE-00210439', 'schema': 'INSPIRE ID'},
            ],
            'full_name': 'Abi, Babak',
        }
    ]
    validate(expected_authors, authors_subschema)

    assert expected_authors[0] == obj.data['authors'][0]
    assert expected_authors[1] == obj.data['authors'][1]


def test_arxiv_author_no_none_in_institution_affiliations():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2203.17053.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2203.17053',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2203.17053.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [
                {'value': u'INFN, Catania'},
            ],
            'ids': [
                {'value': 'INSPIRE-00700856', 'schema': u'INSPIRE ID'},
            ],
            'full_name': u'Ali-Mohammadzadeh, Behnam',
        },
    ]
    validate(expected_authors, authors_subschema)

    assert expected_authors[0] == obj.data['authors'][14]


def test_arxiv_author_no_organization_name():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2205.14864.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2205.14864',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2205.14864.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'ids': [
                {'value': 'INSPIRE-00149777', 'schema': u'INSPIRE ID'},
            ],
            'full_name': u'Biermann, Peter',
        },
    ]
    validate(expected_authors, authors_subschema)

    assert expected_authors[0] == obj.data['authors'][29]


def test_arxiv_handles_invalid_authorid_value():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2107.10592.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2107.10592',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2107.10592.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [
                {'value': u'Kosice U.'},
            ],
            'affiliations_identifiers': [
                {'value': 'https://ror.org/039965637', 'schema': 'ROR'},
            ],
            'full_name': u'Ahuja, Ishaan',
        },
    ]
    validate(expected_authors, authors_subschema)

    assert expected_authors[0] == obj.data['authors'][9]


def test_arxiv_handles_non_ascii_affiliations():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2206.14521.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2206.14521',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2206.14521.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    authors_subschema = schema['properties']['authors']
    expected_authors = [
        {
            'affiliations': [
                {'value': u'Liverpool U.'},
                {'value': u'CERN'},
            ],
            'ids': [
                {'value': 'INSPIRE-00657132', 'schema': u'INSPIRE ID'},
            ],
            'affiliations_identifiers': [
                {'value': 'https://ror.org/04xs57h96', 'schema': 'ROR'},
                {'value': 'https://ror.org/01ggx4157', 'schema': 'ROR'},
            ],
            'full_name': u'Abed Abud, Adam',
        },
    ]
    validate(expected_authors, authors_subschema)

    assert arxiv_author_list(obj, eng) is None
    assert expected_authors[0] == obj.data['authors'][0]


def test_arxiv_author_no_none_in_ror():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2206.14521.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2206.14521',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2206.14521.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)

    authors_subschema = schema['properties']['authors']
    expected_author = [
        {
            'affiliations': [
                {'value': u'INFN, Catania'},
            ],
            'ids': [
                {'value': u'INSPIRE-00700856', 'schema': u'INSPIRE ID'},
            ],
            'affiliations_identifiers': [
                {'value': u'https://ror.org/02pq29p90', 'schema': 'ROR'},
            ],
            'full_name': u'Ali-Mohammadzadeh, Behnam',
        },
    ]
    validate(expected_author, authors_subschema)

    assert expected_author[0] == obj.data['authors'][16]


def test_arxiv_handles_newLines():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2207.10906.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2207.10906',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2207.10906.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    authors_subschema = schema['properties']['authors']
    expected_author = [
        {
            'affiliations': [
                {'value': u'Beijing, Inst. High Energy Phys.'},
            ],
            'ids': [
                {'value': u'INSPIRE-00059665', 'schema': u'INSPIRE ID'},
                {'value': u'0000-0002-3935-619X', 'schema': u'ORCID'},
            ],
            'full_name': u'Ablikim, Medina',
        },
    ]
    validate(expected_author, authors_subschema)

    arxiv_author_list(obj, eng)
    assert expected_author[0] == obj.data['authors'][0]


def test_arxiv_ignores_random_xml_files():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2207.08972.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2207.08972',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2207.08972.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)
    assert obj.data.get('authors', None) is None


def test_arxiv_handles_non_ascii_organization_names():
    schema = load_schema('hep')
    eprints_subschema = schema['properties']['arxiv_eprints']
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '2202.12988.tar.gz'))

    data = {
        '$schema': 'http://localhost:5000/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': '2202.12988',
            },
        ],
    }
    validate(data['arxiv_eprints'], eprints_subschema)

    extra_data = {}
    files = MockFiles({
        '2202.12988.tar.gz': AttrDict({
            'file': AttrDict({
                'uri': filename,
            })
        })
    })

    obj = MockObj(data, extra_data, files=files)
    eng = MockEng()

    arxiv_author_list(obj, eng)
    assert obj.data.get('authors', None) is not None


def test_extract_authors_from_xml_extracts_also_name_suffix():
    data = """
    <collaborationauthorlist xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/">
    <cal:creationDate>2022-01-25</cal:creationDate>
    <cal:publicationReference>Fermilab-PUB-2022-01-25</cal:publicationReference>
    <cal:collaborations>
    <cal:collaboration id="duneid">
    <foaf:name>DUNE</foaf:name>
    <cal:experimentNumber>DUNE</cal:experimentNumber>
    </cal:collaboration>
    </cal:collaborations>
    <cal:authors>
        <foaf:Person>
            <foaf:name>Michael Finger</foaf:name>
            <foaf:givenName>Michael</foaf:givenName>
            <foaf:familyName>Finger</foaf:familyName>
            <cal:authorNameNative lang=""/>
            <cal:authorSuffix>Jr.</cal:authorSuffix>
            <cal:authorStatus/>
            <cal:authorNamePaper>M. Finger Jr.</cal:authorNamePaper>
            <cal:authorAffiliations>
            <cal:authorAffiliation organizationid="o27" connection=""/>
            <cal:authorAffiliation organizationid="vo1" connection="AlsoAt"/>
            </cal:authorAffiliations>
            <cal:authorIDs>
            <cal:authorID source="INSPIRE">INSPIRE-00171357</cal:authorID>
            <cal:authorID source="CCID">391883</cal:authorID>
            <cal:authorID source="ORCID">0000-0003-3155-2484</cal:authorID>
            </cal:authorIDs>
        </foaf:Person>
    </cal:authors>
    </collaborationauthorlist>
    """
    result = extract_authors_from_xml(data)
    assert result[0]["full_name"] == "Finger, Michael, Jr."
