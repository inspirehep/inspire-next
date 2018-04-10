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
import os
from mock import patch
import pkg_resources

import pytest

from invenio_db import db
from invenio_search.api import current_search_client as es
from invenio_workflows import workflow_object_class

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.tasks.actions import (
    normalize_journal_titles,
    refextract,
)

from mocks import MockEng, MockObj

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


@patch('inspirehep.modules.workflows.tasks.actions.get_document_in_workflow')
def test_refextract_from_pdf(mock_get_document_in_workflow):

    # Insert the record which is going to be cited
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'On global solutions to the Navier-Stokes system with large  $L^{3,\\infty}$ initial data'}],
        'arxiv_eprints': [
            {'categories': ['math.AP'], 'value': '1603.03211'}
        ],
        'control_number': 3112,
        'authors': [
            {'full_name': 'Barker, T.'},
            {'full_name': 'Seregin, G.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'his paper addresses a question concerning the behaviour of a sequence of\r\nglobal solutions to the Navier-Stokes equations, with the corresponding\r\nsequence of smooth initial data being bounded in the (non-energy class) weak\r\nLebesgue space $L^{3,\\infty}$. It is closely related to the question of what\r\nwould be a reasonable definition of global weak solutions with a non-energy\r\nclass of initial data, including the aforementioned Lorentz space. This paper\r\ncan be regarded as an extension of a similar problem regarding the Lebesgue\r\nspace $L_3$ to the weak Lebesgue space $L^{3,\\infty}$, whose norms are both\r\nscale invariant with the respect to the Navier-Stokes scaling.'}
        ],
    }

    record = InspireRecord.create(cited_record_json, id_=None, skip_files=True)
    record.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    # Insert the citing record
    mock_get_document_in_workflow.return_value.__enter__.return_value = pkg_resources.resource_filename(
        __name__,
        os.path.join('fixtures', '1704.00452.pdf'),
    )
    mock_get_document_in_workflow.return_value.__exit__.return_value = None

    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {'acquisition_source': {'source': 'arXiv'}}
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert obj.data['references'][0]['raw_refs'][0]['source'] == 'arXiv'

    # Assert that the cited record is identified correctly
    assert obj.data['references'][2]['record']['$ref'] == 'http://localhost:5000/api/literature/3112'

    record.delete()
    record.commit()


@patch('inspirehep.modules.workflows.tasks.actions.get_document_in_workflow')
def test_refextract_from_text(mock_get_document_in_workflow):

    # Insert the record which is going to be cited
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'On global solutions to the Navier-Stokes system with large  $L^{3,\\infty}$ initial data'}],
        'arxiv_eprints': [
            {'categories': ['math.AP'], 'value': '1603.03211'}
        ],
        'control_number': 3112,
        'authors': [
            {'full_name': 'Barker, T.'},
            {'full_name': 'Seregin, G.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'his paper addresses a question concerning the behaviour of a sequence of\r\nglobal solutions to the Navier-Stokes equations, with the corresponding\r\nsequence of smooth initial data being bounded in the (non-energy class) weak\r\nLebesgue space $L^{3,\\infty}$. It is closely related to the question of what\r\nwould be a reasonable definition of global weak solutions with a non-energy\r\nclass of initial data, including the aforementioned Lorentz space. This paper\r\ncan be regarded as an extension of a similar problem regarding the Lebesgue\r\nspace $L_3$ to the weak Lebesgue space $L^{3,\\infty}$, whose norms are both\r\nscale invariant with the respect to the Navier-Stokes scaling.'}
        ],
    }

    record = InspireRecord.create(cited_record_json, id_=None, skip_files=True)
    record.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    # Insert the reference to the above inserted record
    mock_get_document_in_workflow.return_value.__enter__.return_value = None
    mock_get_document_in_workflow.return_value.__exit__.return_value = None

    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {'acquisition_source': {'source': 'submitter'}}
    extra_data = {
        'formdata': {
            'references': '[2] T. Baker and G. Seregin, On global solutions to the Navier-Stokes system with large L3,∞ initial data, arXiv:1603.03211.',
        },
    }
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert obj.data['references'][0]['raw_refs'][0]['source'] == 'submitter'

    # Assert that the cited record is identified correctly
    assert obj.data['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/3112'

    record.delete()
    record.commit()


def test_refextract_from_raw_refs():

    # Insert the record which is going to be cited
    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'On global solutions to the Navier-Stokes system with large  $L^{3,\\infty}$ initial data'}],
        'arxiv_eprints': [
            {'categories': ['math.AP'], 'value': '1603.03211'}
        ],
        'control_number': 3112,
        'authors': [
            {'full_name': 'Barker, T.'},
            {'full_name': 'Seregin, G.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'his paper addresses a question concerning the behaviour of a sequence of\r\nglobal solutions to the Navier-Stokes equations, with the corresponding\r\nsequence of smooth initial data being bounded in the (non-energy class) weak\r\nLebesgue space $L^{3,\\infty}$. It is closely related to the question of what\r\nwould be a reasonable definition of global weak solutions with a non-energy\r\nclass of initial data, including the aforementioned Lorentz space. This paper\r\ncan be regarded as an extension of a similar problem regarding the Lebesgue\r\nspace $L_3$ to the weak Lebesgue space $L^{3,\\infty}$, whose norms are both\r\nscale invariant with the respect to the Navier-Stokes scaling.'}
        ],
    }

    record = InspireRecord.create(cited_record_json, id_=None, skip_files=True)
    record.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    # Insert the reference to the above inserted record
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    data = {
        'references': [
            {
                'raw_refs': [
                    {
                        'schema': 'text',
                        'source': 'arXiv',
                        'value': '[2] T. Baker and G. Seregin, On global solutions to the Navier-Stokes system with large L3,∞ initial data, arXiv:1603.03211.'
                    },
                ],
            },
        ],
    }
    assert validate(data['references'], subschema) is None

    obj = MockObj(data, {})
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert 'reference' in obj.data['references'][0]

    # Assert that the cited record is identified correctly
    assert obj.data['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/3112'

    record.delete()
    record.commit()
