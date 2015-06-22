# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from flask import render_template

from invenio.base.globals import cfg

from invenio.modules.deposit.types import SimpleRecordDeposition
from invenio.modules.deposit.tasks import render_form, \
    prepare_sip, \
    finalize_record_sip, \
    prefill_draft, \
    process_sip_metadata
from invenio.modules.deposit.models import Deposition, InvalidDepositionType
from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_deposit,
)
from invenio.modules.knowledge.api import get_kb_mappings
from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio.modules.workflows.definitions import WorkflowBase

from inspire.modules.workflows.tasks.matching import(
    match_record_remote_deposit,
)
from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload_deposit,
    halt_to_render,
    add_files_to_task_results,
    create_ticket,
    reply_ticket
)
from inspire.modules.workflows.tasks.actions import (
    was_approved,
    reject_record,
    add_core
)
from inspire.modules.deposit.hepnamesform import HEPNamesForm


class hepnames(SimpleRecordDeposition, WorkflowBase):

    """Literature deposit submission."""

    object_type = "submission"

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        halt_to_render,
        halt_record_with_action(action="core_approval",
                                message="Accept submission?"),
        # workflow_if(was_approved),
        # [
        #     workflow_if(match_record_remote_deposit, True),
        #     [
        #         add_core,
        #         send_robotupload_deposit(),
        #         reply_ticket(template="deposit/tickets/user_accepted.html")
        #     ],
        #     workflow_else,
        #     [
        #         reject_record('Record was already found on INSPIRE'),
        #         reply_ticket(template="deposit/tickets/user_rejected.html")
        #     ],
        # ],
        #workflow_else,
        #[
        #    reply_ticket(template="deposit/tickets/user_rejected.html")
        #],
    ]

    name = "Update author details"
    name_plural = "Update author's details"
    group = "Authors"
    draft_definitions = {
        'default': HEPNamesForm,
    }
    template = "deposit/hepnames/run.html"

    # @classmethod
    # def process_sip_metadata(cls, deposition, metadata):
