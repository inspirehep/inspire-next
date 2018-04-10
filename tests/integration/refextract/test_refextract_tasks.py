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
from tempfile import mkstemp

import pytest
from flask import current_app
from mock import patch
import pkg_resources

from invenio_db import db
from invenio_search.api import current_search_client as es

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.refextract.tasks import create_journal_kb_file
from inspirehep.utils.record_getter import get_db_record
from inspirehep.modules.workflows.tasks.actions import refextract

from mocks import MockEng, MockObj


@pytest.fixture
def jhep_with_malformed_title(app):
    """Temporarily add a malformed title to the JHEP record."""
    record = get_db_record('jou', 1213103)
    record['title_variants'].append('+++++')
    record = InspireRecord.create_or_update(record)
    record.commit()

    yield

    record = get_db_record('jou', 1213103)
    record['title_variants'] = record['title_variants'][:-1]
    record = InspireRecord.create_or_update(record)
    record.commit()


def test_create_journal_kb_file(app):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    with open(path, 'r') as fd:
        journal_kb = fd.read().splitlines()

        assert 'JHEP---JHEP' in journal_kb
        '''short_title -> short_title'''

        assert 'THE JOURNAL OF HIGH ENERGY PHYSICS JHEP---JHEP' in journal_kb
        '''journal_title.title -> short_title, normalization is applied'''

        assert 'JOURNAL OF HIGH ENERGY PHYSICS---JHEP' in journal_kb
        '''title_variants -> short_title'''

    os.close(temporary_fd)
    os.remove(path)


def test_create_journal_kb_file_handles_malformed_title_variants(jhep_with_malformed_title):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    with open(path, 'r') as fd:
        journal_kb = fd.read().splitlines()

        assert '---JHEP' not in journal_kb

    os.close(temporary_fd)
    os.remove(path)


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
        'control_number': 1800000,
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
        os.path.join('../workflows', 'fixtures', '1704.00452.pdf'),
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
    assert obj.data['references'][2]['record']['$ref'] == 'http://localhost:5000/api/literature/1800000'

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
        'control_number': 1800000,
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
    assert obj.data['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/1800000'

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
        'control_number': 1800000,
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
    assert obj.data['references'][0]['record']['$ref'] == 'http://localhost:5000/api/literature/1800000'

    record.delete()
    record.commit()
