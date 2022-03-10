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

from copy import deepcopy

import pytest
from factories.db.invenio_records import TestRecordMetadata
from inspire_utils.record import get_value
from invenio_search import current_search
from invenio_workflows import (ObjectStatus, WorkflowEngine, start,
                               workflow_object_class)
from mock import patch
from mocks import fake_classifier_api_request, fake_magpie_api_request
from workflow_utils import build_workflow

from inspirehep.modules.workflows.tasks.matching import (
    fuzzy_match, has_same_source, match_non_completed_wf_in_holdingpen,
    match_previously_rejected_wf_in_holdingpen, stop_matched_holdingpen_wfs)


@pytest.fixture
def simple_record(app):
    yield {
        "workflow_data": {
            "$schema": "http://localhost:5000/schemas/records/hep.json",
            "_collections": ["Literature"],
            "document_type": ["article"],
            "titles": [{"title": "Superconductivity"}],
            "acquisition_source": {"source": "arXiv"},
            "dois": [{"value": "10.3847/2041-8213/aa9110"}],
        },
        "extra_data": {
            "source_data": {
                "data": {
                    "$schema": "http://localhost:5000/schemas/records/hep.json",
                    "_collections": ["Literature"],
                    "document_type": ["article"],
                    "titles": [{"title": "Superconductivity"}],
                    "acquisition_source": {"source": "arXiv"},
                    "dois": [{"value": "10.3847/2041-8213/aa9110"}],
                },
                "extra_data": {},
            },
        },
    }

    list(current_search.delete(index_list="holdingpen-hep"))
    list(current_search.create(ignore=[400], ignore_existing=True))


def test_pending_holdingpen_matches_wf_if_not_completed(app, simple_record):

    workflow = build_workflow(status=ObjectStatus.HALTED, **simple_record)
    obj_id = workflow.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)

    assert match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.COMPLETED
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    # doesn't match anymore because obj is COMPLETED
    assert not match_non_completed_wf_in_holdingpen(obj2, None)


def test_match_previously_rejected_wf_in_holdingpen(app, simple_record):
    obj = build_workflow(status=ObjectStatus.COMPLETED, **simple_record)
    obj_id = obj.id

    obj.extra_data["approved"] = False  # reject it
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    assert match_previously_rejected_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["previously_rejected_matches"] == [obj_id]

    obj = workflow_object_class.get(obj_id)
    obj.status = ObjectStatus.HALTED
    obj.save()
    current_search.flush_and_refresh("holdingpen-hep")

    # doesn't match anymore because obj is COMPLETED
    assert not match_previously_rejected_wf_in_holdingpen(obj2, None)


def test_has_same_source(app, simple_record):
    obj = build_workflow(status=ObjectStatus.HALTED, data_type="hep", **simple_record)
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    match_non_completed_wf_in_holdingpen(obj2, None)

    same_source_func = has_same_source("holdingpen_matches")

    assert same_source_func(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    # change source and match the wf in the holdingpen
    different_source_rec = deepcopy(simple_record)
    different_source_rec["workflow_data"]["acquisition_source"] = {
        "source": "different"
    }
    obj3 = build_workflow(**different_source_rec)

    assert match_non_completed_wf_in_holdingpen(obj3, None)
    assert not same_source_func(obj3, None)


@patch(
    "inspirehep.modules.workflows.tasks.classifier.json_api_request",
    side_effect=fake_classifier_api_request,
)
@patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_stop_matched_holdingpen_wfs(
    mocked_api_request_magpie, mocked_classifer_api, app, simple_record
):
    # need to run a wf in order to assign to it the wf definition and a uuid
    # for it

    obj = build_workflow(data_type="hep", **simple_record)
    workflow_uuid = start("article", object_id=obj.id)
    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]
    obj.status = ObjectStatus.HALTED
    obj.save()
    obj_id = obj.id
    current_search.flush_and_refresh("holdingpen-hep")

    obj2 = build_workflow(**simple_record)
    obj2_id = obj2.id

    match_non_completed_wf_in_holdingpen(obj2, None)
    assert obj2.extra_data["holdingpen_matches"] == [obj_id]

    stop_matched_holdingpen_wfs(obj2, None)

    stopped_wf = workflow_object_class.get(obj_id)
    assert stopped_wf.status == ObjectStatus.COMPLETED
    assert stopped_wf.extra_data["stopped-by-wf"] == obj2_id


