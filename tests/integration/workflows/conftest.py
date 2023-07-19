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
import random
import re
import sys
import uuid

import mock
import pkg_resources
import pytest
import requests_mock
from flask_alembic import Alembic
from invenio_db import db
from invenio_db.utils import drop_alembic_version_table
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search

from inspirehep.factory import create_app
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import (
    init_authentication_token,
    init_users_and_permissions,
)
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import _get_headers_for_hep_root_table_request

# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "helpers"))


from factories.db.invenio_records import (
    cleanup as invenio_records_factory_cleanup,
)  # noqa

HIGGS_ONTOLOGY = """<?xml version="1.0" encoding="UTF-8" ?>

<rdf:RDF xmlns="http://www.w3.org/2004/02/skos/core#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

    <Concept rdf:about="http://cern.ch/thesauri/HEPontology.rdf#Higgsparticle">
        <prefLabel xml:lang="en">Higgs particle</prefLabel>
        <altLabel xml:lang="en">Higgs boson</altLabel>
        <hiddenLabel xml:lang="en">Higgses</hiddenLabel>
        <note xml:lang="en">core</note>
    </Concept>

</rdf:RDF>
"""


@pytest.fixture(scope="module")
def higgs_ontology(tmpdir_factory):
    ontology = tmpdir_factory.mktemp("data").join("HEPont.rdf")
    ontology.write(HIGGS_ONTOLOGY)
    yield str(ontology)


@pytest.fixture(scope="module")
def workflow_app(higgs_ontology):
    """Flask application with no records and function scope.

    .. deprecated:: 2017-09-18
       Use ``app`` instead.
    """
    RT_URL = "http://rt.inspire"
    GROBID_URL = "http://grobid_url.local"

    with requests_mock.Mocker() as m:
        m.register_uri(
            requests_mock.ANY,
            re.compile(".*" + RT_URL + ".*"),
            status_code=200,
            text="Status 200",
        )

        app = create_app(
            CELERY_TASK_ALWAYS_EAGER=True,
            CELERY_CACHE_BACKEND="memory",
            CELERY_TASK_EAGER_PROPAGATES=True,
            CELERY_RESULT_BACKEND="cache",
            CFG_BIBCATALOG_SYSTEM_RT_URL=RT_URL,
            CLASSIFIER_API_URL="http://example.com/classifier",
            DEBUG=False,
            GROBID_URL=GROBID_URL,
            HEP_ONTOLOGY_FILE=higgs_ontology,
            PRODUCTION_MODE=True,
            LEGACY_ROBOTUPLOAD_URL=("http://localhost:1234"),
            MAGPIE_API_URL="http://example.com/magpie",
            WORKFLOWS_FILE_LOCATION="/",
            WORKFLOWS_MATCH_REMOTE_SERVER_URL="http://legacy_search.endpoint/",
            WTF_CSRF_ENABLED=False,
        )

    app.extensions["invenio-search"].register_mappings(
        "records", "inspirehep.modules.records.mappings"
    )

    with app.app_context():
        with mock.patch(
            "inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async"
        ):
            yield app


@pytest.fixture
def workflow_api(workflow_app):
    """Flask API application."""
    yield workflow_app.wsgi_app.mounts["/api"]


@pytest.fixture
def workflow_api_client(workflow_api):
    """Flask test client for the API application."""
    with workflow_api.test_client() as client:
        yield client


def drop_all(app):
    db.drop_all()
    drop_alembic_version_table()
    list(current_search.delete(ignore=[404]))


def create_all(app):
    alembic = Alembic(app=app)
    alembic.upgrade()

    _es = app.extensions["invenio-search"]
    list(_es.create(ignore=[400]))

    init_all_storage_paths()
    init_users_and_permissions()
    init_authentication_token()


@pytest.fixture(autouse=True)
def cleanup_workflows(workflow_app):
    db.session.close_all()
    drop_all(app=workflow_app)
    create_all(app=workflow_app)
    invenio_records_factory_cleanup()


