# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import copy

from flask import render_template

from six import string_types

from invenio.base.globals import cfg
from invenio.ext.login import UserInfo
from invenio_accounts.models import UserEXT

from invenio_deposit.types import SimpleRecordDeposition
from invenio_deposit.tasks import (
    dump_record_sip,
    render_form,
    prepare_sip,
    prefill_draft,
    process_sip_metadata
)
from invenio_deposit.models import Deposition, InvalidDepositionType
from invenio.modules.knowledge.api import get_kb_mappings
from invenio_workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio_workflows.definitions import WorkflowBase

from inspire.dojson.hep import hep2marc

from inspire.modules.workflows.tasks.matching import match

from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload,
    halt_to_render,
    create_ticket,
    create_curation_ticket,
    reply_ticket,
    add_note_entry,
    user_pdf_get,
    close_ticket,
    finalize_record_sip
)
from inspire.modules.workflows.tasks.actions import (
    was_approved,
    reject_record,
    add_core,
)
from inspire.modules.deposit.forms import LiteratureForm
from inspire.modules.predicter.tasks import guess_coreness

from ..tasks import add_submission_extra_data
from ..utils import filter_empty_helper


def filter_empty_elements(recjson):
    """Filter empty fields."""
    list_fields = [
        'authors', 'supervisors', 'report_numbers'
    ]
    for key in list_fields:
        recjson[key] = filter(
            filter_empty_helper(), recjson.get(key, [])
        )

    return recjson


