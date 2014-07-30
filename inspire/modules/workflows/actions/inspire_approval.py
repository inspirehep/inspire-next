# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""Approval action for INSPIRE."""

from invenio.base.i18n import _
from flask import render_template, url_for


class inspire_approval(object):
    """Class representing the approval action."""
    name = _("Approve (INSPIRE)")
    url = url_for("holdingpen.resolve_action")

    def render_mini(self, obj):
        """Method to render the minified action."""
        return render_template(
            'workflows/actions/approval_mini.html',
            message=obj.get_action_message(),
            object=obj,
            resolve_url=self.url,
        )

    def render(self, obj):
        """Method to render the action."""
        return {
            "side": render_template('workflows/actions/approval_side.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url,),
            "main": render_template('workflows/actions/approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url,)
        }

    def resolve(self, bwo):
        """Resolve the action taken in the approval action."""
        from flask import request
        value = request.form.get("value", None)

        if value == 'accept':
            bwo.remove_action()
            bwo.save()
            bwo.continue_workflow(delayed=True)
            return {
                "message": "Record has been accepted!",
                "category": "success",
            }
        elif value == 'reject':
            from invenio.modules.workflows.models import BibWorkflowObject
            BibWorkflowObject.delete(bwo.id)
            return {
                "message": "Record has been rejected (deleted)",
                "category": "warning",
            }
