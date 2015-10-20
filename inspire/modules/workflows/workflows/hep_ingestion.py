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

from collections import OrderedDict

from flask import render_template

from inspire.dojson.hep import hep2marc

from inspire.modules.workflows.models import Payload, create_payload
from inspire.modules.workflows.tasks.actions import (
    add_core_check,
    halt_record,
    shall_halt_workflow,
    shall_push_remotely,
    shall_upload_record,
)

from inspire.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
)

from inspire.modules.workflows.tasks.matching import(
    delete_self_and_stop_processing,
    exists_in_holding_pen,
    exists_in_inspire_or_rejected,
    update_old_object,
)

from inspire.modules.workflows.tasks.submission import (
    finalize_record_sip,
    send_robotupload,
)
from inspire.modules.workflows.tasks.upload import store_record_sip

from inspire.utils.helpers import get_record_from_model

from invenio_deposit.models import DepositionType

from invenio_workflows.tasks.logic_tasks import (
    workflow_else,
    workflow_if,
)

import six


class ClassProperty(property):

    """Special class to allow a classmethod to be accessed as property."""

    def __get__(self, cls, owner):
        """Call getter and return."""
        return self.fget.__get__(None, owner)()


class hep_ingestion(DepositionType):

    """Generic HEP ingestion workflow for a single record.

    This workflow is built upon a set of steps that can be overridden.

    Mainly it is composed of the following steps:

        1. `initial_processing` (e.g. conversion to correct formats)
        2. `match_processing` (e.g. match record to existing records in
           Holding Pen or the database itself.)
        3. `before_halt_check` (e.g. list of tasks before checking
           if record should be halted)
        4. `halt_check` (static function to see if the record require
           human intervention in the Holding Pen. Return True/False)
               a. On `True`: `on_halt` processing (e.g. decide what happens
                  upon halt)
        5. `before_upload_check` (e.g. tasks to run before upload check)
        6. `upload_check` (static function to see if the record shall be
            uploaded. Return True/False
               a. On `True`: `on_upload` processing (e.g. decide what happens
                  upon upload)
               b. On `False`: `on_rejection` processing (e.g. decide what happens
                  upon rejection)
       7. `final_processing` (e.g. conversion to correct formats)

    Integrate this workflow in your other workflows:

    .. code:: python

        class mysource(hep_ingestion):
            initial_processing = [before, processing]  # inject before halt
            halt_check = staticmethod(my_halt_check)  # need to be staticmethod
    """

    model = Payload
    object_type = "HEP"

    initial_processing = [create_payload]
    match_processing = [
        workflow_if(exists_in_inspire_or_rejected()),
        [
            delete_self_and_stop_processing,
        ],
        workflow_if(exists_in_holding_pen),
        [
            update_old_object,
            delete_self_and_stop_processing,
        ]
    ]
    before_halt_check = [
        classify_paper(
            taxonomy="HEPont",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords(filter_kb="antihep"),
    ]
    halt_check = staticmethod(shall_halt_workflow)
    on_halt = [
        halt_record,
    ]
    before_upload_check = [
        add_core_check,
    ]
    upload_check = staticmethod(shall_upload_record)
    on_upload = [
        finalize_record_sip(processor=hep2marc),
        workflow_if(shall_push_remotely),
        [
            send_robotupload(),
        ],
        workflow_else,
        [
            store_record_sip,
        ]
    ]
    on_rejection = []
    final_processing = []

    @classmethod
    def get_workflow(cls):
        """Build the main ingestion workflow.

        This builder enforces a certain structure to the ingestion workflow.
        """
        return (
            cls.initial_processing +
            cls.match_processing +
            cls.before_halt_check + [
                workflow_if(cls.halt_check),
                cls.on_halt,
            ] + cls.before_upload_check + [
                workflow_if(cls.upload_check),
                cls.on_upload,
                workflow_else,
                cls.on_rejection,
            ] + cls.final_processing
        )

    workflow = ClassProperty(get_workflow)

    @staticmethod
    def get_title(bwo):
        """Return title."""
        if isinstance(bwo.data, dict):
            model = hep_ingestion.model(bwo)
            record = get_record_from_model(model)
            titles = record.get("titles.title")
            if titles:
                return titles[0]
        return "No title available"

    @staticmethod
    def get_description(bwo):
        """Get the description column part."""
        if not isinstance(bwo.data, dict):
            return "No description found."
        model = hep_ingestion.model(bwo)
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
        """Return rendered view for additional information."""
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
            model = hep_ingestion.model(bwo)
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
