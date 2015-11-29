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

from invenio_workflows.definitions import WorkflowBase
from invenio_workflows.tasks.logic_tasks import (
    workflow_else,
    workflow_if,
)

from inspirehep.modules.workflows.tasks.actions import shall_halt_workflow
from invenio_workflows.tasks.workflows_tasks import log_info


def approve_record(obj, eng):
    """Will add the approval widget to the record.

    The workflow need to be halted to use the
    action in the holdingpen.
    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    try:
        eng.halt(action="approval",
                 msg='Record needs approval')
    except KeyError:
        # Log the error
        obj.extra_data["_error_msg"] = 'Could not assign action'


class demoworkflow(WorkflowBase):

    """Demo workflow for forms module."""

    object_type = "demo"

    workflow = [
        approve_record,
        workflow_if(shall_halt_workflow),
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
        from invenio_access.control import acc_get_user_email
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
