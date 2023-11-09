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
from inspirehep.modules.workflows.tasks.refextract import extract_journal_info
import pytest
import requests_mock
from calls import generate_record, insert_citing_record
from factories.db.invenio_records import TestRecordMetadata
from flask import current_app
from inspire_schemas.api import load_schema, validate
from inspire_utils.query import ordered
from invenio_search import current_search
from invenio_workflows import (ObjectStatus, WorkflowEngine, start,
                               workflow_object_class)
from invenio_workflows.models import WorkflowObjectModel
from mocks import (fake_classifier_api_request, fake_download_file,
                   fake_magpie_api_request)
from utils import override_config
from workflow_utils import build_workflow

from inspirehep.modules.workflows.tasks.actions import (
    affiliations_for_hidden_collections, core_selection_wf_already_created,
    create_core_selection_wf, link_institutions_with_affiliations,
    load_from_source_data, normalize_author_affiliations,
    normalize_collaborations, normalize_journal_titles, refextract,
    remove_inspire_categories_derived_from_core_arxiv_categories,
    replace_collection_to_hidden, update_inspire_categories)
from inspirehep.modules.workflows.utils import \
    _get_headers_for_hep_root_table_request


@pytest.fixture(scope="function")
def insert_journals_in_db(workflow_app):
    """Temporarily add few journals in the DB"""
    TestRecordMetadata.create_from_file(
        __name__,
        "jou_record_refereed.json",
        pid_type="jou",
        index_name="records-journals",
    )
    TestRecordMetadata.create_from_file(
        __name__,
        "jou_record_refereed_and_proceedings.json",
        pid_type="jou",
        index_name="records-journals",
    )


@pytest.fixture(scope="function")
def insert_hep_records_into_db(workflow_app):
    TestRecordMetadata.create_from_file(
        __name__,
        "record_lit_to_match_extracted_refs.json",
        pid_type="exp",
        index_name="records-hep",
    )


@pytest.fixture(scope="function")
def insert_institutions_in_db(workflow_app):
    """Temporarily add few institutions in the DB"""
    TestRecordMetadata.create_from_file(
        __name__,
        "institution_903335.json",
        pid_type="ins",
        index_name="records-institutions",
    )
    TestRecordMetadata.create_from_file(
        __name__,
        "institution_902725.json",
        pid_type="ins",
        index_name="records-institutions",
    )
    TestRecordMetadata.create_from_file(
        __name__,
        "institution_1126070.json",
        pid_type="ins",
        index_name="records-institutions",
    )


@pytest.fixture(scope="function")
def insert_literature_in_db(workflow_app):
    """Temporarily add few institutions in the DB"""
    TestRecordMetadata.create_from_file(
        __name__, "literature_1863053.json", pid_type="lit", index_name="records-hep"
    )
    TestRecordMetadata.create_from_file(
        __name__, "literature_1862822.json", pid_type="lit", index_name="records-hep"
    )
    TestRecordMetadata.create_from_file(
        __name__, "literature_1836272.json", pid_type="lit", index_name="records-hep"
    )
    TestRecordMetadata.create_from_file(
        __name__, "literature_1459277.json", pid_type="lit", index_name="records-hep"
    )
    TestRecordMetadata.create_from_file(
        __name__, "literature_1800446.json", pid_type="lit", index_name="records-hep"
    )


def test_normalize_journal_titles_known_journals_with_ref(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1": "Test.Jou.1", "Test.Jou.2": "Test.Jou.2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {
                    "journal_title": "A Test Journal1",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1936475"
                    },
                },
                {"cnum": "C01-01-01"},
                {
                    "journal_title": "Test.Jou.2",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1936476"
                    },
                },
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Test.Jou.1"
        assert obj.data["publication_info"][2]["journal_title"] == "Test.Jou.2"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936475"
        }
        assert obj.data["publication_info"][2]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936476"
        }
        assert len(obj.extra_data["journal_inspire_categories"]) == 2
        assert {"term": "Astrophysics"} in obj.extra_data["journal_inspire_categories"]
        assert {"term": "Accelerators"} in obj.extra_data["journal_inspire_categories"]


