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

"""Ingestion workflow for updated authors."""

from __future__ import absolute_import, print_function

from flask import render_template

from invenio_accounts.models import User
from invenio_workflows_ui.definitions import WorkflowBase

from inspirehep.dojson.hepnames import hepnames2marc
from inspirehep.dojson.utils import legacy_export_as_marc

from inspirehep.modules.workflows.tasks.submission import (
    create_ticket,
    send_robotupload
)

from ..tasks import (
    update_ticket_context,
    formdata_to_model
)


class AuthorUpdate(WorkflowBase):
    """Workflow for author updates."""

    name = "Update Author"
    data_type = "authors"

    workflow = [
        formdata_to_model,
        send_robotupload(
            marcxml_processor=hepnames2marc,
            mode="holdingpen"
        ),
        create_ticket(
            template="authors/tickets/curator_update.html",
            queue="Authors_cor_user",
            context_factory=update_ticket_context,
        ),
    ]

    @staticmethod
    def get_title(obj):
        """Return title of object."""
        try:
            user_email = User.query.get(obj.id_user).email
        except AttributeError:
            user_email = ''

        return u"Author update by: {0}".format(user_email)

    @staticmethod
    def get_description(obj):
        """Return description of object."""
        return "Updating author {}".format(
            obj.data.get("name", {}).get("preferred_name", "No name found")
        )

    @staticmethod
    def formatter(obj, **kwargs):
        """Return formatted data of object."""
        of = kwargs.get("of", "hp")
        if of == "xm":
            return legacy_export_as_marc(
                hepnames2marc.do(obj.data)
            )

        try:
            user_email = User.query.get(obj.id_user).email
        except AttributeError:
            user_email = ''
        ticket_id = obj.extra_data.get("ticket_id")
        ticket_url = "https://rt.inspirehep.net/Ticket/Display.html?id={0}".format(
            ticket_id
        )
        # FIXME add a template for the author display in the HP
        return render_template("authors/workflows/authorupdate.html",
                               record=obj.data,
                               user_email=user_email,
                               ticket_url=ticket_url,
                               comments=obj.extra_data.get("comments"))
