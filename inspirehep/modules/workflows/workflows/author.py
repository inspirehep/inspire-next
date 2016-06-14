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

from __future__ import absolute_import, print_function

from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.dojson.hepnames import hepnames2marc

from inspirehep.modules.workflows.tasks.actions import (
    is_record_accepted,
    halt_record,
    is_marked,
    emit_record_signals
)

from inspirehep.modules.workflows.tasks.submission import (
    create_ticket,
    reply_ticket,
    close_ticket,
    send_robotupload
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema

from inspirehep.modules.authors.tasks import (
    update_ticket_context,
    curation_ticket_needed,
    new_ticket_context,
    reply_ticket_context,
    curation_ticket_context,
)


class Author(object):
    """Author ingestion workflow for HEPNames/Authors collection."""
    name = "Author"
    data_type = "authors"

    workflow = [
        # Make sure schema is set for proper indexing in Holding Pen
        set_schema,
        # Emit record signals to receive metadata enrichment
        emit_record_signals,
        IF_ELSE(is_marked('is-update'), [
            send_robotupload(
                marcxml_processor=hepnames2marc,
                mode="holdingpen"
            ),
            create_ticket(
                template="authors/tickets/curator_update.html",
                queue="Authors_cor_user",
                context_factory=update_ticket_context,
            ),
        ], [
            create_ticket(
                template="authors/tickets/curator_new.html",
                queue="Authors_add_user",
                context_factory=new_ticket_context),
            reply_ticket(template="authors/tickets/user_new.html",
                         context_factory=reply_ticket_context,
                         keep_new=True),
            halt_record(action="author_approval",
                        message="Accept submission?"),
            IF_ELSE(is_record_accepted, [
                send_robotupload(
                    marcxml_processor=hepnames2marc,
                    mode="insert"
                ),
                reply_ticket(
                    template="authors/tickets/user_accepted.html",
                    context_factory=reply_ticket_context),
                close_ticket(ticket_id_key="ticket_id"),
                IF(curation_ticket_needed, [
                    create_ticket(
                        template="authors/tickets/curation_needed.html",
                        queue="AUTHORS_curation",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id"
                    ),
                ]),
            ], [
                close_ticket(ticket_id_key="ticket_id"),
            ]),
        ]),
    ]
