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

"""Workflow for processing single arXiv records harvested."""

from __future__ import absolute_import, division, print_function

from workflow.patterns.controlflow import IF, IF_ELSE, IF_NOT

from inspirehep.modules.workflows.tasks.actions import (
    halt_record,
    in_production_mode,
    is_marked,
    is_record_accepted,
)

from inspirehep.modules.workflows.tasks.submission import (
    close_ticket,
    create_ticket,
    reply_ticket,
    send_robotupload
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema

from inspirehep.modules.authors.tasks import (
    curation_ticket_context,
    curation_ticket_needed,
    new_ticket_context,
    reply_ticket_context,
    update_ticket_context,
)


SEND_TO_LEGACY = [
    send_robotupload(
        mode="insert"
    ),
]


NOTIFY_ACCEPTED = [
    reply_ticket(
        template="authors/tickets/user_accepted.html",
        context_factory=reply_ticket_context),
    close_ticket(ticket_id_key="ticket_id"),
]


CLOSE_TICKET_IF_NEEDED = [
    IF(curation_ticket_needed, [
        create_ticket(
            template="authors/tickets/curation_needed.html",
            queue="AUTHORS_curation",
            context_factory=curation_ticket_context,
            ticket_id_key="curation_ticket_id"
        ),
    ]),
]


NOTIFY_NOT_ACCEPTED = [
    close_ticket(ticket_id_key="ticket_id"),
]


SEND_UPDATE_NOTIFICATION = [
    send_robotupload(
        mode="holdingpen",
        callback_url=None
    ),
    create_ticket(
        template="authors/tickets/curator_update.html",
        queue="Authors_cor_user",
        context_factory=update_ticket_context,
    ),
    reply_ticket(
        template="authors/tickets/user_new.html",
        context_factory=reply_ticket_context,
        keep_new=True,
    ),
]


ASK_FOR_REVIEW = [
    create_ticket(
        template="authors/tickets/curator_new.html",
        queue="Authors_add_user",
        context_factory=new_ticket_context,
    ),
    reply_ticket(
        template="authors/tickets/user_new.html",
        context_factory=reply_ticket_context,
        keep_new=True,
    ),
    halt_record(
        action="author_approval",
        message="Accept submission?",
    ),
]


class Author(object):
    """Author ingestion workflow for HEPNames/Authors collection."""
    name = "Author"
    data_type = "authors"

    workflow = [
        # Make sure schema is set for proper indexing in Holding Pen
        set_schema,
        IF_ELSE(
            is_marked('is-update'),
            SEND_UPDATE_NOTIFICATION,
            ASK_FOR_REVIEW +
            [
                IF_ELSE(
                    is_record_accepted,
                    (
                        SEND_TO_LEGACY +
                        NOTIFY_ACCEPTED +
                        [
                            # TODO: once legacy is out, this should become
                            # unconditional, and remove the SEND_TO_LEGACY
                            # steps
                            IF_NOT(in_production_mode, [store_record]),
                        ] +
                        CLOSE_TICKET_IF_NEEDED
                    ),
                    NOTIFY_NOT_ACCEPTED
                ),
            ],
        ),
    ]