def test_normalize_journal_titles_known_journals_with_ref_from_variants(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1 Variant 2": "Test.Jou.1", "A Test Journal2 Variant 3": "Test.Jou.2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {
                    "journal_title": "A Test Journal1 Variant 2",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1936475"
                    },
                },
                {"cnum": "C01-01-01"},
                {
                    "journal_title": "A Test Journal2 Variant 3",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1936476"
                    },
                },
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Test.Jou.1"
        assert obj.data["publication_info"][2]["journal_title"] == "Test.Jou.2"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936475"
        }
        assert obj.data["publication_info"][2]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936476"
        }
        assert len(obj.extra_data["journal_inspire_categories"]) == 2
        assert {"term": "Astrophysics"} in obj.extra_data["journal_inspire_categories"]
        assert {"term": "Accelerators"} in obj.extra_data["journal_inspire_categories"]


def test_normalize_journal_titles_known_journals_no_ref(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1": "Test.Jou.1", "Test.Jou.2": "Test.Jou.2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {"journal_title": "A Test Journal1"},
                {"cnum": "C01-01-01"},
                {"journal_title": "Test.Jou.2"},
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Test.Jou.1"
        assert obj.data["publication_info"][2]["journal_title"] == "Test.Jou.2"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936475"
        }
        assert obj.data["publication_info"][2]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936476"
        }
        assert len(obj.extra_data["journal_inspire_categories"]) == 2
        assert {"term": "Astrophysics"} in obj.extra_data["journal_inspire_categories"]
        assert {"term": "Accelerators"} in obj.extra_data["journal_inspire_categories"]


def test_normalize_journal_titles_known_journals_wrong_ref(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1": "Test.Jou.1", "Test.Jou.2": "Test.Jou.2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {"journal_title": "A Test Journal1", "journal_record": {"$ref": "wrong1"}},
                {"cnum": "C01-01-01"},
                {"journal_title": "Test.Jou.2", "journal_record": {"$ref": "wrong2"}},
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Test.Jou.1"
        assert obj.data["publication_info"][2]["journal_title"] == "Test.Jou.2"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936475"
        }
        assert obj.data["publication_info"][2]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936476"
        }
        assert len(obj.extra_data["journal_inspire_categories"]) == 2
        assert {"term": "Astrophysics"} in obj.extra_data["journal_inspire_categories"]
        assert {"term": "Accelerators"} in obj.extra_data["journal_inspire_categories"]


def test_normalize_journal_titles_unknown_journals_with_ref(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"Unknown1": "Unknown1", "Unknown2": "Unknown2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {
                    "journal_title": "Unknown1",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/0000000"
                    },
                },
                {"cnum": "C01-01-01"},
                {
                    "journal_title": "Unknown2",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1111111"
                    },
                },
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Unknown1"
        assert obj.data["publication_info"][2]["journal_title"] == "Unknown2"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/0000000"
        }
        assert obj.data["publication_info"][2]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1111111"
        }
        assert not obj.extra_data.get("journal_inspire_categories")


