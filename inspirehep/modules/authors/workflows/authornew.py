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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Ingestion workflow for new authors."""

from __future__ import absolute_import, print_function

from flask import render_template

from invenio_accounts.models import User
from invenio_workflows_ui.definitions import WorkflowBase
from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.dojson.hepnames import hepnames2marc
from inspirehep.modules.workflows.tasks.actions import (
    is_record_accepted,
    halt_record,
)

from inspirehep.modules.workflows.tasks.submission import (
    create_ticket,
    reply_ticket,
    close_ticket,
    send_robotupload
)

from ..tasks import (
    curation_ticket_needed,
    new_ticket_context,
    reply_ticket_context,
    curation_ticket_context,
    formdata_to_model,
    recreate_data
)


class AuthorNew(WorkflowBase):
    """Workflow for new author information."""

    name = "New Author"
    data_type = "authors"

    workflow = [
        formdata_to_model,
        create_ticket(
            template="authors/tickets/curator_new.html",
            queue="Authors_add_user",
            context_factory=new_ticket_context),
        reply_ticket(template="authors/tickets/user_new.html",
                     context_factory=reply_ticket_context,
                     keep_new=True),
        halt_record(action="author_approval",
                    message="Accept submission?"),
        IF_ELSE(is_record_accepted,
                [
                    IF(recreate_data,
                        [formdata_to_model]),
                    send_robotupload(
                        marcxml_processor=hepnames2marc,
                        mode="insert"
                    ),
                    reply_ticket(
                        template="authors/tickets/user_accepted.html",
                        context_factory=reply_ticket_context),
                    close_ticket(ticket_id_key="ticket_id"),
                    IF(curation_ticket_needed,
                        [
                            create_ticket(
                                template="authors/tickets/curation_needed.html",
                                queue="AUTHORS_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id"
                            ),
                        ]),

                ],
                [
                    close_ticket(ticket_id_key="ticket_id"),
                ])
    ]

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        id_user = bwo.id_user
        try:
            user_email = User.query.get(id_user).email
        except AttributeError:
            user_email = ''

        return u"New Author by: {0}".format(user_email)

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        return bwo.data.get("name", {}).get("preferred_name", "No name found")

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        of = kwargs.get("of", "hp")

        id_user = bwo.id_user
        try:
            user_email = User.query.get(id_user).email
        except AttributeError:
            user_email = ''
        ticket_id = bwo.extra_data.get("ticket_id")
        ticket_url = "https://rt.inspirehep.net/Ticket/Display.html?id={}".format(
            ticket_id
        )

        if of == "xm":
            xml = bwo.extra_data.get("marcxml")
            return xml
        else:
            # FIXME add a template for the author display in the HP
            return render_template("authors/workflows/authorupdate.html",
                                   record=bwo.data,
                                   user_email=user_email,
                                   ticket_url=ticket_url,
                                   comments=bwo.extra_data.get("comments"))
