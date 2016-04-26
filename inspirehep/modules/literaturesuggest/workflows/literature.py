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

"""Main HEP literature submission workflow."""

# import copy

from flask import render_template

# from sqlalchemy.orm.exc import NoResultFound

from six import string_types

# from invenio_accounts.models import User
# from invenio_oauthclient.models import UserIdentity
from invenio_records.api import Record

# from invenio_deposit.tasks import (
#     dump_record_sip,
#     render_form,
#     prepare_sip,
#     prefill_draft,
#     process_sip_metadata
# )
# from invenio_deposit.models import Deposition, InvalidDepositionType
# from invenio_knowledge.api import get_kb_mappings
# from workflow.patterns.controlflow import IF, IF_ELSE
from invenio_workflows_ui.definitions import WorkflowBase

from inspirehep.modules.workflows.tasks.actions import shall_upload_record

from inspirehep.modules.workflows.tasks.submission import (
    halt_record_with_action
)

# from inspirehep.dojson.hep import hep2marc

# from inspirehep.modules.workflows.tasks.matching import match

# from inspirehep.modules.workflows.tasks.submission import (
#     halt_record_with_action,
#     send_robotupload,
#     halt_to_render,
#     create_ticket,
#     create_curation_ticket,
#     reply_ticket,
#     add_note_entry,
#     user_pdf_get,
#     close_ticket,
#     finalize_record_sip
# )
# from inspirehep.modules.workflows.tasks.actions import (
#     shall_upload_record,
#     reject_record,
#     add_core_check,
#     shall_push_remotely,
# )
# from inspirehep.modules.workflows.tasks.upload import store_record_sip
from ..forms import LiteratureForm
# from inspirehep.modules.predicter.tasks import guess_coreness

# from ..tasks import (send_robotupload,
#                      create_marcxml_record,
#                      convert_data_to_model,
#                      create_curator_ticket_new,
#                      reply_ticket,
#                      recreate_data,
#                      curation_ticket_needed,
#                      create_curation_ticket)

# from ..tasks import add_submission_extra_data

from ..tasks import (
    add_submission_extra_data,
    convert_data_to_model
)


class literature(WorkflowBase):

    """Literature deposit submission."""

    object_type = "submission"

    workflow = [
        convert_data_to_model(),
        add_submission_extra_data,
        # Generate MARC based on metadata dictionary.
        # create_ticket(template="deposit/tickets/curator_submitted.html",
        #               queue="HEP_add_user",
        #               ticket_id_key="ticket_id"),
        # reply_ticket(template="deposit/tickets/user_submitted.html",
        #              keep_new=True),
        # guess_coreness("literature_guessing.pickle"),
        # classify_paper_with_deposit(
        #    taxonomy="HEPont.rdf",
        #    output_mode="dict",
        # ),
        halt_record_with_action(action="core_approval",
                                message="Accept submission?"),
        # IF_ELSE(shall_upload_record, [

        #     ])
        # [
        #     workflow_if(match, True),
        #     [
        #         add_core_check,
        #         add_note_entry,
        #         user_pdf_get,
        #         finalize_record_sip(processor=hep2marc),
        # Send robotupload and halt until webcoll callback
        #         workflow_if(shall_push_remotely),
        #         [
        #             send_robotupload(),
        #         ],
        #         workflow_else,
        #         [
        #             store_record_sip,
        #         ],
        #         create_curation_ticket(
        #             template="deposit/tickets/curation_core.html",
        #             queue="HEP_curation",
        #             ticket_id_key="curation_ticket_id"
        #         ),
        #         reply_ticket(template="deposit/tickets/user_accepted.html"),
        #     ],
        #     workflow_else,
        #     [
        #         reject_record('Record was already found on INSPIRE'),
        #         reply_ticket(template="deposit/tickets/user_rejected_exists.html"),
        #     ],
        # ],
        # workflow_else,
        # [
        # reply_ticket()  # setting template=None as text come from Holding Pen
        # ],
        # close_ticket(ticket_id_key="ticket_id")
    ]

    # TODO this comes from the legacy SimpleRecordDeposition
    # hold_for_upload = False

    name = "Literature"
    name_plural = "Suggest content"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @classmethod
    def render_completed(cls, d):
        """Page to render when deposition was successfully completed."""
        # TODO this comes from the legacy SimpleRecordDeposition
        pass
        # ctx = dict(
        #     deposition=d,
        #     deposition_type=(
        #         None if d.type.is_default() else d.type.get_identifier()
        #     ),
        #     uuid=d.id,
        #     my_depositions=Deposition.get_depositions(
        #         current_user, type=d.type
        #     ),
        #     sip=d.get_latest_sip(),
        #     format_record=format_record,
        # )

        # return render_template('deposit/completed.html', **ctx)

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from invenio_accounts.models import User

        try:
            email = User.query.get(bwo.id_user).email
        except AttributeError:
            email = ''

        # results = bwo.get_tasks_results()

        data = bwo.data
        if data:
            record = Record(data)
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
                'literaturesuggest/workflows/submission_record.html',
                categories=categories,
                authors=authors,
                identifiers=identifiers,
                # results=results,
                user_email=email,
                object=bwo,
                record=record
            )
        else:
            return "Submitter: {0}".format(email)

    @classmethod
    def formatter(cls, obj, **kwargs):
        """Nicely format the record."""
        record = obj.data
        if not record:
            return ""
        return record