def test_normalize_journal_titles_unknown_journals_no_ref(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"Unknown1": "Unknown1", "Unknown2": "Unknown2"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {"journal_title": "Unknown1"},
                {"cnum": "C01-01-01"},
                {"journal_title": "Unknown2"},
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Unknown1"
        assert obj.data["publication_info"][2]["journal_title"] == "Unknown2"
        assert "journal_record" not in obj.data["publication_info"][0]
        assert "journal_record" not in obj.data["publication_info"][2]
        assert not obj.extra_data.get("journal_inspire_categories")


def test_normalize_journal_titles_doesnt_assign_categories_from_journals_in_references(
    workflow_app, insert_journals_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1": "Test.Jou.1", "Proc.Roy.Irish Acad.A": "Proc.Roy.Irish Acad.A"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
            "publication_info": [
                {
                    "journal_title": "A Test Journal1",
                    "journal_record": {
                        "$ref": "http://localhost:5000/api/journals/1936475"
                    },
                },
            ],
            "references": [
                {
                    "reference": {
                        "authors": [{"full_name": "A, Papaetrou"}],
                        "misc": [
                            "A static solution of the equations of the gravitational field for an arbitrary charge distribution"
                        ],
                        "publication_info": {
                            "artid": "191",
                            "journal_record": {
                                "$ref": "http://localhost:5000/api/journals/1936476"
                            },
                            "journal_title": "Proc.Roy.Irish Acad.A",
                            "journal_volume": "51",
                            "page_start": "191",
                            "year": 1947,
                        },
                    }
                }
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert obj.data["publication_info"][0]["journal_title"] == "Test.Jou.1"
        assert obj.data["publication_info"][0]["journal_record"] == {
            "$ref": "http://localhost:5000/api/journals/1936475"
        }
        assert len(obj.extra_data["journal_inspire_categories"]) == 1
        assert {"term": "Astrophysics"} in obj.extra_data["journal_inspire_categories"]
        assert {"term": "Accelerators"} not in obj.extra_data["journal_inspire_categories"]


def test_update_inspire_categories(workflow_app):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["book", "note", "report"],
        "publication_info": [
            {
                "journal_title": "Unknown1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/0000000"
                },
            },
            {"cnum": "C01-01-01"},
            {
                "journal_title": "Unknown2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1111111"
                },
            },
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj.extra_data["journal_inspire_categories"] = [
        {"term": "Astrophysics"},
        {"term": "Accelerators"},
    ]
    update_inspire_categories(obj, None)
    assert (
        obj.data["inspire_categories"] == obj.extra_data["journal_inspire_categories"]
    )


def test_dont_update_inspire_categories(workflow_app):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["book", "note", "report"],
        "publication_info": [
            {
                "journal_title": "Unknown1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/0000000"
                },
            },
            {"cnum": "C01-01-01"},
            {
                "journal_title": "Unknown2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1111111"
                },
            },
        ],
        "inspire_categories": [
            {"term": "Test"},
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj.extra_data["journal_inspire_categories"] = [
        {"term": "Astrophysics"},
        {"term": "Accelerators"},
    ]
    update_inspire_categories(obj, None)
    assert (
        obj.data["inspire_categories"] != obj.extra_data["journal_inspire_categories"]
    )


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async"
)
def test_refextract_from_pdf(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services,
):
    """Test refextract from PDF and reference matching for default Configuration
    by going through the entire workflow."""
    cited_record_json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": ["Literature"],
        "arxiv_eprints": [
            {
                "categories": [
                    "quant-ph",
                    "cond-mat.mes-hall",
                    "cond-mat.str-el",
                    "math-ph",
                    "math.MP",
                ],
                "value": "1308.0815",
            }
        ],
        "control_number": 1000,
        "document_type": ["article"],
        "titles": [
            {
                "source": "arXiv",
                "title": "Solving a two-electron quantum dot model in terms of polynomial solutions of a Biconfluent Heun equation",
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index="records-hep", pid_type="lit"
    )
    citing_record, categories = insert_citing_record()

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "ARXIV_CATEGORIES": categories,
    }

    schema = load_schema("hep")
    subschema = schema["properties"]["acquisition_source"]

    assert validate(citing_record["acquisition_source"], subschema) is None

    with mock.patch.dict(workflow_app.config, extra_config):
        with override_config(FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE=True):
            workflow_id = build_workflow(citing_record).id
            citing_doc_workflow_uuid = start("article", object_id=workflow_id)

    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]
    assert len(citing_doc_obj.data["references"]) == 1