def test_fuzzy_match_without_math_ml_and_latex(workflow_app):
    correct_match = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            }
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": "This paper presents the projections on the anomalous neutral triple gauge couplings via production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. The study is carried out in the mode where one Z boson decays into a pair of same-flavor, opposite-sign leptons (electrons or muons) and the other one decays to the two neutrinos. The new bounds on the charge-parity (CP)-conserving couplings and CP-violating couplings and achieved at 95% Confidence Level (C.L.) using the transverse momentum of the dilepton system, respectively.",
                "source": "Elsevier B.V.",
            }
        ],
    }

    record_match_1 = TestRecordMetadata.create_from_kwargs(
        json=correct_match, index_name="records-hep"
    )
    record_1 = record_match_1.record_metadata

    incorrect_match = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            },
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": 'Wrong content (<math altimg="si1.svg"><mi>a</mi><mi>N</mi><mi>T</mi><mi>G</mi><mi>C</mi></math>) via <math altimg="si2.svg"><mi>p</mi><mi>p</mi><mo stretchy="false">→</mo><mi>Z</mi><mi>Z</mi></math> production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. osite-sign leptons (electrons or muons) and the other one very very incorrect decayn the charge-parity (CP)-conserving couplings <math altimg="si3.svg"><msub><mrow><mi>C</mi></mrow><mrow><mover accent="true"><mrow><mi>B</mi></mrow><mrow><mo>˜</mo></mrow></mover><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and CP-violating couplings <math altimg="si4.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>W</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math>, <math altimg="si5.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and <math altimg="si6.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>B</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> achievedfakey fakesystem (<math altimg="si7.svg"><msubsup><mrow><mi>p</mi></mrow><mrow><mi>T</mi></mrow><mrow><mi>ℓ</mi><mi>ℓ</mi></mrow></msubsup></math>) are <math altimg="si8.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.042</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.042</mn><mo stretchy="false">]</mo></math>, <math altimg="si9.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.049</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.049</mn><mo stretchy="false">]</mo></math>, <math altimg="si10.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.048</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.048</mn><mo stretchy="false">]</mo></math>, and <math altimg="si11.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.047</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.047</mn><mo stretchy="false">]</mo></math> in units of TeV<sup loc="post">−4</sup>, respectively.',
                "source": "Elsevier B.V.",
            }
        ],
    }

    record_match_2 = TestRecordMetadata.create_from_kwargs(
        json=incorrect_match, index_name="records-hep"
    )
    record_match_2.record_metadata

    record = {
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            },
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": 'This paper presents the projections on the anomalous neutral triple gauge couplings (<math altimg="si1.svg"><mi>a</mi><mi>N</mi><mi>T</mi><mi>G</mi><mi>C</mi></math>) via <math altimg="si2.svg"><mi>p</mi><mi>p</mi><mo stretchy="false">→</mo><mi>Z</mi><mi>Z</mi></math> production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. The study is carried out in the mode where one Z boson decays into a pair of same-flavor, opposite-sign leptons (electrons or muons) and the other one decays to the two neutrinos. The new bounds on the charge-parity (CP)-conserving couplings <math altimg="si3.svg"><msub><mrow><mi>C</mi></mrow><mrow><mover accent="true"><mrow><mi>B</mi></mrow><mrow><mo>˜</mo></mrow></mover><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and CP-violating couplings <math altimg="si4.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>W</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math>, <math altimg="si5.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and <math altimg="si6.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>B</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> achieved at 95% Confidence Level (C.L.) using the transverse momentum of the dilepton system (<math altimg="si7.svg"><msubsup><mrow><mi>p</mi></mrow><mrow><mi>T</mi></mrow><mrow><mi>ℓ</mi><mi>ℓ</mi></mrow></msubsup></math>) are <math altimg="si8.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.042</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.042</mn><mo stretchy="false">]</mo></math>, <math altimg="si9.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.049</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.049</mn><mo stretchy="false">]</mo></math>, <math altimg="si10.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.048</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.048</mn><mo stretchy="false">]</mo></math>, and <math altimg="si11.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.047</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.047</mn><mo stretchy="false">]</mo></math> in units of TeV<sup loc="post">−4</sup>, respectively.',
                "source": "Elsevier B.V.",
            }
        ],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    eng = object()

    original_abstract = obj.data["abstracts"][0]["value"]
    assert fuzzy_match(obj, eng)
    assert "matches" in obj.extra_data

    matches = get_value(obj.extra_data, "matches.fuzzy")

    # assert the result with correct abstract comes as a first result
    assert matches[0]["control_number"] == record_1.json["control_number"]
    assert obj.data["abstracts"][0]["value"] == original_abstract


