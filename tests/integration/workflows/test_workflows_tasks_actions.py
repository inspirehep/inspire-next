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
import requests_mock
import pytest

from inspire_schemas.api import load_schema, validate
from invenio_search import current_search
from invenio_workflows import (
    start,
    workflow_object_class,
    WorkflowEngine,
    ObjectStatus,
)
from invenio_workflows.errors import WorkflowsError
from invenio_workflows.models import WorkflowObjectModel

from inspirehep.modules.workflows.tasks.actions import (
    core_selection_wf_already_created, create_core_selection_wf,
    load_from_source_data,
    normalize_journal_titles, affiliations_for_hidden_collections, replace_collection_to_hidden,
    normalize_collaborations,
    normalize_affiliations,
    link_institutions_with_affiliations
)

from calls import insert_citing_record

from factories.db.invenio_records import TestRecordMetadata

from mocks import (
    fake_beard_api_request,
    fake_download_file,
    fake_magpie_api_request,
)
from workflow_utils import build_workflow

from calls import generate_record


@pytest.fixture(scope='function')
def insert_journals_in_db(workflow_app):
    """Temporarily add few journals in the DB"""
    TestRecordMetadata.create_from_file(
        __name__, 'jou_record_refereed.json', pid_type='jou', index_name='records-journals'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'jou_record_refereed_and_proceedings.json', pid_type='jou', index_name='records-journals'
    )


@pytest.fixture(scope='function')
def insert_experiments_into_db(workflow_app):
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_without_collaboration.json', pid_type='exp', index_name='records-experiments'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_collaboration.json', pid_type='exp', index_name='records-experiments'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_collaboration_and_subgroups.json', pid_type='exp', index_name='records-experiments'
    )


@pytest.fixture(scope='function')
def insert_ambiguous_experiments_into_db(workflow_app):
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_ambiguous_collaboration_1.json', pid_type='exp', index_name='records-experiments'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_ambiguous_collaboration_2.json', pid_type='exp', index_name='records-experiments'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_subgroup_1.json', pid_type='exp', index_name='records-experiments'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'experiment_with_subgroup_2.json', pid_type='exp', index_name='records-experiments'
    )


@pytest.fixture(scope='function')
def insert_institutions_in_db(workflow_app):
    """Temporarily add few institutions in the DB"""
    TestRecordMetadata.create_from_file(
        __name__, 'institution_903335.json', pid_type='ins', index_name='records-institutions'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'institution_902725.json', pid_type='ins', index_name='records-institutions'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'institution_1126070.json', pid_type='ins', index_name='records-institutions'
    )


@pytest.fixture(scope='function')
def insert_literature_in_db(workflow_app):
    """Temporarily add few institutions in the DB"""
    TestRecordMetadata.create_from_file(
        __name__, 'literature_1863053.json', pid_type='ins', index_name='records-hep'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'literature_1862822.json', pid_type='ins', index_name='records-hep'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'literature_1836272.json', pid_type='ins', index_name='records-hep'
    )
    TestRecordMetadata.create_from_file(
        __name__, 'literature_1459277.json', pid_type='ins', index_name='records-hep'
    )


def test_normalize_journal_titles_known_journals_with_ref(workflow_app, insert_journals_in_db):
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


def test_normalize_journal_titles_known_journals_with_ref_from_variants(workflow_app, insert_journals_in_db):
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


def test_normalize_journal_titles_known_journals_no_ref(workflow_app, insert_journals_in_db):
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


def test_normalize_journal_titles_known_journals_wrong_ref(workflow_app, insert_journals_in_db):
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


def test_normalize_journal_titles_unknown_journals_with_ref(workflow_app, insert_journals_in_db):
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