@mock.patch(
    "inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch("inspirehep.modules.workflows.tasks.arxiv.is_pdf_link", return_value=True)
@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    "inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async"
)
def test_count_reference_coreness(
    mocked_indexing_task,
    mocked_api_request_magpie,
    mocked_api_request_classifier,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services
):
    cited_record_json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": ["Literature"],
        "arxiv_eprints": [
            {
                "categories": [
                    "quant-ph",
                    "cond-mat.mes-hall",
                    "cond-mat.str-el",
                    "math-ph",
                    "math.MP",
                ],
                "value": "1308.0815",
            }
        ],
        "control_number": 1000,
        "document_type": ["article"],
        "titles": [
            {
                "source": "arXiv",
                "title": "Solving a two-electron quantum dot model in terms of polynomial solutions of a Biconfluent Heun equation",
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index="records-hep", pid_type="lit"
    )
    citing_record, categories = insert_citing_record()

    extra_config = {
        "CLASSIFIER_API_URL": "http://example.com/classifier",
        "MAGPIE_API_URL": "http://example.com/magpie",
        "ARXIV_CATEGORIES": categories,
    }

    schema = load_schema("hep")
    subschema = schema["properties"]["acquisition_source"]

    assert validate(citing_record["acquisition_source"], subschema) is None

    with mock.patch.dict(workflow_app.config, extra_config):
        with override_config(FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE=True):
            workflow_id = build_workflow(citing_record).id
            citing_doc_workflow_uuid = start("article", object_id=workflow_id)

    citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
    citing_doc_obj = citing_doc_eng.processed_objects[0]

    assert citing_doc_obj.extra_data["reference_count"] == {
        "core": 0,
        "non_core": 1,
    }


@pytest.fixture
def load_from_source_data_workflow(workflow_app):
    class SourceDataWorkflow(object):
        workflow = [load_from_source_data]

    workflow_app.extensions["invenio-workflows"].register_workflow(
        "load_source_data",
        SourceDataWorkflow,
    )

    yield workflow_app

    del workflow_app.extensions["invenio-workflows"].workflows["load_source_data"]


def test_workflow_loads_from_source_data_fails_on_no_source_data(
    load_from_source_data_workflow,
    workflow_app,
    record_from_db,
):
    extra_data_without_source_data = {}
    workflow_id = workflow_object_class.create(
        data_type="hep",
        data=record_from_db,
        extra_data=extra_data_without_source_data,
    ).id

    with pytest.raises(ValueError) as exc:
        start("load_source_data", object_id=workflow_id)

    assert exc.match(r"source_data.*missing")


def test_affiliations_for_hidden_collections_works_correctly_for_complex_affiliations_value(
    workflow_app,
):
    expected_affiliations = ["HAL Hidden"]
    record = generate_record()
    record["authors"][0]["raw_affiliations"] = [
        {"value": "Some longer description In2P3. with proper keyword included"},
        {"value": "Another one but this time with wrong keywords Fremilab included"},
    ]

    workflow = build_workflow(record)

    affiliations = affiliations_for_hidden_collections(workflow)
    assert affiliations == expected_affiliations


def test_affiliations_for_hidden_collections_works_correctly_with_unicode(
    workflow_app,
):
    expected_affiliations = ["HAL Hidden"]
    record = generate_record()
    record["authors"][0]["raw_affiliations"] = [
        {
            "value": u"Some longer description grand accélérateur national d'ions lourds. with proper keyword included"
        },
        {"value": u"Another one but this time with wrong keywords Fremilab included"},
    ]
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/curation/literature/assign-institutions".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": record["authors"]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        workflow = build_workflow(record)

        affiliations = affiliations_for_hidden_collections(workflow)
        assert affiliations == expected_affiliations


def test_replace_collection_to_hidden_sets_proper_hidden_collections_on_metadata(
    workflow_app,
):
    expected_collections = ["CDS Hidden", "Fermilab"]
    record = generate_record()
    record["authors"][0]["raw_affiliations"] = [
        {"value": "Some longer description CErN? with proper keyword included"},
        {"value": "Another one but this time with wrong keywords IN2P345 included"},
    ]
    record["authors"][1]["raw_affiliations"] = [
        {"value": "Blah blah blah fermilab, blah blah"}
    ]
    workflow = build_workflow(record)

    wf = replace_collection_to_hidden(workflow, None)
    assert wf.data["_collections"] == expected_collections


def test_replace_collection_to_hidden_sets_proper_hidden_collections_on_metadata_from_report_number(
    workflow_app,
):
    expected_collections = ["CDS Hidden", "Fermilab"]
    record = generate_record()
    record["report_numbers"] = [{"value": "CERN-2019"}, {"value": "FERMILAB-1923"}]
    workflow = build_workflow(record)

    wf = replace_collection_to_hidden(workflow, None)
    assert wf.data["_collections"] == expected_collections


def test_replace_collection_to_hidden_sets_proper_hidden_collections_on_metadata_from_report_number_and_affiliations(
    workflow_app,
):
    expected_collections = ["CDS Hidden", "Fermilab"]
    record = generate_record()
    record["authors"][0]["raw_affiliations"] = [
        {"value": "Another one but this time with wrong keywords Fermilab"},
    ]
    record["authors"][1]["raw_affiliations"] = [
        {"value": "Blah blah blah fermilab, blah blah"}
    ]
    record["report_numbers"] = [{"value": "CERN-2019"}]
    workflow = build_workflow(record)

    wf = replace_collection_to_hidden(workflow, None)
    assert wf.data["_collections"] == expected_collections


def test_normalize_journal_titles_in_references(workflow_app, insert_journals_in_db):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {"A Test Journal1": "Test.Jou.1", "Something not in db": "Something not in db"}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["book", "note", "report"],
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
                },
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")

        normalize_journal_titles(obj, None)

        assert (
            obj.data["references"][0]["reference"]["publication_info"]["journal_title"]
            == "Test.Jou.1"
        )
        assert obj.data["references"][0]["reference"]["publication_info"][
            "journal_record"
        ] == {"$ref": "http://localhost:5000/api/journals/1936475"}
        assert (
            obj.data["references"][1]["reference"]["publication_info"]["journal_title"]
            == "Something not in db"
        )


