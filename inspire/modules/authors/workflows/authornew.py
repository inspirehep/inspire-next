#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

from flask import render_template, url_for

from invenio.modules.workflows.definitions import WorkflowBase
from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_else,
    workflow_if,
)
from invenio.modules.workflows.tasks.marcxml_tasks import (
    approve_record,
    was_approved
)
from invenio.modules.workflows.tasks.workflows_tasks import log_info

from ..tasks import send_robotupload, \
    create_marcxml_record, \
    convert_data_to_model, \
    create_curator_ticket_new, \
    reply_ticket


class authornew(WorkflowBase):

    """Workflow for new author information."""

    object_type = "Author New"

    workflow = [
        convert_data_to_model(),
        create_marcxml_record(),
        create_curator_ticket_new(
            template="authors/tickets/curator_new.html",
            queue="Authors_add_user"),
        reply_ticket(template="authors/tickets/user_new.html",
                     keep_new=True),
        approve_record,
        workflow_if(was_approved),
        [
            send_robotupload(mode="insert"),
            reply_ticket(template="authors/tickets/user_accepted.html"),
            log_info("New author info has been approved"),
        ],
        workflow_else,
        [
            log_info("New author info has been rejected")
        ]
    ]

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        from invenio.modules.access.control import acc_get_user_email
        id_user = bwo.id_user
        user_email = acc_get_user_email(id_user)

        return u"New Author by: {0}".format(user_email)

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        return bwo.get_data().get("name").get("preferred_name")

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        form_url = url_for("inspire_authors.newreview", objectid=bwo.id)
        extra_data = bwo.get_extra_data()
        return render_template("authors/workflows/authorupdate.html",
                               data=bwo.get_data(),
                               marcxml=extra_data.get("marcxml"),
                               form_url=form_url,
                               comments=extra_data.get("comments"))