def test_normalize_journal_titles_unknown_journals_no_ref(workflow_app, insert_journals_in_db):
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
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async')
def test_refextract_from_pdf(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
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

    with mock.patch.dict(workflow_app.config, extra_config):
        workflow_id = build_workflow(citing_record).id
        citing_doc_workflow_uuid = start('article', object_id=workflow_id)

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
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async')
def test_refextract_with_call_to_hep(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services
):
    cited_record_json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": ["Literature"],
        "control_number": 1,
        "document_type": ["article"],
        "publication_info": [
            {
                "artid": "045",
                "journal_title": "JHEP",
                "journal_volume": "06",
                "page_start": "045",
                "year": 2007,
            }
        ],
        "titles": [{"title": "The Strongly-Interacting Light Higgs"}],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index='records-hep', pid_type='lit')
    citing_record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'titles': [
            {
                'title': 'My title',
            }
        ],
        'control_number': 1001,
        'document_type': ['article'],
        "references": [
            {
                "reference": {
                    "publication_info": {
                        "artid": "045",
                        "journal_title": "JHEP",
                        "journal_volume": "06",
                        "page_start": "045",
                        "year": 2007,
                    }
                }
            }
        ]
    }

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "FEATURE_FLAG_ENABLE_MATCH_REFERENCES_HEP": True,
    }

    with mock.patch.dict(workflow_app.config, extra_config):
        with requests_mock.Mocker(real_http=True) as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/api/matcher/linked_references/'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL"),
                ),
                headers={'content-type': 'application/json'},
                status_code=200,
                json={
                    'references': [
                        {
                            'record': {'$ref': 'http://localhost:5000/api/literature/1'},
                            "reference": {
                                "publication_info": {
                                    "artid": "045",
                                    "journal_title": "JHEP",
                                    "journal_volume": "06",
                                    "page_start": "045",
                                    "year": 2007,
                                }
                            }
                        }
                    ]
                }
            )
            workflow_id = build_workflow(citing_record).id
            citing_doc_workflow_uuid = start('article', object_id=workflow_id)
    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]

    assert citing_doc_obj.data['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/1'


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
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async')
def test_refextract_with_call_to_hep_with_error(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services
):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'titles': [
            {
                'title': 'My title',
            }
        ],
        'control_number': 1001,
        'document_type': ['article'],
        "references": [
            {
                "reference": {
                    "publication_info": {
                        "artid": "045",
                        "journal_title": "JHEP",
                        "journal_volume": "06",
                        "page_start": "045",
                        "year": 2007,
                    }
                }
            }
        ]
    }

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "FEATURE_FLAG_ENABLE_MATCH_REFERENCES_HEP": True,
    }

    with mock.patch.dict(workflow_app.config, extra_config):
        with requests_mock.Mocker(real_http=True) as requests_mocker:
            requests_mocker.register_uri(
                'POST', '{url}/api/matcher/linked_references/'.format(
                    url=workflow_app.config.get("INSPIREHEP_URL"),
                ),
                headers={'content-type': 'application/json'},
                status_code=500,
                json={
                    "message": "Error Message"
                }
            )
            workflow_id = build_workflow(record).id
            with pytest.raises(WorkflowsError):
                start('article', object_id=workflow_id)
    obj = workflow_object_class.get(workflow_id)

    assert obj.status == ObjectStatus.ERROR
    assert 'Error Message' in obj.extra_data['_error_msg']


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
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async')
def test_count_reference_coreness(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
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

    with mock.patch.dict(workflow_app.config, extra_config):
        workflow_id = build_workflow(citing_record).id
        citing_doc_workflow_uuid = start('article', object_id=workflow_id)

    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]

    assert citing_doc_obj.extra_data['reference_count'] == {
        'core': 0,
        'non_core': 1,
    }


@pytest.fixture
def load_from_source_data_workflow(workflow_app):
    class SourceDataWorkflow(object):
        workflow = [load_from_source_data]

    workflow_app.extensions['invenio-workflows'].register_workflow(
        'load_source_data',
        SourceDataWorkflow,
    )

    yield workflow_app

    del workflow_app.extensions['invenio-workflows'].workflows['load_source_data']


def test_workflow_loads_from_source_data_fails_on_no_source_data(
    load_from_source_data_workflow,
    workflow_app,
    record_from_db,
):
    extra_data_without_source_data = {}
    workflow_id = workflow_object_class.create(
        data_type='hep',
        data=record_from_db,
        extra_data=extra_data_without_source_data,
    ).id

    with pytest.raises(ValueError) as exc:
        start('load_source_data', object_id=workflow_id)

    assert exc.match(r'source_data.*missing')


def test_find_interesting_affiliations_works_correctly_for_complex_affiliations_value(workflow_app):
    expected_affiliations = ["HAL Hidden"]
    record = generate_record()
    record['authors'][0]['raw_affiliations'] = [{"value": "Some longer description In2P3. with proper keyword included"}, {"value": "Another one but this time with wrong keywords Fremilab included"}]

    workflow = build_workflow(record)

    affiliations = affiliations_for_hidden_collections(workflow)
    assert affiliations == expected_affiliations