@pytest.fixture
def mocked_external_services(workflow_app):
    grobid_response = pkg_resources.resource_string(
        __name__, os.path.join("fixtures", "grobid_1407.7587.xml")
    )
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(".*(indexer|localhost).*"),
            real_http=True,
        )
        requests_mocker.register_uri(
            "POST",
            re.compile(
                "https?://localhost:1234.*",
            ),
            text="[INFO]",
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                ".*" + workflow_app.config["WORKFLOWS_MATCH_REMOTE_SERVER_URL"] + ".*"
            ),
            status_code=200,
            json=[],
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                ".*"
                + workflow_app.config["CFG_BIBCATALOG_SYSTEM_RT_URL"]
                + "/ticket/new.*"
            ),
            status_code=200,
            text="RT/3.8.7 200 Ok\n\n# Ticket 1 created.\n# Ticket 1 updated.",
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                ".*"
                + workflow_app.config["CFG_BIBCATALOG_SYSTEM_RT_URL"]
                + "/ticket/.*/comment"
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                ".*"
                + workflow_app.config["CFG_BIBCATALOG_SYSTEM_RT_URL"]
                + "/ticket/.*/edit"
            ),
            status_code=200,
            text="Irrelevant part 1 of message \nIrrelevant part 2 of message \n# Ticket 1 updated.",
        )
        requests_mocker.register_uri(
            "POST",
            "http://grobid_url.local/api/processHeaderDocument",
            text=grobid_response.decode("utf-8"),
            headers={"content-type": "application/xml"},
            status_code=200,
        )
        requests_mocker.register_uri(
            "POST",
            "http://grobid_url.local/api/processFulltextDocument",
            headers={"content-type": "application/xml"},
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            "{inspirehep_url}/literature/workflows_record_sources".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            "{inspirehep_url}/literature/workflows_record_sources".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/exact-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/matcher/fuzzy-match".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"matched_data": {}},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "http://web:8000/curation/literature/affiliations-normalization",
            json={
                "normalized_affiliations": [
                    [],
                    [],
                ],
                "ambiguous_affiliations": [],
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "GET",
            "{inspirehep_url}/curation/literature/assign-institutions".format(
                inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            json={"authors": [{"full_name": "test author"}]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "POST",
            "{}/extract_references_from_url".format(
                workflow_app.config["REFEXTRACT_SERVICE_URL"]
            ),
            json={
                "extracted_references": [
                    {
                        "author": ["G. Chalons, M. D. Goodsell, S. Kraml"],
                        "journal_page": ["113"],
                        "journal_reference": ["JHEP,1904,113"],
                        "journal_title": ["JHEP"],
                        "journal_volume": ["1904"],
                        "journal_year": ["2019"],
                        "linemarker": ["67"],
                        "misc": ["H. Reyes-González, S. L. Williamson"],
                        "raw_ref": [
                            "[67] G. Chalons, M. D. Goodsell, S. Kraml, H. Reyes-González, S. L. Williamson, “LHC limits on gluinos and squarks in the minimal Dirac gaugino model”, JHEP 04, 113 (2019), arXiv:1812.09293."
                        ],
                        "reportnumber": ["arXiv:1812.09293"],
                        "title": [
                            "LHC limits on gluinos and squarks in the minimal Dirac gaugino model"
                        ],
                        "year": ["2019"],
                    },
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "POST",
            "{}/matcher/linked_references/".format(
                workflow_app.config["INSPIREHEP_URL"]
            ),
            json={
                "references": [
                    {
                        "record": {
                            "$ref": "http://localhost:5000/api/literature/1000",
                        },
                        "raw_refs": [
                            {
                                "source": "submitter",
                                "schema": "That's a schema",
                                "value": "That's a reference",
                            }
                        ],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "POST",
            "{}/extract_references_from_text".format(
                workflow_app.config["REFEXTRACT_SERVICE_URL"]
            ),
            json={
                "extracted_references": [
                    {
                        "author": [
                            "G. Chalons, M. D. Goodsell, S. Kraml, H. Reyes-González, S. L. Williamson"
                        ],
                        "journal_page": ["113"],
                        "journal_reference": ["JHEP,1904,113"],
                        "journal_title": ["JHEP"],
                        "journal_volume": ["1904"],
                        "journal_year": ["2019"],
                        "linemarker": ["67"],
                        "raw_ref": [
                            "[67] G. Chalons, M. D. Goodsell, S. Kraml, H. Reyes-Gonz´ alez, S. L. Williamson, “LHC limits on gluinos and squarks in the minimal Dirac gaugino model”, JHEP 04, 113 (2019), arXiv:1812.09293."
                        ],
                        "reportnumber": ["arXiv:1812.09293"],
                        "title": [
                            "LHC limits on gluinos and squarks in the minimal Dirac gaugino model"
                        ],
                        "year": ["2019"],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        requests_mocker.register_uri(
            "POST",
            "{}/extract_journal_info".format(
                workflow_app.config["REFEXTRACT_SERVICE_URL"]
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
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        if "INSPIREHEP_URL" in workflow_app.config:
            # HEP record upload
            requests_mocker.register_uri(
                "POST",
                re.compile(
                    ".*"
                    + workflow_app.config["INSPIREHEP_URL"]
                    + "/(literature|aurhors)/?"
                ),
                status_code=201,
                json={
                    "metadata": {
                        "control_number": random.randint(10000, 99999),
                    },
                    "uuid": str(uuid.uuid4()),
                },
            )

        yield requests_mocker


@pytest.fixture
def record_from_db(workflow_app):
    json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": ["Literature"],
        "document_type": ["article"],
        "titles": [{"title": "Fancy title for a new record"}],
        "arxiv_eprints": [{"categories": ["hep-th"], "value": "1407.7587"}],
        "control_number": 1234,
        "authors": [
            {"full_name": "Maldacena, J."},
            {"full_name": "Strominger, A."},
        ],
        "abstracts": [{"source": "arxiv", "value": "A basic abstract."}],
        "report_numbers": [{"value": "DESY-17-036"}],
    }
    record = InspireRecord.create(json, id_=None, skip_files=True)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    current_search.flush_and_refresh("records-hep")

    yield record

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(pid_type="lit", pid_value=record["control_number"])

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()


@pytest.fixture
def record_to_merge(workflow_app):
    json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "_collections": ["Literature"],
        "authors": [
            {
                "full_name": "Jessica, Jones",
            },
        ],
        "document_type": ["thesis"],
        "number_of_pages": 100,
        "preprint_date": "2016-11-16",
        "public_notes": [{"source": "arXiv", "value": "100 pages, 36 figures"}],
        "titles": [{"title": "Alias Investigations"}],
        "dois": [{"value": "10.1007/978-3-319-15001-7"}],
    }
    record = InspireRecord.create(json, id_=None, skip_files=True)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    current_search.flush_and_refresh("records-hep")

    yield record

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(pid_type="lit", pid_value=record["control_number"])

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()
