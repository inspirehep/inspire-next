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

"""Approval action for INSPIRE."""

from flask import render_template

from .hep_approval import HEPApproval


class CoreApproval(HEPApproval):
    """Class representing the approval action."""

    @staticmethod
    def render_mini(obj):
        """Method to render the minified action."""
        rejection_text = ""
        try:
            from invenio_accounts.models import User
            user = User.query.get(obj.id_user)
            rejection_text = "\n".join([line.strip() for line in render_template(
                'literaturesuggest/tickets/user_rejected.html',
                user=user,
                title=obj.data.get('titles', [{'title': "No title"}])[0]['title']
            ).split("\n")])
        except Exception:
            from flask import current_app
            current_app.logger.exception("Failed to load rejection_text")
        return render_template(
            'inspire_workflows/actions/core_approval_mini.html',
            message=obj.get_action_message(),
            object=obj,
            rejection_text=rejection_text
        )

    @staticmethod
    def render(obj, *args, **kwargs):
        """Method to render the action."""
        rejection_text = ""
        try:
            from invenio_accounts.models import User
            user = User.query.get(obj.id_user)
            rejection_text = "\n".join([line.strip() for line in render_template(
                'literaturesuggest/tickets/user_rejected.html',
                user=user,
                title=obj.data.get('titles', [{'title': "No title"}])[0]['title']
            ).split("\n")])
        except Exception:
            from flask import current_app
            current_app.logger.exception("Failed to load rejection_text")
        return {
            "side": render_template('inspire_workflows/actions/core_approval_side.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    rejection_text=rejection_text),
            "main": render_template('inspire_workflows/actions/core_approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    rejection_text=rejection_text)
        }