def test_replace_collection_to_hidden_sets_proper_hidden_collections_on_metadata(workflow_app):
    expected_collections = ["CDS Hidden", "Fermilab"]
    record = generate_record()
    record['authors'][0]['raw_affiliations'] = [
        {"value": "Some longer description CErN? with proper keyword included"},
        {"value": "Another one but this time with wrong keywords IN2P345 included"}
    ]
    record['authors'][1]['raw_affiliations'] = [{"value": "Blah blah blah fermilab, blah blah"}]
    workflow = build_workflow(record)

    wf = replace_collection_to_hidden(workflow, None)
    assert wf.data['_collections'] == expected_collections


def test_normalize_journal_titles_in_references(workflow_app, insert_journals_in_db):
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
        "references": [
            {
                "reference": {
                    "publication_info": {
                        "journal_title": "A Test Journal1",
                    }
                }
            },
            {
                "reference": {
                    "publication_info": {
                        "journal_title": "Something not in db",
                    }
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

    assert obj.data['references'][0]['reference']['publication_info']['journal_title'] == 'Test.Jou.1'
    assert obj.data['references'][0]['reference']['publication_info']['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['references'][1]['reference']['publication_info']['journal_title'] == 'Something not in db'


def test_normalize_collaborations(workflow_app, insert_experiments_into_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {'value': "Atlas II", "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"}},
            {"value": "Particle Data Group"},
            {"value": "Unknown"}
        ],

    }

    expected_collaborations = [
        {'value': "Atlas II", "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"}},
        {'value': 'Particle Data Group', 'record': {'$ref': 'https://inspirehep.net/api/experiments/1800050'}},
        {"value": "Unknown"}
    ]

    expected_accelerator_experiments = [
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1800050'}}
    ]

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )
    obj = normalize_collaborations(obj, None)
    assert obj.data['collaborations'] == expected_collaborations
    assert obj.data['accelerator_experiments'] == expected_accelerator_experiments


def test_normalize_collaborations_with_different_name_variants(workflow_app, insert_experiments_into_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {'value': "ATLAS Muon"},
            {"value": "ATLAS Liquid   Argon"},
            {"value": "Particle Data Group"}
        ],
    }

    expected_collaborations = [
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1108541'}, 'value': u'ATLAS Muon'},
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1108541'}, 'value': u'ATLAS Liquid Argon'},
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1800050'}, 'value': u'Particle Data Group'}
    ]

    expected_accelerator_experiments = [
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1108541'}, "legacy_name": "CERN-LHC-ATLAS"},
        {'record': {u'$ref': u'https://inspirehep.net/api/experiments/1800050'}}
    ]

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )
    obj = normalize_collaborations(obj, None)
    assert obj.data['collaborations'] == expected_collaborations
    assert obj.data['accelerator_experiments'] == expected_accelerator_experiments


@mock.patch("inspirehep.modules.workflows.tasks.actions.logging.Logger.info")
def test_normalize_collaborations_doesnt_link_experiment_when_ambiguous_collaboration_names(
        mock_logger, workflow_app, insert_ambiguous_experiments_into_db
):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],

    }

    expected_collaborations = [{"value": "SHIP"}]

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    obj = normalize_collaborations(obj, None)

    assert obj.data['collaborations'] == expected_collaborations
    assert not obj.data.get('accelerator_experiments')
    assert mock_logger.mock_calls[2][1][0] == u"(wf: 1) ambiguous match for collaboration SHIP. Matched collaborations: SHIP, SHiP"


@mock.patch("inspirehep.modules.workflows.tasks.actions.logging.Logger.info")
def test_normalize_collaborations_doesnt_link_experiment_when_ambiguous_subgroup(mock_logger, workflow_app, insert_ambiguous_experiments_into_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "Belle SVD"}
        ],

    }

    expected_collaborations = [{"value": "Belle SVD"}]

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    obj = normalize_collaborations(obj, None)

    assert obj.data['collaborations'] == expected_collaborations
    assert not obj.data.get('accelerator_experiments')
    assert mock_logger.mock_calls[1][1][0] == u'(wf: 1) ambiguous match for collaboration Belle SVD. Matches for collaboration subgroup: Belle-II, Belle'


