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
import requests
from flask import current_app
from mock import patch
from mocks import MockEng, MockObj
from six import binary_type

from inspirehep.modules.workflows.tasks.classifier import (classify_paper,
                                                           get_classifier_url,
                                                           guess_coreness,
                                                           prepare_payload)

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
    <Concept rdf:about="http://cern.ch/thesauri/HEPontology.rdf#Corekeyword">
        <prefLabel xml:lang="en">Core Keyword</prefLabel>
        <note xml:lang="en">core</note>
    </Concept>

</rdf:RDF>
"""


def test_get_classifier_api_url_from_configuration():
    config = {"CLASSIFIER_API_URL": "https://inspire-classifier.web.cern.ch/api"}

    with patch.dict(current_app.config, config):
        expected = "https://inspire-classifier.web.cern.ch/api/predict/coreness"
        result = get_classifier_url()

        assert expected == result


def test_get_classifier_api_url_returns_none_when_not_in_configuration():
    config = {"CLASSIFIER_API_URL": ""}

    with patch.dict(current_app.config, config):
        assert get_classifier_url() is None


def test_prepare_payload():
    record = {
        "titles": [
            {
                "title": "Effects of top compositeness",
            },
        ],
        "abstracts": [
            {
                "value": "We investigate the effects of (...)",
            },
        ],
    }

    expected = {
        "title": "Effects of top compositeness",
        "abstract": "We investigate the effects of (...)",
    }
    result = prepare_payload(record)

    assert expected == result


@patch("inspirehep.modules.workflows.tasks.classifier.get_classifier_url")
def test_guess_coreness_returns_early_without_a_classifier_url(
    mocked_get_classifier_url,
):
    mocked_get_classifier_url.return_value = ""

    obj = MockObj({}, {})
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert "relevance_prediction" not in obj.extra_data


@patch("inspirehep.modules.workflows.tasks.classifier.get_classifier_url")
def test_guess_coreness_fails_when_request_fails(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = (
        "http://10.254.0.186:5000/api/predict/does-not-exist"
    )

    obj = MockObj({}, {})
    eng = MockEng()

    with pytest.raises(requests.RequestException):
        guess_coreness(obj, eng)


@patch("inspirehep.modules.workflows.tasks.classifier.get_classifier_url")
def test_guess_coreness_when_core(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = (
        "http://10.254.0.186:5000/api/predict/coreness"
    )

    obj = MockObj(
        {
            "titles": [{"title": "Instanton Corrections for m and Ω"}],
            "abstracts": [
                {
                    "value": "In this paper, we study instanton corrections in the N=2⋆ gauge theory by using its description in string \
                theory as a freely-acting orbifold. The latter is used to compute, using the worldsheet, the deformation of the Yang–Mills \
                action. In addition, we calculate the deformed instanton partition function, thus extending the results to the non-perturbative \
                sector of the gauge theory. As we point out, the structure of the deformation is extremely similar to the Ω-deformation, therefore \
                confirming the universality of the construction. Finally, we comment on the realisation of the mass deformation using physical \
                vertex operators by exploiting the equivalence between Scherk–Schwarz deformations and freely-acting orbifolds."
                }
            ],
        },
        {},
    )
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data["relevance_prediction"] == {
        "decision": "CORE",
        "max_score": 0.9497610926628113,
        "relevance_score": 1.9497610926628113,
        "scores": {
            "CORE": 0.9497610926628113,
            "Rejected": 0.0014781546778976917,
            "Non-CORE": 0.048760786652565,
        },
    }


@patch("inspirehep.modules.workflows.tasks.classifier.get_classifier_url")
def test_guess_coreness_when_non_core(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = (
        "http://10.254.0.186:5000/api/predict/coreness"
    )

    obj = MockObj(
        {
            "titles": [
                {
                    "title": "Vertex F-algebra structures on the complex oriented homology of H-spaces"
                }
            ],
            "abstracts": [
                {
                    "value": 'We give a topological construction of graded vertex F-algebras by generalizing Joyce\'s vertex algebra construction to complex-oriented homology. Given an H-space X with a <math altimg="si1.svg"><mi>B</mi><mi mathvariant="normal">U</mi><mo stretchy="false">(</mo><mn>1</mn><mo stretchy="false">)</mo></math>-action, a choice of K-theory class, and a complex oriented homology theory E, we build a graded vertex F-algebra structure on <math altimg="si197.svg"><msub><mrow><mi>E</mi></mrow><mrow><mo>⁎</mo></mrow></msub><mo stretchy="false">(</mo><mi>X</mi><mo stretchy="false">)</mo></math> where F is the formal group law associated with E.'
                }
            ],
        },
        {},
    )
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data["relevance_prediction"] == {
        "decision": "Non-CORE",
        "max_score": 0.9195370078086853,
        "relevance_score": 0.9195370078086853,
        "scores": {
            "CORE": 0.06607123464345932,
            "Rejected": 0.014391724020242691,
            "Non-CORE": 0.9195370078086853,
        },
    }


@patch("inspirehep.modules.workflows.tasks.classifier.get_classifier_url")
def test_guess_coreness_when_rejected(mocked_get_classifier_url):
    mocked_get_classifier_url.return_value = (
        "http://10.254.0.186:5000/api/predict/coreness"
    )

    obj = MockObj(
        {
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
            ],
        },
        {},
    )
    eng = MockEng()

    assert guess_coreness(obj, eng) is None
    assert obj.extra_data["relevance_prediction"] == {
        "decision": "Rejected",
        "max_score": 0.8802158832550049,
        "relevance_score": -0.8802158832550049,
        "scores": {
            "CORE": 0.04252934828400612,
            "Rejected": 0.8802158832550049,
            "Non-CORE": 0.07725479453802109,
        },
    }


@pytest.fixture()
def higgs_ontology(tmpdir):
    ontology = tmpdir.join("HEPont.rdf")
    ontology.write(HIGGS_ONTOLOGY)
    yield str(ontology)


@patch("inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow")
def test_classify_paper_with_fulltext(get_document_in_workflow, tmpdir, higgs_ontology):
    obj = MockObj({}, {})
    eng = MockEng()
    fulltext = tmpdir.join("fulltext.txt")
    fulltext.write("Higgs boson")
    get_document_in_workflow.return_value.__enter__.return_value = binary_type(fulltext)
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected_fulltext_keywords = [{"number": 1, "keyword": "Higgs particle"}]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert (
        obj.extra_data["classifier_results"]["complete_output"]["core_keywords"]
        == expected_fulltext_keywords
    )
    assert obj.extra_data["classifier_results"]["fulltext_used"] is True
    assert "extracted_keywords" not in obj.extra_data


@patch("inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow")
def test_classify_paper_with_no_fulltext(get_document_in_workflow, higgs_ontology):
    data = {
        "titles": [
            {
                "title": "Some title",
            },
        ],
        "abstracts": [
            {"value": "Very interesting paper about the Higgs boson."},
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_document_in_workflow.return_value.__enter__.return_value = None
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected_kewords = [{"number": 1, "keyword": "Higgs particle"}]

    expected_extracted_keywords = ["Higgs particle"]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert (
        obj.extra_data["classifier_results"]["complete_output"]["core_keywords"]
        == expected_kewords
    )
    assert obj.extra_data["extracted_keywords"] == expected_extracted_keywords
    assert obj.extra_data["classifier_results"]["fulltext_used"] is False


@patch("inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow")
def test_classify_paper_uses_keywords(get_document_in_workflow, higgs_ontology):
    data = {
        "titles": [
            {
                "title": "Some title",
            },
        ],
        "keywords": [
            {
                "value": "Higgs boson",
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_document_in_workflow.return_value.__enter__.return_value = None
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected = [{"number": 1, "keyword": "Higgs particle"}]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert (
        obj.extra_data["classifier_results"]["complete_output"]["core_keywords"]
        == expected
    )
    assert obj.extra_data["classifier_results"]["fulltext_used"] is False


@patch("inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow")
def test_classify_paper_does_not_raise_on_unprintable_keywords(
    get_document_in_workflow, higgs_ontology
):
    paper_with_unprintable_keywords = pkg_resources.resource_filename(
        __name__, os.path.join("fixtures", "1802.08709.pdf")
    )

    get_document_in_workflow.return_value.__enter__.return_value = (
        paper_with_unprintable_keywords
    )
    get_document_in_workflow.return_value.__exit__.return_value = None

    obj = MockObj({}, {})
    eng = MockEng()

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(
        obj, eng
    )  # Does not raise.


@patch("inspirehep.modules.workflows.tasks.classifier.get_document_in_workflow")
def test_classify_paper_with_fulltext_and_data(
    get_document_in_workflow, tmpdir, higgs_ontology
):
    data = {
        "titles": [
            {
                "title": "Some title",
            },
        ],
        "abstracts": [
            {"value": "Very interesting paper about the Higgs boson."},
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    fulltext = tmpdir.join("fulltext.txt")
    fulltext.write("Core Keyword")
    get_document_in_workflow.return_value.__enter__.return_value = binary_type(fulltext)
    get_document_in_workflow.return_value.__exit__.return_value = None

    expected_fulltext_keywords = [{"number": 1, "keyword": "Core Keyword"}]

    expected_extracted_keywords = ["Higgs particle"]

    classify_paper(
        taxonomy=higgs_ontology,
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
        no_cache=True,
    )(obj, eng)

    assert (
        obj.extra_data["classifier_results"]["complete_output"]["core_keywords"]
        == expected_fulltext_keywords
    )
    assert obj.extra_data["classifier_results"]["fulltext_used"] is True
    assert obj.extra_data["extracted_keywords"] == expected_extracted_keywords
