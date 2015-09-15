# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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


from flask import render_template

from invenio_access.control import acc_get_user_email
from invenio_workflows.definitions import WorkflowBase

from ..tasks import (create_marcxml_record, send_robotupload,
                     convert_data_to_model, create_curator_ticket_update)


class authorupdate(WorkflowBase):

    """Workflow for author updates."""

    object_type = "Author Update"

    workflow = [
        convert_data_to_model(),
        create_marcxml_record(),
        send_robotupload(mode="holdingpen"),
        create_curator_ticket_update(
            template="authors/tickets/curator_update.html",
            queue="Authors_cor_user")
    ]

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        id_user = bwo.id_user
        user_email = acc_get_user_email(id_user)

        return u"Author update by: {0}".format(user_email)

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        return "Updating author {}".format(
            bwo.get_data().get("name", {}).get("display_name")
        )

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""

        of = kwargs.get("of", "hp")

        extra_data = bwo.get_extra_data()
        xml = extra_data.get("marcxml")

        id_user = bwo.id_user
        user_email = acc_get_user_email(id_user)
        ticket_id = extra_data.get("ticket_id")
        ticket_url = "https://rt.inspirehep.net/Ticket/Display.html?id={}".format(
            ticket_id
        )

        if of == "xm":
            return xml
        else:
            # FIXME add a template for the author display in the HP
            return render_template("authors/workflows/authorupdate.html",
                                   record_preview="",
                                   user_email=user_email,
                                   ticket_url=ticket_url,
                                   comments=extra_data.get("comments"))
