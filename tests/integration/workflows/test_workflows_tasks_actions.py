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

"""Tests for workflows actions."""

from __future__ import absolute_import, division, print_function

import mock

import pytest

from inspire_schemas.api import load_schema, validate
from invenio_workflows import (
    WorkflowEngine,
    start,
    workflow_object_class,
)

from inspirehep.modules.workflows.tasks.actions import normalize_journal_titles

from calls import insert_citing_record

from factories.db.invenio_records import TestRecordMetadata

from mocks import (
    fake_beard_api_request,
    fake_download_file,
    fake_magpie_api_request,
)


@pytest.fixture(scope='function')
def insert_journals_in_db(isolated_app):
    """Temporarily add few journals in the DB"""
    TestRecordMetadata.create_from_file(
        __name__, 'jou_record_refereed.json', pid_type='jou', index_name='records-journals'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'jou_record_refereed_and_proceedings.json', pid_type='jou', index_name='records-journals'
    )


def test_normalize_journal_titles_known_journals_with_ref(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "A Test Journal1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936475"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Test.Jou.2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_with_ref_from_variants(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "A Test Journal1 Variant 2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936475"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "A Test Journal2 Variant 3",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_no_ref(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "A Test Journal1"
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Test.Jou.2"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_wrong_ref(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "A Test Journal1",
                "journal_record": {
                    "$ref": "wrong1"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Test.Jou.2",
                "journal_record": {
                    "$ref": "wrong2"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Test.Jou.1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Test.Jou.2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_unknown_journals_with_ref(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Unknown1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/0000000"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Unknown2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1111111"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Unknown1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Unknown2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/0000000'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1111111'}


def test_normalize_journal_titles_unknown_journals_no_ref(isolated_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Unknown1"
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Unknown2"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Unknown1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Unknown2'
    assert 'journal_record' not in obj.data['publication_info'][0]
    assert 'journal_record' not in obj.data['publication_info'][2]


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_refextract_from_pdf(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    isolated_app,
    mocked_external_services
):
    """Test refextract from PDF and reference matching for default Configuration
     by going through the entire workflow."""

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'arxiv_eprints': [
            {
                'categories': ['quant-ph', 'cond-mat.mes-hall', 'cond-mat.str-el', 'math-ph', 'math.MP'],
                'value': '1308.0815'
            }
        ],
        'control_number': 1000,
        'document_type': ['article'],
        'titles': [
            {
                'source': 'arXiv',
                'title': 'Solving a two-electron quantum dot model in terms of polynomial solutions of a Biconfluent Heun equation'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index='records-hep', pid_type='lit')
    citing_record, categories = insert_citing_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }

    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    assert validate(citing_record['acquisition_source'], subschema) is None

    with mock.patch.dict(isolated_app.config, extra_config):
        citing_doc_workflow_uuid = start('article', [citing_record])

    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]

    assert citing_doc_obj.data['references'][7]['record']['$ref'] == 'http://localhost:5000/api/literature/1000'
    assert citing_doc_obj.data['references'][0]['raw_refs'][0]['source'] == 'arXiv'


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.actions.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link',
    return_value=True
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
def test_count_reference_coreness(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    isolated_app,
    mocked_external_services
):
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'arxiv_eprints': [
            {
                'categories': ['quant-ph', 'cond-mat.mes-hall', 'cond-mat.str-el', 'math-ph', 'math.MP'],
                'value': '1308.0815'
            }
        ],
        'control_number': 1000,
        'document_type': ['article'],
        'titles': [
            {
                'source': 'arXiv',
                'title': 'Solving a two-electron quantum dot model in terms of polynomial solutions of a Biconfluent Heun equation'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index='records-hep', pid_type='lit')
    citing_record, categories = insert_citing_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }

    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    assert validate(citing_record['acquisition_source'], subschema) is None

    with mock.patch.dict(isolated_app.config, extra_config):
        citing_doc_workflow_uuid = start('article', [citing_record])

    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]

    assert citing_doc_obj.extra_data['reference_count'] == {
        'core': 0,
        'non_core': 1,
    }
