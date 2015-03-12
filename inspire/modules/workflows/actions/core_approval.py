# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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

from flask import render_template, url_for

from invenio.base.i18n import _
from invenio.modules.accounts.models import User
from invenio.modules.deposit.models import Deposition


class core_approval(object):

    """Class representing the approval action."""

    name = _("Approve record")
    url = url_for("holdingpen.resolve_action")

    def render_mini(self, obj):
        """Method to render the minified action."""
        user = User.query.get(obj.id_user)
        d = Deposition(obj)
        rejection_text = "\n".join([line.strip() for line in render_template(
            'deposit/tickets/user_rejected.html',
            user=user,
            title=d.title
        ).split("\n")])
        return render_template(
            'workflows/actions/core_approval_mini.html',
            message=obj.get_action_message(),
            object=obj,
            resolve_url=self.url,
            rejection_text=rejection_text
        )

    def render(self, obj):
        """Method to render the action."""
        user = User.query.get(obj.id_user)
        d = Deposition(obj)
        rejection_text = "\n".join([line.strip() for line in render_template(
            'deposit/tickets/user_rejected.html',
            user=user,
            title=d.title
        ).split("\n")])
        return {
            "side": render_template('workflows/actions/core_approval_side.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url,
                                    rejection_text=rejection_text),
            "main": render_template('workflows/actions/core_approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url,
                                    rejection_text=rejection_text)
        }

    def resolve(self, bwo):
        """Resolve the action taken in the approval action."""
        from flask import request
        value = request.form.get("value", None)

        bwo.remove_action()
        extra_data = bwo.get_extra_data()
        extra_data["approved"] = value in ('accept', 'accept_core')
        extra_data["core"] = value == "accept_core"
        extra_data["reason"] = request.form.get("text", "")
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