def test_matching(workflow_app):

    correct_match = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            }
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": "This paper presents the projections on the anomalous neutral triple gauge couplings via production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. The study is carried out in the mode where one Z boson decays into a pair of same-flavor, opposite-sign leptons (electrons or muons) and the other one decays to the two neutrinos. The new bounds on the charge-parity (CP)-conserving couplings and CP-violating couplings and achieved at 95% Confidence Level (C.L.) using the transverse momentum of the dilepton system, respectively.",
                "source": "Elsevier B.V.",
            }
        ],
        "arxiv_eprints": [{"categories": ["hep-ph", "astro-ph.CO"], "value": "1811.12764"}],
    }

    record_match_1 = TestRecordMetadata.create_from_kwargs(
        json=correct_match, index_name="records-hep"
    )
    record_1 = record_match_1.record_metadata

    incorrect_match = {
        "$schema": "https://inspirehep.net/schemas/records/hep.json",
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            },
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": 'This paper presents the projections on the anomalous neutral triple gauge couplings (<math altimg="si1.svg"><mi>a</mi><mi>N</mi><mi>T</mi><mi>G</mi><mi>C</mi></math>) via <math altimg="si2.svg"><mi>p</mi><mi>p</mi><mo stretchy="false">→</mo><mi>Z</mi><mi>Z</mi></math> production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. The study is carried out in the mode where one Z boson decays into a pair of same-flavor, opposite-sign leptons (electrons or muons) and the other one decays to the two neutrinos. The new bounds on the charge-parity (CP)-conserving couplings <math altimg="si3.svg"><msub><mrow><mi>C</mi></mrow><mrow><mover accent="true"><mrow><mi>B</mi></mrow><mrow><mo>˜</mo></mrow></mover><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and CP-violating couplings <math altimg="si4.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>W</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math>, <math altimg="si5.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and <math altimg="si6.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>B</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> achieved at 95% Confidence Level (C.L.) using the transverse momentum of the dilepton system (<math altimg="si7.svg"><msubsup><mrow><mi>p</mi></mrow><mrow><mi>T</mi></mrow><mrow><mi>ℓ</mi><mi>ℓ</mi></mrow></msubsup></math>) are <math altimg="si8.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.042</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.042</mn><mo stretchy="false">]</mo></math>, <math altimg="si9.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.049</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.049</mn><mo stretchy="false">]</mo></math>, <math altimg="si10.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.048</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.048</mn><mo stretchy="false">]</mo></math>, and <math altimg="si11.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.047</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.047</mn><mo stretchy="false">]</mo></math> in units of TeV<sup loc="post">−4</sup>, respectively.',
                "source": "Elsevier B.V.",
            }
        ],
        "arxiv_eprints": [{"categories": ["hep-lat"], "value": "1205.1659"}],
    }

    record_match_2 = TestRecordMetadata.create_from_kwargs(
        json=incorrect_match, index_name="records-hep"
    )
    record_match_2.record_metadata

    record = {
        "_collections": ["Literature"],
        "titles": [
            {
                "title": "Search for the limits on anomalous neutral triple gauge couplings via ZZ production in the $\\ell\\ell\\nu\\nu$ channel at FCC-hh",
            },
        ],
        "authors": [
            {"full_name": "Yilmaz, Ali"},
        ],
        "document_type": ["article"],
        "abstracts": [
            {
                "value": 'This paper presents the projections on the anomalous neutral triple gauge couplings (<math altimg="si1.svg"><mi>a</mi><mi>N</mi><mi>T</mi><mi>G</mi><mi>C</mi></math>) via <math altimg="si2.svg"><mi>p</mi><mi>p</mi><mo stretchy="false">→</mo><mi>Z</mi><mi>Z</mi></math> production in the 2ℓ2ν final state at a 100 TeV proton-proton collider, FCC-hh. The realistic FCC-hh detector environments and its effects taken into account in the analysis. The study is carried out in the mode where one Z boson decays into a pair of same-flavor, opposite-sign leptons (electrons or muons) and the other one decays to the two neutrinos. The new bounds on the charge-parity (CP)-conserving couplings <math altimg="si3.svg"><msub><mrow><mi>C</mi></mrow><mrow><mover accent="true"><mrow><mi>B</mi></mrow><mrow><mo>˜</mo></mrow></mover><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and CP-violating couplings <math altimg="si4.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>W</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math>, <math altimg="si5.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>W</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> and <math altimg="si6.svg"><msub><mrow><mi>C</mi></mrow><mrow><mi>B</mi><mi>B</mi></mrow></msub><mo stretchy="false">/</mo><msup><mrow><mi mathvariant="normal">Λ</mi></mrow><mrow><mn>4</mn></mrow></msup></math> achieved at 95% Confidence Level (C.L.) using the transverse momentum of the dilepton system (<math altimg="si7.svg"><msubsup><mrow><mi>p</mi></mrow><mrow><mi>T</mi></mrow><mrow><mi>ℓ</mi><mi>ℓ</mi></mrow></msubsup></math>) are <math altimg="si8.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.042</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.042</mn><mo stretchy="false">]</mo></math>, <math altimg="si9.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.049</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.049</mn><mo stretchy="false">]</mo></math>, <math altimg="si10.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.048</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.048</mn><mo stretchy="false">]</mo></math>, and <math altimg="si11.svg"><mo stretchy="false">[</mo><mo linebreak="badbreak" linebreakstyle="after">−</mo><mspace width="0.2em"/><mn>0.047</mn><mo>,</mo><mspace width="0.2em"/><mspace width="0.2em"/><mo linebreak="badbreak" linebreakstyle="after">+</mo><mspace width="0.2em"/><mn>0.047</mn><mo stretchy="false">]</mo></math> in units of TeV<sup loc="post">−4</sup>, respectively.',
                "source": "Elsevier B.V.",
            }
        ],
        "arxiv_eprints": [{"categories": ["hep-lat"], "value": "1205.1659"}],
    }

    obj = workflow_object_class.create(data=record, id_user=1, data_type="hep")
    eng = object()

    original_abstract = obj.data["abstracts"][0]["value"]
    assert fuzzy_match(obj, eng)
    assert "matches" in obj.extra_data
    matches = get_value(obj.extra_data, "matches.fuzzy")

    # assert the result with correct abstract and not with the incorrect one
    assert matches[0]["control_number"] == record_1.json["control_number"]
    assert obj.data["abstracts"][0]["value"] == original_abstract
    assert len(matches) == 1
