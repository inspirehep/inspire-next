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

from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.modules.workflows.tasks.actions import (
    halt_record,
    is_marked,
    is_record_accepted,
    load_from_source_data,
    validate_record,
)

from inspirehep.modules.workflows.tasks.submission import (
    close_ticket,
    create_ticket,
    reply_ticket,
    send_robotupload
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema

from inspirehep.modules.workflows.tasks.author import (
    curation_ticket_context,
    curation_ticket_needed,
    new_ticket_context,
    reply_ticket_context,
    update_ticket_context,
)
from inspirehep.modules.workflows.utils import do_not_repeat


SEND_TO_LEGACY = [
    send_robotupload(mode='replace', priority_config_key='LEGACY_ROBOTUPLOAD_PRIORITY_AUTHOR'),
]


NOTIFY_AND_CLOSE_ACCEPTED = [
    do_not_repeat('close_ticket_author_submission_accepted')(
        close_ticket(
            ticket_id_key="ticket_id",
            template="authors/tickets/user_accepted_author.html",
            context_factory=reply_ticket_context)
    ),
]


CLOSE_TICKET_IF_NEEDED = [
    IF(curation_ticket_needed, [
        do_not_repeat('create_ticket_author_submission_curation_needed')(
            create_ticket(
                template="authors/tickets/curation_needed_author.html",
                queue="AUTHORS_curation",
                context_factory=curation_ticket_context,
                ticket_id_key="curation_ticket_id"
            )
        ),
    ]),
]


NOTIFY_NOT_ACCEPTED = [
    close_ticket(ticket_id_key="ticket_id"),
]


SEND_UPDATE_NOTIFICATION = [
    do_not_repeat('create_ticket_author_submission_curator_update')(
        create_ticket(
            template="authors/tickets/curator_update_author.html",
            queue="Authors_cor_user",
            context_factory=update_ticket_context,
        )
    )
]


ASK_FOR_REVIEW = [
    do_not_repeat('create_ticket_author_submission_curator_new')(
        create_ticket(
            template="authors/tickets/curator_new_author.html",
            queue="Authors_add_user",
            context_factory=new_ticket_context,
        )
    ),
    do_not_repeat('reply_ticket_author_submission_user_new')(
        reply_ticket(
            template="authors/tickets/user_new_author.html",
            context_factory=reply_ticket_context,
            keep_new=True,
        )
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
        load_from_source_data,
        # Make sure schema is set for proper indexing in Holding Pen
        set_schema,
        validate_record('authors'),
        IF_ELSE(
            is_marked('is-update'),
            [
                SEND_TO_LEGACY,
                SEND_UPDATE_NOTIFICATION,
            ],
            [
                ASK_FOR_REVIEW,
                IF_ELSE(
                    is_record_accepted,
                    (
                        [store_record] +
                        SEND_TO_LEGACY +
                        NOTIFY_AND_CLOSE_ACCEPTED +
                        CLOSE_TICKET_IF_NEEDED
                    ),
                    NOTIFY_NOT_ACCEPTED
                ),
            ],
        ),
    ]