def test_normalize_collaborations(workflow_app):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "collaborations": [
            {
                "value": "Atlas II",
                "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"},
            },
            {"value": "Particle Data Group"},
            {"value": "Unknown"},
        ],
    }

    expected_collaborations = [
        {
            "value": "Atlas II",
            "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"},
        },
        {
            "value": "Particle Data Group",
            "record": {"$ref": "https://inspirehep.net/api/experiments/1800050"},
        },
        {"value": "Unknown"},
    ]

    expected_accelerator_experiments = [
        {"record": {"$ref": "https://inspirehep.net/api/experiments/1800050"}}
    ]
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/collaborations-normalization",
            json={
                "normalized_collaborations": expected_collaborations,
                "accelerator_experiments": expected_accelerator_experiments,
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_collaborations(obj, None)
        assert obj.data["collaborations"] == expected_collaborations
        assert obj.data["accelerator_experiments"] == expected_accelerator_experiments


def test_normalize_collaborations_no_collaboration(workflow_app):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "collaborations": [],
    }

    expected_collaborations = []

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    obj = normalize_collaborations(obj, None)
    assert obj.data["collaborations"] == expected_collaborations


def test_normalize_collaborations_in_workflow_with_already_existing_accelerator_experiments(
    workflow_app,
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "accelerator_experiments": [
            {"record": {"$ref": "https://inspirehep.net/api/experiments/1800050"}}
        ],
        "collaborations": [
            {
                "value": "Atlas II",
                "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"},
            },
            {"value": "Particle Data Group"},
            {"value": "Unknown"},
        ],
    }

    expected_collaborations = [
        {
            "value": "Atlas II",
            "record": {"$ref": "https://inspirebeta.net/api/experiments/9999"},
        },
        {
            "value": "Particle Data Group",
            "record": {"$ref": "https://inspirehep.net/api/experiments/1800050"},
        },
        {"value": "Unknown"},
    ]

    expected_accelerator_experiments = [
        {"record": {"$ref": "https://inspirehep.net/api/experiments/1800050"}}
    ]

    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/collaborations-normalization",
            json={
                "normalized_collaborations": expected_collaborations,
                "accelerator_experiments": expected_accelerator_experiments,
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_collaborations(obj, None)
        assert obj.data["collaborations"] == expected_collaborations
        assert obj.data["accelerator_experiments"] == expected_accelerator_experiments


@mock.patch("inspirehep.modules.workflows.tasks.actions.logging.Logger.info")
def test_normalize_affiliations_happy_flow(
    mock_logger,
    workflow_app,
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
                    }
                ],
            },
            {
                "full_name": "Latacz, Barbara",
                "raw_affiliations": [{"value": "CERN, Genève, Switzerland"}],
            },
        ],
    }
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [
                        {
                            "record": {
                                "$ref": "http://localhost:5000/api/institutions/903335"
                            },
                            "value": "Warsaw U.",
                        }
                    ],
                    [
                        {
                            "record": {
                                "$ref": "http:/localhost:5000/api/institutions/902725"
                            },
                            "value": "CERN",
                        }
                    ],
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_author_affiliations(obj, None)

        assert obj.data["authors"][0]["affiliations"] == [
            {
                "record": {"$ref": "http://localhost:5000/api/institutions/903335"},
                "value": "Warsaw U.",
            }
        ]
        assert obj.data["authors"][1]["affiliations"] == [
            {
                "record": {"$ref": "http:/localhost:5000/api/institutions/902725"},
                "value": "CERN",
            }
        ]

        assert mock_logger.mock_calls[-2][1] == (
            "(wf: %s) Normalized affiliations for author %s. Raw affiliations: %s. Assigned affiliations: %s",
            1,
            "Kowal, Michal",
            "Faculty of Physics, University of Warsaw, Pasteura 5 Warsaw",
            [
                {
                    "record": {"$ref": "http://localhost:5000/api/institutions/903335"},
                    "value": "Warsaw U.",
                }
            ],
        )


