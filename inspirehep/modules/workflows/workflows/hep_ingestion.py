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

from inspirehep.dojson.hep import hep2marc

from inspirehep.modules.predicter.tasks import (
    guess_coreness,
)

from inspirehep.modules.refextract.tasks import extract_journal_info

from inspirehep.modules.workflows.models import (
    SIPWorkflowMixin,
    Payload,
    create_payload,
)
from inspirehep.modules.workflows.tasks.actions import (
    add_core_check,
    halt_record,
    is_record_relevant,
    shall_push_remotely,
    shall_upload_record,
    reject_record,
)

from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
)

from inspirehep.modules.workflows.tasks.matching import(
    delete_self_and_stop_processing,
    stop_processing,
    exists_in_holding_pen,
    record_exists,
    update_old_object,
)
from inspirehep.modules.workflows.tasks.submission import (
    finalize_record_sip,
    send_robotupload,
)
from inspirehep.modules.workflows.tasks.upload import store_record_sip

from inspirehep.utils.helpers import get_record_from_model

from invenio_deposit.models import DepositionType

from invenio_workflows.tasks.logic_tasks import (
    workflow_else,
    workflow_if,
)


class ClassProperty(property):

    """Special class to allow a classmethod to be accessed as property."""

    def __get__(self, cls, owner):
        """Call getter and return."""
        return self.fget.__get__(None, owner)()


class hep_ingestion(SIPWorkflowMixin, DepositionType):
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
        workflow_if(exists_in_holding_pen),
        [
            delete_self_and_stop_processing,
        ],
        workflow_if(record_exists),
        [
            stop_processing,
        ],
    ]
    before_halt_check = [
        extract_journal_info,
        classify_paper(
            taxonomy="HEPont",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords(filter_kb="antihep"),
        # Predict action for a generic HEP paper based only on title
        # and abstract.
        guess_coreness("arxiv_skip_astro_title_abstract.pickle"),
    ]
    halt_check = staticmethod(is_record_relevant)
    on_halt = [
        halt_record(action="hep_approval"),
    ]
    on_no_halt = [
        reject_record("Record automatically rejected")
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
                workflow_if(cls.halt_check),
                cls.on_halt,
                workflow_else,
                cls.on_no_halt,
            ] + cls.before_upload_check + [
                workflow_if(cls.upload_check),
                cls.on_upload,
                workflow_else,
                cls.on_no_upload,
            ] + cls.final_processing
        )

    workflow = ClassProperty(get_workflow)

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
