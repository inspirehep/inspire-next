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

import json
import mock
import os
import pkg_resources

import pytest

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search.api import current_search_client as es
from invenio_workflows import (
    WorkflowEngine,
    start,
    workflow_object_class,
)

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.tasks.actions import normalize_journal_titles

from calls import core_record

from mocks import (
    fake_beard_api_request,
    fake_download_file,
    fake_magpie_api_request,
)

from utils import _delete_record


@pytest.fixture(scope='function')
def insert_journals_in_db(workflow_app):
    """Temporarily add few journals in the DB"""

    journal_no_pro_and_ref = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_refereed.json')))

    journal_pro_and_ref = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_refereed_and_proceedings.json')))

    with db.session.begin_nested():
        journal_no_pro_and_ref = InspireRecord.create_or_update(
            journal_no_pro_and_ref, skip_files=False)
        journal_no_pro_and_ref.commit()
        journal_pro_and_ref = InspireRecord.create_or_update(
            journal_pro_and_ref, skip_files=False)
        journal_pro_and_ref.commit()
    db.session.commit()
    es.indices.refresh('records-journals')

    yield

    _delete_record('jou', 1936475)
    _delete_record('jou', 1936476)
    es.indices.refresh('records-journals')


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
@mock.patch('inspirehep.modules.workflows.tasks.actions.get_document_in_workflow')
def test_refextract_from_pdf(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_is_pdf_link,
    mocked_package_download,
    mocked_arxiv_download,
    workflow_app,
    mocked_external_services
):
    """Test refextract by going through the entire workflow."""

    '''Import the cited record'''

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
      'abstracts': [
        {
          'source': 'arXiv',
          'value': 'The effects on the non-relativistic dynamics of a system compound by two electrons interacting by a Coulomb potential and with an external harmonic\r\noscillator potential, confined to move in a two dimensional Euclidean space, are investigated. In particular, it is shown that it is possible to determine\r\nexactly and in a closed form a finite portion of the energy spectrum and the associated eigeinfunctions for the Schr\\\"odinger equation describing the relative motion of the electrons, by putting it into the form of a biconfluent Heun equation. In the same framework, another set of solutions of this type can\r\nbe straightforwardly obtained for the case when the two electrons are submitted also to an external constant magnetic field.'
        }
      ],
      'arxiv_eprints': [
        {
          'categories': ['quant-ph', 'cond-mat.mes-hall', 'cond-mat.str-el', 'math-ph', 'math.MP'],
          'value': '1308.0815'
        }
      ],
      'authors': [
        {'full_name': 'Caruso, F.'},
        {'full_name': 'Martins, J.'},
        {'full_name': 'Oguri, V.'},
      ],
      'document_type': ['article'],
      'dois': [
        {'value': '10.1016/j.aop.2014.04.023'}
      ],
      'titles': [
        {
          'source': 'arXiv',
          'title': 'Solving a two-electron quantum dot model in terms of polynomial solutions of a Biconfluent Heun equation'
        }
      ],
    }

    record = InspireRecord.create(cited_record_json, id_=None)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    es.indices.refresh('records-hep')

    '''Import the citing record'''

    record, categories = core_record()

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
        'ARXIV_CATEGORIES': categories,
    }

    with workflow_app.app_context():
        with mock.patch.dict(workflow_app.config, extra_config):
            citing_doc_workflow_uuid = start('article', [record])

        citing_doc_eng = WorkflowEngine.from_uuid(citing_doc_workflow_uuid)
        citing_doc_obj = citing_doc_eng.processed_objects[0]

        assert citing_doc_obj.data['references'][7]['record']['$ref'] == cited_doc_obj.data['control_number']

    '''Cleanup stuff'''

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(
        pid_type='lit',
        pid_value=record['control_number']
    )

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()