def test_normalize_affiliations_when_authors_has_two_happy_flow(
    workflow_app,
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
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [
                        {
                            "record": {
                                "$ref": "http://localhost:5000/api/institutions/903335"
                            },
                            "value": "Warsaw U.",
                        },
                        {
                            "record": {
                                "$ref": "http:/localhost:5000/api/institutions/902725"
                            },
                            "value": "CERN",
                        },
                    ]
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_author_affiliations(obj, None)

        assert obj.data["authors"][0]["affiliations"] == [
            {
                "record": {"$ref": "http://localhost:5000/api/institutions/903335"},
                "value": "Warsaw U.",
            },
            {
                "record": {"$ref": "http:/localhost:5000/api/institutions/902725"},
                "value": "CERN",
            },
        ]


def test_normalize_affiliations_when_lit_affiliation_missing_institution_ref(
    workflow_app,
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
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [
                        {
                            "record": {
                                "$ref": "http:/localhost:5000/api/institutions/902725"
                            },
                            "value": "CERN",
                        },
                        {
                            "value": "NCBJ, Swierk",
                        },
                    ]
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_author_affiliations(obj, None)

        assert ordered(obj.data["authors"][0]["affiliations"]) == ordered(
            [
                {
                    "value": "NCBJ, Swierk",
                },
                {
                    "record": {"$ref": "http:/localhost:5000/api/institutions/902725"},
                    "value": "CERN",
                },
            ]
        )


def test_normalize_affiliations_handle_not_found_affiliations(
    workflow_app,
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
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [[]],
                "ambiguous_affiliations": ["Non existing aff"],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = normalize_author_affiliations(obj, None)

        assert not obj.data["authors"][0].get("affiliations")


def test_link_institutions_with_affiliations(
    workflow_app, insert_literature_in_db, insert_institutions_in_db
):
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/assign-institutions",
            json={
                "authors": [
                    {
                        "full_name": "Kowal, Michal",
                        "affiliations": [
                            {
                                "value": "CERN",
                                "record": {
                                    "$ref": "http://localhost:5000//api/institutions/902725"
                                },
                            },
                            {
                                "value": "Warsaw U.",
                                "record": {
                                    "$ref": "https://inspirehep.net/api/institutions/903335"
                                },
                            },
                        ],
                    },
                    {
                        "full_name": "Latacz, Barbara",
                        "affiliations": [
                            {
                                "value": "CERN",
                                "record": {
                                    "$ref": "http://localhost:5000//api/institutions/902725"
                                },
                            }
                        ],
                    },
                ],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        record = {
            "_collections": ["Literature"],
            "titles": ["A title"],
            "document_type": ["report"],
            "authors": [
                {
                    "full_name": "Kowal, Michal",
                    "affiliations": [{"value": "CERN"}, {"value": "Warsaw U."}],
                },
                {"full_name": "Latacz, Barbara", "affiliations": [{"value": "CERN"}]},
            ],
        }

        obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
        obj = link_institutions_with_affiliations(obj, None)

        expected_affiliation_1 = {
            "record": {"$ref": "http://localhost:5000//api/institutions/902725"},
            "value": "CERN",
        }
        expected_affiliation_2 = {
            "record": {"$ref": "https://inspirehep.net/api/institutions/903335"},
            "value": "Warsaw U.",
        }

        assert expected_affiliation_1 == obj.data["authors"][0]["affiliations"][0]
        assert expected_affiliation_2 == obj.data["authors"][0]["affiliations"][1]
        assert expected_affiliation_1 == obj.data["authors"][1]["affiliations"][0]


@mock.patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_core_selection_wf_already_created_show_created_wf(
    mocked_api_request_magpie, mocked_classifer_api, workflow_app
):
    record = {
        "_collections": ["Literature"],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["report"],
        "collaborations": [{"value": "SHIP"}],
        "control_number": 123456,
    }
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/collaborations-normalization",
            json={"normalized_collaborations": [], "accelerator_experiments": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/normalize-journal-titles",
            json={"normalized_journal_titles": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        request_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        workflow_object = workflow_object_class.create(
            data=record, id_user=None, data_type="hep"
        )
        workflow_object.extra_data["source_data"] = {
            "data": record,
            "extra_data": {"source_data": {"data": record}},
        }
        workflow_object.save()
        start("article", object_id=workflow_object.id)
        current_search.flush_and_refresh("holdingpen-hep")
        assert len(core_selection_wf_already_created(123456)) == 0

        workflow_object = workflow_object_class.create(
            data=record, id_user=None, data_type="hep"
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
        "_collections": ["Literature"],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["report"],
        "collaborations": [{"value": "SHIP"}],
        "control_number": 123456,
    }
    workflow_object = workflow_object_class.create(
        data=record, id_user=None, data_type="hep"
    )
    workflow_object.extra_data["_task_history"] = ["Should be removed"]
    workflow_object.extra_data["_error_msg"] = ["Should be removed"]
    workflow_object.extra_data["source_data"] = ["Should be removed"]
    workflow_object.extra_data["restart-count"] = "Should be removed"
    workflow_object.extra_data["auto-approved"] = True
    workflow_object.save()

    assert (
        WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="core_selection")
        ).count()
        == 0
    )

    create_core_selection_wf(workflow_object, None)

    wf = WorkflowObjectModel.query.filter(
        WorkflowObjectModel.workflow.has(name="core_selection")
    ).one()
    assert wf.data == workflow_object.data
    assert "_error_msg" not in wf.extra_data
    assert "restart_count" not in wf.extra_data
    assert workflow_object.extra_data["_task_history"] != wf.extra_data["_task_history"]
    assert wf.status == ObjectStatus.HALTED

    current_search.flush_and_refresh("holdingpen-hep")

    create_core_selection_wf(workflow_object, None)

    # ensure that new core_selection_wf is not created when one already exists
    new_query_wfs = WorkflowObjectModel.query.filter(
        WorkflowObjectModel.workflow.has(name="core_selection")
    ).one()
    assert new_query_wfs.id == wf.id


def test_create_core_selection_workflow_task_wont_create_when_record_is_core(
    workflow_app,
):
    record = {
        "_collections": ["Literature"],
        "titles": [
            {"title": "A title"},
        ],
        "document_type": ["report"],
        "collaborations": [{"value": "SHIP"}],
        "control_number": 123456,
        "core": True,
    }
    workflow_object = workflow_object_class.create(
        data=record, id_user=None, data_type="hep"
    )

    assert (
        WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="core_selection")
        ).count()
        == 0
    )

    create_core_selection_wf(workflow_object, None)

    assert (
        WorkflowObjectModel.query.filter(
            WorkflowObjectModel.workflow.has(name="core_selection")
        ).count()
        == 0
    )


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.extract_references_from_pdf",
    return_value=[],
)
def test_refextract_when_document_type_is_xml(
    mock_extract_refs, workflow_app, insert_institutions_in_db
):
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "authors": [
            {
                "full_name": "Easter, Paul J.",
                "ids": [{"schema": "INSPIRE BAI", "value": "P.J.Easter.2"}],
                "raw_affiliations": [
                    {"value": "Belgrade, Serbia"},
                ],
                "signature_block": "EASTARp",
                "uuid": "4c4b7fdf-04ae-421f-bcab-bcc5907cea4e",
            }
        ],
    }
    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    refextract(obj, None)
    assert not obj.data.get("references")