@mock.patch("inspirehep.modules.workflows.tasks.actions.logging.Logger.info")
def test_normalize_affiliations_happy_flow(mock_logger, workflow_app, insert_literature_in_db):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "raw_affiliations": [
                    {
                        "value": "Faculty of Physics, University of Warsaw, Pasteura 5 Warsaw"
                    }
                ],
            },
            {
                "full_name": "Latacz, Barbara",
                "raw_affiliations": [
                    {"value": "CERN, Genève, Switzerland"}
                ],
            },
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert obj.data["authors"][0]["affiliations"] == [
        {
            u"record": {u"$ref": u"http://localhost:5000/api/institutions/903335"},
            u"value": u"Warsaw U.",
        }
    ]
    assert obj.data["authors"][1]["affiliations"] == [
        {
            u"record": {u"$ref": u"http:/localhost:5000/api/institutions/902725"},
            u"value": u"CERN",
        }
    ]

    assert mock_logger.mock_calls[1][1] == (
        u'(wf: %s) Normalized affiliations for author %s. Raw affiliations: %s. Assigned affiliations: %s',
        1,
        'Kowal, Michal',
        'Faculty of Physics, University of Warsaw, Pasteura 5 Warsaw',
        [{u'record': {u'$ref': u'http://localhost:5000/api/institutions/903335'}, u'value': u'Warsaw U.'}]
    )


def test_normalize_affiliations_when_authors_has_two_happy_flow(
    workflow_app, insert_literature_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "raw_affiliations": [
                    {
                        "value": "Faculty of Physics, University of Warsaw, Pasteura 5 Warsaw"
                    },
                    {"value": "CERN, Genève, Switzerland"},
                ],
            }
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert obj.data["authors"][0]["affiliations"] == [
        {
            u"record": {u"$ref": u"http://localhost:5000/api/institutions/903335"},
            u"value": u"Warsaw U.",
        },
        {
            u"record": {u"$ref": u"http:/localhost:5000/api/institutions/902725"},
            u"value": u"CERN",
        },
    ]


def test_normalize_affiliations_when_lit_affiliation_missing_institution_ref(
    workflow_app, insert_literature_in_db, insert_institutions_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kozioł, Karol",
                "raw_affiliations": [
                    {"value": "NCBJ Świerk"},
                    {"value": "CERN, Genève, Switzerland"},
                ],
            }
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert obj.data["authors"][0]["affiliations"] == [
        {
            "value": u"NCBJ, Swierk",
        },
        {
            u'record': {
                u'$ref': u'http:/localhost:5000/api/institutions/902725'
            },
            u'value': u'CERN'
        }
    ]


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions._match_lit_author_affiliation",
    return_value={"value": "CERN"}
)
def test_normalize_affiliations_run_query_only_once_when_authors_have_same_raw_aff(
    mock_assign_matched_affiliation_to_author, workflow_app, insert_literature_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "raw_affiliations": [
                    {"value": "CERN, Rue de Genève, Meyrin, Switzerland"}
                ],
            },
            {
                "full_name": "Latacz, Barbara",
                "raw_affiliations": [
                    {"value": "CERN, Rue de Genève, Meyrin, Switzerland"}
                ],
            },
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert mock_assign_matched_affiliation_to_author.called_once()


def test_normalize_affiliations_handle_not_found_affiliations(
    workflow_app, insert_literature_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "raw_affiliations": [{"value": "Non existing aff"}],
            },
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert not obj.data["authors"][0].get("affiliations")


def test_link_institutions_with_affiliations(
    workflow_app, insert_literature_in_db, insert_institutions_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "affiliations": [{"value": "CERN"}, {"value": "Warsaw U."}]
            },
            {
                "full_name": "Latacz, Barbara",
                "affiliations": [{"value": "CERN"}]
            },
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = link_institutions_with_affiliations(obj, None)

    expected_affiliation_1 = {
        'record': {u'$ref': u'http://localhost:5000//api/institutions/902725'}, 'value': 'CERN'
    }
    expected_affiliation_2 = {
        'record': {u'$ref': u'https://inspirehep.net/api/institutions/903335'}, 'value': 'Warsaw U.'
    }

    assert expected_affiliation_1 == obj.data["authors"][0]["affiliations"][0]
    assert expected_affiliation_2 == obj.data["authors"][0]["affiliations"][1]
    assert expected_affiliation_1 == obj.data["authors"][1]["affiliations"][0]


