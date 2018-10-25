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
        expected = 'https://inspire-classifier.web.cern.ch/api/classifier'
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
def test_guess_coreness_when_core(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = 'https://inspire-classifier.web.cern.ch/api/classifier'

    obj = MockObj({
        "titles": [
            {
                "title": "Instanton Corrections for m and Ω"
            }
        ],
        "abstracts": [
            {
                "value": "In this paper, we study instanton corrections in the N=2⋆ gauge theory by using its description in string \
                theory as a freely-acting orbifold. The latter is used to compute, using the worldsheet, the deformation of the Yang–Mills \
                action. In addition, we calculate the deformed instanton partition function, thus extending the results to the non-perturbative \
                sector of the gauge theory. As we point out, the structure of the deformation is extremely similar to the Ω-deformation, therefore \
                confirming the universality of the construction. Finally, we comment on the realisation of the mass deformation using physical \
                vertex operators by exploiting the equivalence between Scherk–Schwarz deformations and freely-acting orbifolds."
            }
        ]
    }, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.9612694382667542,
        'decision': 'CORE',
        'scores': {
            'CORE': 0.9612694382667542,
            'Non-CORE': 0.02646675705909729,
            'Rejected': 0.012263836339116096,
        },
        'relevance_score': 1.9612694382667542,
    }


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
def test_guess_coreness_when_non_core(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = 'https://inspire-classifier.web.cern.ch/api/classifier'

    obj = MockObj({
        "titles": [
            {
                "title": "Relative Biological Effectiveness of Antiprotons the AD-4/ACE Experiment"
            }
        ],
        "abstracts": [
            {
                "value": "Particle beam cancer therapy was introduced by Robert R. Wilson in 1947 based on the advantageous \
                depth dose profile of a particle beam in human-like targets (water) compared to X-rays or electrons. Heavy charged \
                particles have a finite range in water and present a distinct peak of dose deposition at the end of their range. \
                Early work in Berkeley concentrated on multiple ion species and revealed strong differences in effectiveness in \
                terminating cancer cells for different ions and along the particle track. This can be expressed in terms of the \
                relative biological effectiveness (RBE). The search for the “ideal particle” was started and early on, exotic particles \
                like pions and antiprotons entered the field. Enhancement in physical dose deposition near the end of range for \
                antiprotons compared to protons was shown experimentally but no data for the relative biological effectiveness were \
                available. In 2004 the AD-4/ACE collaboration set out to fill this gap. In a pilot experiment using a 50 MeV antiproton \
                beam we measured the ratio of cell termination between the Bragg peak and the entrance region (plateau), which can be \
                expressed by the biological effective dose ratio (BEDR), showing an increase of cell killing capability of antiprotons \
                compared to protons at identical energy by a factor of 4. This promising result led to a continuation of the AD-4/ACE \
                campaign using higher energy antiprotons and adding absolute dosimetry capabilities, allowing the extraction of the RBE \
                of antiprotons at any depth along the antiproton beam."
            }
        ]
    }, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.6497962474822998,
        'decision': 'Non-CORE',
        'scores': {
            'CORE': 0.33398324251174927,
            'Non-CORE': 0.6497962474822998,
            'Rejected': 0.016220496967434883,
        },
        'relevance_score': 0.6497962474822998,
    }


@patch('inspirehep.modules.workflows.tasks.classifier.get_classifier_url')
def test_guess_coreness_when_rejected(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = 'https://inspire-classifier.web.cern.ch/api/classifier'

    obj = MockObj({
        "titles": [
            {
                "title": "The Losses from Integration in Matching Markets can be Large"
            }
        ],
        "abstracts": [
            {
                "value": "Although the integration of two-sided matching markets using stable mechanisms generates expected gains from \
                integration, I show that there are worst-case scenarios in which these are negative. The losses from integration can be \
                large enough that the average rank of an agent's spouse decreases by 37.5 of the length of their preference list in any \
                stable matching mechanism."
            }
        ]
    }, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data['relevance_prediction'] == {
        'max_score': 0.8697909116744995,
        'decision': 'Rejected',
        'scores': {
            'CORE': 0.032547879964113235,
            'Non-CORE': 0.09766120463609695,
            'Rejected': 0.8697909116744995,
        },
        'relevance_score': -0.8697909116744995,
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
