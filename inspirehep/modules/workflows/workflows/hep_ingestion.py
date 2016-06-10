# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.dojson.hep import hep2marc
from inspirehep.dojson.utils import legacy_export_as_marc

from inspirehep.modules.refextract.tasks import extract_journal_info

from inspirehep.modules.workflows.tasks.actions import (
    add_core,
    halt_record,
    is_record_relevant,
    shall_push_remotely,
    shall_upload_record,
    reject_record,
    is_experimental_paper,
)

from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
)
from inspirehep.modules.workflows.tasks.beard import guess_coreness
from inspirehep.modules.workflows.tasks.magpie import (
    guess_keywords,
    guess_categories,
    guess_experiments,
)
from inspirehep.modules.workflows.tasks.matching import(
    delete_self_and_stop_processing,
    stop_processing,
    exists_in_holding_pen,
    record_exists,
    update_old_object,
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema
from inspirehep.modules.workflows.tasks.submission import (
    send_robotupload,
)
from inspirehep.utils.record import get_value


class ClassProperty(property):

    """Special class to allow a classmethod to be accessed as property."""

    def __get__(self, cls, owner):
        """Call getter and return."""
        return self.fget.__get__(None, owner)()


class HEPIngestion(object):
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

        class mysource(HEPIngestion):
            initial_processing = [before, processing]  # inject before halt
            halt_check = staticmethod(my_halt_check)  # need to be staticmethod
    """
    name = "HEP"
    data_type = "hep"

    initial_processing = [set_schema]
    match_processing = [
        IF(exists_in_holding_pen, [
            delete_self_and_stop_processing,
        ]),
        IF(record_exists, [
            stop_processing,
        ]),
    ]
    before_halt_check = [
        extract_journal_info,
        classify_paper(
            taxonomy="HEPont.rdf",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords,
        guess_categories,
        IF(is_experimental_paper, [
            guess_experiments,
        ]),
        guess_keywords,
        # Predict action for a generic HEP paper based only on title
        # and abstract.
        guess_coreness,  # ("arxiv_skip_astro_title_abstract.pickle"),
    ]
    halt_check = staticmethod(is_record_relevant)
    on_halt = [
        halt_record(action="hep_approval"),
    ]
    on_no_halt = [
        reject_record("Record automatically rejected")
    ]
    before_upload_check = [
        add_core,
    ]
    upload_check = staticmethod(shall_upload_record)
    on_upload = [
        IF_ELSE(shall_push_remotely, [
            send_robotupload(marcxml_processor=hep2marc),
        ], [
            store_record,
        ]),
    ]
    on_no_upload = []
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
                IF_ELSE(cls.halt_check, cls.on_halt, cls.on_no_halt)
            ] + cls.before_upload_check + [
                IF_ELSE(cls.upload_check, cls.on_upload, cls.on_no_upload)
            ] + cls.final_processing
        )

    workflow = ClassProperty(get_workflow)

    @classmethod
    def get_title(cls, obj, **kwargs):
        """Return the value to put in the title column of Holding Pen."""
        if isinstance(obj.data, dict):
            titles = filter(None, get_value(obj.data, "titles.title", []))
            if titles:
                # Show first title that evaluates to True
                return titles[0]
        return "No title available"

    @classmethod
    def get_additional(cls, obj, **kwargs):
        """Return the value to put in the additional column of HoldingPen."""
        if "classifier_results" in obj.extra_data:
            keywords = obj.extra_data.get('classifier_results').get("complete_output")
        else:
            keywords = []
        prediction_results = obj.extra_data.get("relevance_prediction", {})
        return render_template(
            'inspire_workflows/styles/harvesting_record_additional.html',
            object=obj,
            keywords=keywords,
            score=prediction_results.get("max_score"),
            decision=prediction_results.get("decision")
        )

    @classmethod
    def formatter(cls, obj, **kwargs):
        """Nicely format the record."""
        if not obj.data:
            return ""
        if kwargs and kwargs.get('of') == 'xm':
            return legacy_export_as_marc(hep2marc.do(obj.data))
        return render_template(
            'inspirehep_theme/format/record/Holding_Pen_HTML_detailed.tpl',
            record=obj.data
        )

    @classmethod
    def get_sort_data(cls, obj, **kwargs):
        """Return a dictionary useful for sorting in Holding Pen."""
        prediction_results = obj.extra_data.get("relevance_prediction", {})
        if prediction_results:
            return {
                "max_score": prediction_results.get("max_score"),
                "decision": prediction_results.get("decision"),
                "relevance_score": prediction_results.get("relevance_score")
            }
        else:
            return {}

    @classmethod
    def get_record(cls, obj, **kwargs):
        """Return a dictionary-like object representing the current object.

        This object will be used for indexing and be the basis for display
        in Holding Pen.
        """
        if not isinstance(obj.data, dict):
            return {}
        return obj.data

    @staticmethod
    def get_description(obj):
        """Get the description column part."""
        if not isinstance(obj.data, dict):
            return "No description found."
        abstract = ""
        authors = []
        categories = []
        final_identifiers = []

        # Get identifiers
        dois = get_value(obj.data, "dois.value", [])
        if dois:
            final_identifiers.extend(dois)

        system_no = get_value(obj.data, "external_system_numbers.value", [])
        if system_no:
            final_identifiers.extend(system_no)

        # Get subject categories, adding main one first. Order matters here.
        record_categories = get_value(obj.data, "arxiv_eprints.categories", []) + \
            get_value(obj.data, "field_categories.term", [])
        for category_list in record_categories:
            if isinstance(category_list, list):
                categories.extend(category_list)
            else:
                categories.append(category_list)
        categories = list(OrderedDict.fromkeys(categories))  # Unique only
        abstract = get_value(obj.data, "abstracts.value", [""])[0]
        authors = obj.data.get("authors", [])
        return render_template('inspire_workflows/styles/harvesting_record.html',
                               object=obj,
                               authors=authors,
                               categories=categories,
                               abstract=abstract,
                               identifiers=final_identifiers)