def test_normalize_affiliations_doesnt_return_nested_affiliations_if_using_memoized(
    workflow_app, insert_literature_in_db,
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "emails": [
                    "weili@mail.itp.ac.cn"
                ],
                "full_name": "Li, Wei",
                "raw_affiliations": [
                    {
                        "value": "Institute of Theoretical Physics, Chinese Academy of Sciences, 100190 Beijing, P.R. China"
                    }
                ]
            },
            {
                "emails": [
                    "masahito.yamazaki@ipmu.jp"
                ],
                "full_name": "Yamazaki, Masahito",
                "raw_affiliations": [
                    {
                        "value": "Institute of Theoretical Physics, Chinese Academy of Sciences, 100190 Beijing, P.R. China"
                    }
                ]
            }
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert obj.data["authors"][0]["affiliations"] == [
        {u'record': {u'$ref': u'https://inspirebeta.net/api/institutions/903895'},
         u'value': u'Beijing, Inst. Theor. Phys.'}
    ]

    assert obj.data["authors"][1]["affiliations"] == [
        {u'record': {u'$ref': u'https://inspirebeta.net/api/institutions/903895'},
         u'value': u'Beijing, Inst. Theor. Phys.'}
    ]


def test_normalize_affiliations_doesnt_add_duplicated_affiliations(
    workflow_app, insert_literature_in_db,
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Kowal, Michal",
                "raw_affiliations": [
                    {"value": "Warsaw U., Faculty of Physics"},
                    {"value": "Warsaw U., Faculty of Mathematics, Informatics, and Mechanics"}]
            }
        ],
    }
    test_normalize_affiliations_when_authors_has_two_happy_flow
    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_affiliations(obj, None)

    assert obj.data["authors"][0]["affiliations"] == [
        {u'record': {u'$ref': u'http://localhost:5000/api/institutions/903335'}, u'value': u'Warsaw U.'}]


def test_core_selection_wf_already_created_show_created_wf(workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }

    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['source_data'] = {"data": record, "extra_data": {"source_data": {"data": record}}}
    workflow_object.save()
    start("article", object_id=workflow_object.id)
    current_search.flush_and_refresh("holdingpen-hep")
    assert len(core_selection_wf_already_created(123456)) == 0

    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    start("core_selection", object_id=workflow_object.id)
    workflow_object.save()
    current_search.flush_and_refresh("holdingpen-hep")
    assert len(core_selection_wf_already_created(123456)) == 1

    workflow_object.status = ObjectStatus.COMPLETED
    workflow_object.save()
    current_search.flush_and_refresh("holdingpen-hep")
    assert len(core_selection_wf_already_created(123456)) == 1


def test_create_core_selection_workflow_task(workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )
    workflow_object.extra_data['_task_history'] = ['Should be removed']
    workflow_object.extra_data['_error_msg'] = ['Should be removed']
    workflow_object.extra_data['source_data'] = ['Should be removed']
    workflow_object.extra_data['restart-count'] = "Should be removed"
    workflow_object.extra_data['auto-approved'] = True
    workflow_object.save()

    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

    create_core_selection_wf(workflow_object, None)

    wf = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one()
    assert wf.data == workflow_object.data
    assert "_error_msg" not in wf.extra_data
    assert "restart_count" not in wf.extra_data
    assert workflow_object.extra_data['_task_history'] != wf.extra_data['_task_history']
    assert wf.status == ObjectStatus.HALTED

    current_search.flush_and_refresh("holdingpen-hep")

    create_core_selection_wf(workflow_object, None)

    # ensure that new core_selection_wf is not created when one already exists
    new_query_wfs = WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).one()
    assert new_query_wfs.id == wf.id


def test_create_core_selection_workflow_task_wont_create_when_record_is_core(workflow_app):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": [
            "report"
        ],
        "collaborations": [
            {"value": "SHIP"}
        ],
        "control_number": 123456,
        "core": True

    }
    workflow_object = workflow_object_class.create(
        data=record,
        id_user=None,
        data_type='hep'
    )

    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0

    create_core_selection_wf(workflow_object, None)

    assert WorkflowObjectModel.query.filter(WorkflowObjectModel.workflow.has(name="core_selection")).count() == 0
