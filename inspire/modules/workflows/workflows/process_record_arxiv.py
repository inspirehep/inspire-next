# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Workflow for processing single arXiv records harvested."""

import six

from collections import OrderedDict
from flask import render_template

from invenio_oaiharvester.tasks.records import convert_record_to_json

from invenio_deposit.models import DepositionType

from inspire.modules.workflows.tasks.matching import(
    exists_in_inspire_or_rejected,
    exists_in_holding_pen,
    save_identifiers_to_kb,
    update_old_object,
    delete_self_and_stop_processing,
    arxiv_set_category_field
)

# from inspire.modules.refextract.tasks import extract_journal_info

from inspire.dojson.hep import hep2marc

from inspire.modules.workflows.tasks.classifier import (
    filter_core_keywords,
    classify_paper,
)

# from inspire.modules.oaiharvester.tasks.arxiv import (
#     arxiv_plot_extract,
#     arxiv_fulltext_download,
#     arxiv_author_list,
# )
from invenio_workflows.tasks.workflows_tasks import log_info

from inspire.modules.workflows.tasks.actions import (
    was_approved,
    add_core,
)

from invenio_workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)

from inspire.modules.converter.tasks import convert_record
from invenio_workflows.definitions import RecordWorkflow

from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload,
    finalize_record_sip,
)
from inspire.modules.predicter.tasks import (
    guess_coreness
)
from inspire.modules.workflows.models import Payload, create_payload
from inspire.utils.helpers import get_record_from_model


class process_record_arxiv(RecordWorkflow, DepositionType):

    """Processing workflow for a single arXiv record.

    The records have been harvested via oaiharvester.
    """

    model = Payload

    object_type = "arXiv"
    workflow = [
        # First we perform conversion from OAI-PMH XML to MARCXML
        convert_record("oaiarXiv2inspire_nofilter.xsl"),
        # Then we convert from MARCXML to JSON object with doJSON
        convert_record_to_json,
        # Create payload object to align with Deposition object
        create_payload,
        workflow_if(exists_in_inspire_or_rejected()),
        [
            delete_self_and_stop_processing,
            # update_existing_record_oaiharvest(),
        ],
        workflow_else,
        [
            workflow_if(exists_in_holding_pen("HP_IDENTIFIERS")),
            [
                update_old_object("HP_IDENTIFIERS"),
                delete_self_and_stop_processing,
            ],
            workflow_else,
            [
                # FIXME: Remove this when elasticsearch filtering is ready
                arxiv_set_category_field,
                save_identifiers_to_kb("HP_IDENTIFIERS"),
                # arxiv_plot_extract,
                # arxiv_fulltext_download(),
                # arxiv_refextract,
                # arxiv_author_list("authorlist2marcxml.xsl"),
                # extract_journal_info,
                classify_paper(
                    taxonomy="HEPont",
                    only_core_tags=False,
                    spires=True,
                    with_author_keywords=True,
                ),
                filter_core_keywords(filter_kb="antihep"),
                guess_coreness("new_astro_model.pickle"),
                halt_record_with_action(action="arxiv_approval",
                                        message="Accept article?"),
                workflow_if(was_approved),
                [
                    add_core,
                    finalize_record_sip(processor=hep2marc),
                    send_robotupload(),
                ],
                workflow_else,
                [
                    log_info("Record rejected"),
                ],
            ],
        ],
    ]

    @staticmethod
    def get_title(bwo):
        if not isinstance(bwo.data, dict):
            return "No title found."
        model = process_record_arxiv.model(bwo)
        record = get_record_from_model(model)
        return "; ".join(record.get("titles.title", ["No title found"]))

    @staticmethod
    def get_description(bwo):
        """Get the description column part."""
        if not isinstance(bwo.data, dict):
            return "No description found."
        model = process_record_arxiv.model(bwo)
        record = get_record_from_model(model)
        abstract = ""
        authors = []
        categories = []
        final_identifiers = []
        if hasattr(record, "get"):
            # Get identifiers
            dois = record.get("dois.value", [])
            if dois:
                final_identifiers.extend(dois)

            system_no = record.get("external_system_numbers.value", [])
            if system_no:
                final_identifiers.extend(system_no)

            # Get subject categories, adding main one first. Order matters here.
            record_categories = record.get("arxiv_eprints.categories", []) + \
                record.get("subject_terms.term", [])
            for category_list in record_categories:
                if isinstance(category_list, list):
                    categories.extend(category_list)
                else:
                    categories.append(category_list)
            categories = list(OrderedDict.fromkeys(categories))  # Unique only
            abstract = record.get("abstracts.value", [""])[0]
            authors = record.get("authors", [])
        return render_template('workflows/styles/harvesting_record.html',
                               object=bwo,
                               authors=authors,
                               categories=categories,
                               abstract=abstract,
                               identifiers=final_identifiers)

    @staticmethod
    def get_additional(bwo):
        """Returns rendered view for additional information."""
        from inspire.modules.predicter.utils import get_classification_from_task_results

        keywords = get_classification_from_task_results(bwo)
        results = bwo.get_tasks_results()
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
        return render_template(
            'workflows/styles/harvesting_record_additional.html',
            object=bwo,
            keywords=keywords,
            score=prediction_results.get("max_score"),
            decision=prediction_results.get("decision")
        )

    @staticmethod
    def get_sort_data(bwo, **kwargs):
        """Return a dictionary of key values useful for sorting in Holding Pen."""
        results = bwo.get_tasks_results()
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
            max_score = prediction_results.get("max_score")
            decision = prediction_results.get("decision")
            relevance_score = max_score
            if decision == "CORE":
                relevance_score += 10
            elif decision == "Rejected":
                relevance_score = (max_score * -1) - 10
            return {
                "max_score": prediction_results.get("max_score"),
                "decision": prediction_results.get("decision"),
                "relevance_score": relevance_score
            }
        else:
            return {}

    @staticmethod
    def formatter(bwo, **kwargs):
        """Nicely format the record."""
        try:
            model = process_record_arxiv.model(bwo)
            record = get_record_from_model(model)
        except TypeError as err:
            return "Error: {0}".format(err)
        return render_template(
            'format/record/Holding_Pen_HTML_detailed.tpl',
            record=record
        )

    @classmethod
    def get_record(cls, obj, **kwargs):
        """Return a dictionary-like object representing the current object.

        This object will be used for indexing and be the basis for display
        in Holding Pen.
        """
        if isinstance(obj.data, six.text_type):
            return {}
        model = cls.model(obj)
        return get_record_from_model(model).dumps()  # Turn into pure dict