def test_refextract_from_text_data(insert_hep_records_into_db, workflow_app, mocked_external_services):
    """TODO: record cassette and remove mock request"""
    with override_config(FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE=True):
        schema = load_schema("hep")
        subschema = schema["properties"]["acquisition_source"]

        data = {"acquisition_source": {"source": "submitter"}}
        extra_data = {
            "formdata": {
                "references": "M.R. Douglas, G.W. Moore, D-branes, quivers, and ALE instantons, arXiv:hep-th/9603167",
            },
        }
        assert validate(data["acquisition_source"], subschema) is None

        obj = workflow_object_class.create(
            data=data, extra_data=extra_data, id_user=1, data_type="hep"
        )

        refextract(obj, None) is None
        assert obj.data["references"][0]["raw_refs"][0]["source"] == "submitter"
        assert "references" in obj.data


def test_refextract_from_url(insert_hep_records_into_db, workflow_app, mocked_external_services):
    """TODO: record cassette and remove mock request"""
    with override_config(FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE=True):
        schema = load_schema("hep")
        subschema = schema["properties"]["acquisition_source"]

        data = {
            "documents": [
                {"url": "https://arxiv.org/pdf/2204.13950.pdf", "fulltext": True}
            ],
            "acquisition_source": {"source": "submitter"},
        }

        assert validate(data["acquisition_source"], subschema) is None

        obj = workflow_object_class.create(data=data, id_user=1, data_type="hep")

        refextract(obj, None) is None
        assert obj.data["references"][0]["raw_refs"][0]["source"] == "submitter"
        assert "references" in obj.data


