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

import pkg_resources
import pytest
from flask import current_app
from six import binary_type

from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    get_classifier_url,
    prepare_payload,
    guess_coreness,
)
from mock import patch
from mocks import MockEng, MockObj


HIGGS_ONTOLOGY = '''<?xml version="1.0" encoding="UTF-8" ?>

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
'''


def test_get_classifier_api_url_from_configuration():
    config = {'CLASSIFIER_API_URL': 'https://inspire-classifier.web.cern.ch'}

    with patch.dict(current_app.config, config):
        expected = 'https://inspire-classifier.web.cern.ch/api/predict/core'
        result = get_classifier_url()

        assert expected == result


def test_get_classifier_api_url_returns_none_when_not_in_configuration():
    config = {'CLASSIFIER_API_URL': ''}

    with patch.dict(current_app.config, config):
        assert get_classifier_url() is None


def test_prepare_payload():
    record = {
        'titles': [
            {
                'title': 'Effects of top compositeness',
            },
        ],
        'abstracts': [
            {
                'value': 'We investigate the effects of (...)',
            },
        ],
    }

    expected = {
        'title': 'Effects of top compositeness',
        'abstract': 'We investigate the effects of (...)',
    }
    result = prepare_payload(record)

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
def test_guess_coreness_fails_without_a_classifier_url(g_b_u):
    g_b_u.return_value = ''

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert 'relevance_prediction' not in obj.extra_data


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
def test_guess_coreness_does_not_fail_when_request_fails(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = 'https://inspire-classifier.web.cern.ch/api/predict/does-not-exist'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert 'relevance_prediction' not in obj.extra_data


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
@patch('inspirehep.modules.workflows.tasks.classifier.json_api_request')
def test_guess_coreness_when_core(j_a_r, g_b_u):
    j_a_r.return_value = {
        'prediction': 'core',
        'scores': {
            'core_score': 0.7,
            'non_core_score': 0.2,
            'rejected_score': 0.1,
        },
    }
    g_b_u.return_value = 'https://inspire-classifier.web.cern.ch/api/predict/core'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.7,
        'decision': 'CORE',
        'scores': {
            'CORE': 0.7,
            'Non-CORE': 0.2,
            'Rejected': 0.1,
        },
        'relevance_score': 0.7,
    }


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
@patch('inspirehep.modules.workflows.tasks.classifier.json_api_request')
def test_guess_coreness_when_non_core(j_a_r, g_b_u):
    j_a_r.return_value = {
        'prediction': 'non-core',
        'scores': {
            'core_score': 0.3,
            'non_core_score': 0.6,
            'rejected_score': 0.1,
        },
    }
    g_b_u.return_value = 'https://inspire-classifier.web.cern.ch/api/predict/core'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.6,
        'decision': 'Non-CORE',
        'scores': {
            'CORE': 0.3,
            'Non-CORE': 0.6,
            'Rejected': 0.1,
        },
        'relevance_score': 0.6,
    }


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
@patch('inspirehep.modules.workflows.tasks.classifier.json_api_request')
def test_guess_coreness_when_rejected(j_a_r, g_b_u):
    j_a_r.return_value = {
        'prediction': 'rejected',
        'scores': {
            'core_score': 0.1,
            'non_core_score': 0.1,
            'rejected_score': 0.8,
        },
    }
    g_b_u.return_value = 'https://inspire-classifier.web.cern.ch/api/predict/core'

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.8,
        'decision': 'Rejected',
        'scores': {
            'CORE': 0.1,
            'Non-CORE': 0.1,
            'Rejected': 0.8,
        },
        'relevance_score': 0.8,
    }


@pytest.fixture()
def higgs_ontology(tmpdir):
    ontology = tmpdir.join('HEPont.rdf')
    ontology.write(HIGGS_ONTOLOGY)
    yield str(ontology)


@patch('inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow')
def test_classify_paper_with_fulltext(get_document_in_workflow, tmpdir, higgs_ontology):
    obj = MockObj({}, {})
    eng = MockEng()
    fulltext = tmpdir.join('fulltext.txt')
    fulltext.write('Higgs boson')
    get_document_in_workflow.return_value.__enter__.return_value = binary_type(fulltext)
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is True


@patch('inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow')
def test_classify_paper_with_no_fulltext(get_document_in_workflow, higgs_ontology):
    data = {
        'titles': [
            {
                'title': 'Some title',
            },
        ],
        'abstracts': [
            {
                'value': 'Very interesting paper about the Higgs boson.'
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_document_in_workflow.return_value.__enter__.return_value = None
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is False


@patch('inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow')
def test_classify_paper_uses_keywords(get_document_in_workflow, higgs_ontology):
    data = {
        'titles': [
            {
                'title': 'Some title',
            },
        ],
        'keywords': [
            {
                'value': 'Higgs boson',
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_document_in_workflow.return_value.__enter__.return_value = None
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is False


@patch('inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow')
def test_classify_paper_does_not_raise_on_unprintable_keywords(get_document_in_workflow, higgs_ontology):
    paper_with_unprintable_keywords = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1802.08709.pdf'))

    get_document_in_workflow.return_value.__enter__.return_value = paper_with_unprintable_keywords
    get_document_in_workflow.return_value.__exit__.return_value = None

    obj = MockObj({}, {})
    eng = MockEng()

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)  # Does not raise.
