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

from flask import render_template, current_app

from sqlalchemy.orm.exc import NoResultFound

from six import string_types

from invenio_base.globals import cfg
from invenio_ext.login import UserInfo
from invenio_accounts.models import UserEXT
from invenio_records.api import Record

from invenio_deposit.types import SimpleRecordDeposition
from invenio_deposit.tasks import (
    dump_record_sip,
    render_form,
    prepare_sip,
    prefill_draft,
    process_sip_metadata
)
from invenio_deposit.models import Deposition, InvalidDepositionType
from invenio_knowledge.api import get_kb_mappings
from invenio_workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio_workflows.definitions import WorkflowBase

from inspirehep.dojson.hep import hep2marc

from inspirehep.modules.workflows.tasks.matching import match

from inspirehep.modules.workflows.tasks.submission import (
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
from inspirehep.modules.workflows.tasks.actions import (
    shall_upload_record,
    reject_record,
    add_core,
)
from inspirehep.modules.deposit.forms import LiteratureForm
from inspirehep.modules.predicter.tasks import guess_coreness
from inspirehep.utils.helpers import get_record_from_model

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
        guess_coreness("literature_guessing.pickle"),
        # classify_paper_with_deposit(
        #    taxonomy="HEPont.rdf",
        #    output_mode="dict",
        # ),
        halt_record_with_action(action="core_approval",
                                message="Accept submission?"),
        workflow_if(shall_upload_record),
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
            record = Record(sip.metadata)
            return record.get("titles.title", ["No title"])[0]
        else:
            return "User submission in progress"

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from invenio_access.control import acc_get_user_email
        results = bwo.get_tasks_results()
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)

        id_user = deposit_object.workflow_object.id_user
        user_email = acc_get_user_email(id_user)

        sip = deposit_object.get_latest_sip()
        if sip:
            record = Record(sip.metadata)
            identifiers = []
            report_numbers = record.get("report_numbers", [])
            dois = record.get("dois.value", [])
            if report_numbers:
                for report_number in report_numbers:
                    number = report_number.get("value", "")
                    if number:
                        identifiers.append(number)
            if dois:
                identifiers.extend(["doi:{0}".format(d) for d in dois])

            categories = []
            subjects = record.get("subject_terms", [])
            if subjects:
                for subject in subjects:
                    if isinstance(subject, string_types):
                        categories.append(subject)
                    elif isinstance(subject, dict):
                        if subject.get("term"):
                            categories.append(subject.get("term"))
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
        from inspirehep.modules.predicter.utils import get_classification_from_task_results
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

        sip = deposit_object.get_latest_sip(deposit_object.submitted)
        record = sip.metadata

        if hasattr(sip, "package"):
            marcxml = sip.package
        else:
            return "No data found in submission (no package)."

        of = kwargs.get("of", "hd")
        if of == "xm":
            return marcxml
        else:
            return render_template(
                'format/record/Holding_Pen_HTML_detailed.tpl',
                record=Record(record)
            )

    @classmethod
    def get_record(cls, obj, **kwargs):
        """Return a dictionary-like object representing the current object.

        This object will be used for indexing and be the basis for display
        in Holding Pen.
        """
        model = cls.model(obj)
        record = get_record_from_model(model)
        if record:
            return record.dumps()
        return {}

    @classmethod
    def get_sort_data(cls, dummy_obj, **kwargs):
        """Return any extra sorting data."""
        return {}

    @classmethod
    def process_sip_metadata(cls, deposition, metadata):
        from ..dojson.model import literature

        form_fields = copy.deepcopy(metadata)

        filter_empty_elements(metadata)
        converted = literature.do(metadata)
        metadata.clear()
        metadata.update(converted)

        # Add extra fields that need to be computed or depend on other
        # fields.
        #
        # ============================
        # Collection
        # ============================
        metadata['collections'] = [{'primary': "HEP"}]
        if form_fields['type_of_doc'] == 'thesis':
            metadata['collections'].append({'primary': "THESIS"})
        if "subject_terms" in metadata:
            # Check if it was imported from arXiv
            if any([x["scheme"] == "arXiv" for x in metadata["subject_terms"]]):
                metadata['collections'].extend([{'primary': "arXiv"},
                                                {'primary': "Citeable"}])
                # Add arXiv as source
                if metadata.get("abstracts"):
                    metadata['abstracts'][0]['source'] = 'arXiv'
                if form_fields.get("arxiv_id"):
                    metadata['external_system_numbers'] = [{
                        'value': 'oai:arXiv.org:' + form_fields['arxiv_id'],
                        'institute': 'arXiv'
                    }]
        if "publication_info" in metadata:
            metadata['collections'].append({'primary': "Published"})
        # ============================
        # Title source
        # ============================
        if 'title_source' in form_fields and form_fields['title_source']:
            metadata['titles'][0]['source'] = form_fields['title_source']
        # ============================
        # Title from arXiv
        # ============================
        if 'title_arXiv' in form_fields and form_fields['title_arXiv']:
            for title in metadata['titles']:
                if title['title'] == form_fields['title_arXiv']:
                    break
            else:
                metadata['titles'].append({
                    'title': form_fields['title_arXiv'],
                    'source': 'arXiv'
                })
        # ============================
        # Conference name
        # ============================
        if 'conf_name' in form_fields:
            if 'nonpublic_note' in form_fields:
                metadata.setdefault("hidden_notes", []).append({
                    "value": form_fields['conf_name']
                })
                metadata['hidden_notes'].append({
                    'value': form_fields['nonpublic_note']
                })
            else:
                metadata.setdefault("hidden_notes", []).append({
                    "value": form_fields['conf_name']
                })
            metadata['collections'].extend([{'primary': "ConferencePaper"}])

        # ============================
        # Page range
        # ============================
        if 'page_nr' not in metadata:
            if metadata.get("publication_info", {}).get("page_artid"):
                pages = metadata['publication_info']['page_artid'].split('-')
                if len(pages) == 2:
                    try:
                        metadata['page_nr'] = int(pages[1]) - int(pages[0]) + 1
                    except ValueError:
                        pass
        # ============================
        # Language
        # ============================
        if metadata.get("languages", []) and metadata["languages"][0] == "oth":
            if form_fields.get("other_language"):
                metadata["languages"] = [form_fields["other_language"]]

        # ===============================
        # arXiv category in report number
        # ===============================
        if metadata.get("_categories"):
            del metadata["_categories"]

        # ============================
        # Date of defense
        # ============================
        if form_fields.get('defense_date'):
            defense_note = {
                'value': 'Presented on ' + form_fields['defense_date']
            }
            metadata.setdefault("public_notes", []).append(defense_note)
        # ==========
        # Owner Info
        # ==========
        userid = deposition.user_id
        user = UserInfo(userid)
        email = user.info.get('email', '')
        try:
            source = UserEXT.query.filter_by(id_user=userid, method='orcid').one()
        except NoResultFound:
            source = ''
        if source:
            source = source.method + ':' + source.id
        metadata['acquisition_source'] = dict(
            source=source,
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
            metadata.setdefault('hidden_notes', []).append(
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
        if metadata.get("publication_info") and not isinstance(metadata['publication_info'], list):
            metadata["publication_info"] = [metadata['publication_info']]