def test_remove_inspire_categories_derived_from_core_arxiv_categories(workflow_app):
    expected_inspire_categories = [
        {"source": "arxiv", "term": "Astrophysics"},
        {"source": "arxiv", "term": "Gravitation and Cosmology"},
        {"source": "user", "term": "Other"},
        {"term": "Other"},
    ]
    record = {
        "_collections": ["Literature"],
        "titles": ["A title"],
        "document_type": ["report"],
        "arxiv_eprints": [
            {
                "categories": ["hep-ph", "astro-ph.CO", "gr-qc", "hep-ex", "hep-th"],
                "value": "2207.01633",
            }
        ],
        "inspire_categories": [
            {"source": "arxiv", "term": "Phenomenology-HEP"},
            {"source": "arxiv", "term": "Astrophysics"},
            {"source": "arxiv", "term": "Gravitation and Cosmology"},
            {"source": "arxiv", "term": "Experiment-HEP"},
            {"source": "arxiv", "term": "Theory-HEP"},
            {"source": "user", "term": "Other"},
            {"term": "Other"},
        ],
    }
    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    remove_inspire_categories_derived_from_core_arxiv_categories(obj, None)
    schema = load_schema("hep")
    subschema = schema["properties"]["inspire_categories"]

    assert ordered(obj.data["inspire_categories"]) == ordered(
        expected_inspire_categories
    )
    assert validate(obj.data["inspire_categories"], subschema) is None


def test_extract_journal_info_hep_request(workflow_app):
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)'},
        ],
    }
    assert validate(data['publication_info'], subschema) is None
    obj = workflow_object_class.create(data=data, id_user=1, data_type="hep")

    with override_config(FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE=True):
        with requests_mock.Mocker() as mock_request:
            mock_request.register_uri(
                "POST",
                "{}/extract_journal_info".format(
                    current_app.config["REFEXTRACT_SERVICE_URL"]
                ),
                json={
                    "extracted_publication_infos": [
                        {
                            "title": "A test title",
                            "year": 2014,
                            'title': 'A test title'
                        }
                    ]
                },
            )

            expected = [
                {
                    'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)',
                    'year': 2014,
                    'journal_title': 'A test title'
                }
            ]
            assert extract_journal_info(obj, None) is None
            result = obj.data['publication_info']

            assert validate(result, subschema) is None
            assert expected == result
