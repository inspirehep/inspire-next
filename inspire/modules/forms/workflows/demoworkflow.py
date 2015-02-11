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

from flask import render_template

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


class demoworkflow(WorkflowBase):

    """Demo workflow for forms module."""

    object_type = "demo"

    workflow = [
        approve_record,
        workflow_if(was_approved),
        [
            log_info("Record has been approved"),
        ],
        workflow_else,
        [
            log_info("Record has been rejected")
        ]
    ]

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        from invenio.modules.access.control import acc_get_user_email
        id_user = bwo.id_user
        user_email = acc_get_user_email(id_user)

        return u"Demo form by: {0}".format(user_email)

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        return bwo.workflow.name

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        return render_template("holdingpen/demoform.html",
                               data=bwo.get_data())