class literature(SimpleRecordDeposition, WorkflowBase):

    """Literature deposit submission."""

    object_type = "submission"

    model = Deposition

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        dump_record_sip(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        add_submission_extra_data,
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(processor=hep2marc),
        halt_to_render,
        create_ticket(template="deposit/tickets/curator_submitted.html",
                      queue="HEP_add_user",
                      ticket_id_key="ticket_id"),
        reply_ticket(template="deposit/tickets/user_submitted.html",
                     keep_new=True),
        # add_files_to_task_results,  Not needed as no files are added..
        guess_coreness("new_astro_model.pickle"),
        # classify_paper_with_deposit(
        #    taxonomy="HEPont.rdf",
        #    output_mode="dict",
        # ),
        halt_record_with_action(action="core_approval",
                                message="Accept submission?"),
        workflow_if(was_approved),
        [
            workflow_if(match, True),
            [
                add_core,
                add_note_entry,
                user_pdf_get,
                finalize_record_sip(processor=hep2marc),
                # Send robotupload and halt until webcoll callback
                send_robotupload(),
                create_curation_ticket(
                    template="deposit/tickets/curation_core.html",
                    queue="HEP_curation",
                    ticket_id_key="curation_ticket_id"
                ),
                reply_ticket(template="deposit/tickets/user_accepted.html"),
            ],
            workflow_else,
            [
                reject_record('Record was already found on INSPIRE'),
                reply_ticket(template="deposit/tickets/user_rejected_exists.html"),
            ],
        ],
        workflow_else,
        [
            reply_ticket()  # setting template=None as text come from Holding Pen
        ],
        close_ticket(ticket_id_key="ticket_id")
    ]

    name = "Literature"
    name_plural = "Suggest content"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)
        sip = deposit_object.get_latest_sip()
        if sip:
            # Get the SmartJSON object
            record = sip.metadata
            try:
                return record.get("title", {"title": "No title"}).get("title")
            except AttributeError:
                return record.get("title")
        else:
            return "User submission in progress"

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from invenio.modules.access.control import acc_get_user_email
        results = bwo.get_tasks_results()
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)

        id_user = deposit_object.workflow_object.id_user
        user_email = acc_get_user_email(id_user)

        sip = deposit_object.get_latest_sip()
        if sip:
            record = sip.metadata
            identifiers = []
            report_numbers = record.get("report_number", [])
            doi = record.get("doi", {}).get("doi")
            if report_numbers:
                for report_number in report_numbers:
                    number = report_number.get("primary", "")
                    if number:
                        identifiers.append(number)
            if doi:
                identifiers.append("doi:{0}".format(doi))

            categories = []
            subjects = record.get("subject_term", [])
            if subjects:
                for subject in subjects:
                    if isinstance(subject, string_types):
                        categories += [subject]
                    else:
                        categories += [subject.get("term") for subject in subjects]
            categories = [record.get("type_of_doc", "")] + categories

            authors = []
            authors += [record.get("_first_author", {})]
            authors += record.get("_additional_authors", [])
            return render_template(
                'workflows/styles/submission_record.html',
                categories=categories,
                authors=authors,
                identifiers=identifiers,
                results=results,
                user_email=user_email,
                object=bwo,
                record=record
            )
        else:
            return "Submitter: {0}".format(user_email)

    @staticmethod
    def get_additional(bwo, **kwargs):
        """Return formatted data of object."""
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
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)

        submission_data = deposit_object.get_latest_sip(deposit_object.submitted)
        record = submission_data.metadata

        return render_template(
            'format/record/Holding_Pen_HTML_detailed.tpl',
            record=record
        )

    @classmethod
    def process_sip_metadata(cls, deposition, metadata):
        from ..dojson.model import literature

        form_fields = copy.deepcopy(metadata)

        filter_empty_elements(metadata)
        converted = literature.do(metadata)
        metadata.clear()
        metadata.update(converted)

        try:
            # Add extra fields that need to be computed or depend on other
            # fields.
            #
            # ============================
            # Collection
            # ============================
            metadata['collections'] = [{'primary': "HEP"}]
            if form_fields['type_of_doc'] == 'thesis':
                metadata['collections'].append({'primary': "THESIS"})
            if "subject_term" in metadata:
                # Check if it was imported from arXiv
                if any([x["scheme"] == "arXiv" for x in metadata["subject_term"]]):
                    metadata['collections'].extend([{'primary': "arXiv"},
                                                    {'primary': "Citeable"}])
                    # Add arXiv as source
                    if metadata.get("abstract"):
                        metadata['abstract']['source'] = 'arXiv'
                    if form_fields.get("arxiv_id"):
                        metadata['system_number_external'] = {
                            'system_number_external': 'oai:arXiv.org:' + form_fields['arxiv_id'],
                            'institute': 'arXiv'
                        }
            if metadata["publication_info"]:
                metadata['collections'].append({'primary': "Published"})
            # ============================
            # Title source
            # ============================
            if 'title_source' in form_fields and form_fields['title_source']:
                metadata['title']['source'] = form_fields['title_source']
            # ============================
            # Conference name
            # ============================
            if 'conf_name' in form_fields:
                metadata.setdefault("hidden_note", []).append({
                    "value": form_fields['conf_name']
                })
            # ============================
            # Page range
            # ============================
            if 'page_nr' not in metadata:
                if metadata.get("publication_info", {}).get("page_artid"):
                    pages = metadata['publication_info']['page_artid'].split('-')
                    if len(pages) == 2:
                        try:
                            metadata['page_nr'] = {
                                "value": int(pages[1]) - int(pages[0]) + 1
                            }
                        except ValueError:
                            pass
            # ============================
            # Language
            # ============================
            if metadata.get("language") == "oth":
                if form_fields.get("other_language"):
                    metadata["language"] = form_fields["other_language"]
            # ============================
            # Date of defense
            # ============================
            if form_fields.get('defense_date'):
                defense_note = {
                    'value': 'Presented on ' + form_fields['defense_date']
                }
                metadata.setdefault("note", []).append(defense_note)
            # ==========
            # Owner Info
            # ==========
            userid = deposition.user_id
            user = UserInfo(userid)
            email = user.info.get('email', '')
            external_ids = UserEXT.query.filter_by(id_user=userid).all()
            sources = ["{0}{1}".format('inspire:uid:', userid)]
            sources.extend(["{0}:{1}".format(e_id.method,
                                             e_id.id) for e_id in external_ids])
            metadata['acquisition_source'] = dict(
                source=sources,
                email=email,
                method="submission",
                submission_number=deposition.id,
            )
            # ==============
            # References
            # ==============
            if form_fields.get('references'):
                metadata['references'] = form_fields.get('references')
            # ==============
            # Extra comments
            # ==============
            if form_fields.get('extra_comments'):
                metadata.setdefault('hidden_note', []).append(
                    {
                        'value': form_fields['extra_comments'],
                        'source': 'submitter'
                    }
                )
            # ======================================
            # Journal name Knowledge Base conversion
            # ======================================
            if metadata.get("publication_info", {}).get("journal_title"):
                journals_kb = dict([(x['key'].lower(), x['value'])
                                    for x in get_kb_mappings(cfg.get("DEPOSIT_INSPIRE_JOURNALS_KB"))])

                metadata['publication_info']['journal_title'] = journals_kb.get(metadata['publication_info']['journal_title'].lower(),
                                                                                metadata['publication_info']['journal_title'])
        except KeyError:
            pass
