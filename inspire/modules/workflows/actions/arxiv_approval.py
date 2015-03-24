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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Approval action for INSPIRE arXiv harvesting."""

from flask import render_template, url_for, current_app

from invenio.base.i18n import _
from invenio.modules.accounts.models import User
from invenio.modules.deposit.models import Deposition


class arxiv_approval(object):

    """Class representing the approval action."""

    name = _("Approve record")
    url = url_for("holdingpen.resolve_action")

    def render_mini(self, obj):
        """Method to render the minified action."""
        return render_template(
            'workflows/actions/arxiv_approval_mini.html',
            message=obj.get_action_message(),
            object=obj,
            resolve_url=self.url,
        )

    def render(self, obj):
        """Method to render the action."""
        return {
            "side": render_template('workflows/actions/arxiv_approval_side.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url),
            "main": render_template('workflows/actions/arxiv_approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url)
        }

    def resolve(self, bwo):
        """Resolve the action taken in the approval action."""
        from flask import request

        value = request.form.get("value", None)
        upload_pdf = request.form.get("pdf_submission", False)

        bwo.remove_action()
        extra_data = bwo.get_extra_data()
        extra_data["approved"] = value in ('accept', 'accept_core')
        extra_data["core"] = value == "accept_core"
        extra_data["reason"] = request.form.get("text", "")
        extra_data["pdf_upload"] = True if upload_pdf == "true" else False
        bwo.set_extra_data(extra_data)
        bwo.save()
        bwo.continue_workflow(delayed=True)

        if extra_data["approved"]:
            return {
                "message": "Suggestion has been accepted!",
                "category": "success",
            }
        else:
            return {
                "message": "Suggestion has been rejected",
                "category": "warning",
            }
