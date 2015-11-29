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

from flask import current_app, render_template

from invenio_accounts.models import User

from invenio_deposit.models import Deposition

from .hep_approval import hep_approval


class core_approval(hep_approval):

    """Class representing the approval action."""

    def render_mini(self, obj):
        """Method to render the minified action."""
        try:
            user = User.query.get(obj.id_user)
            d = Deposition(obj)
            rejection_text = "\n".join([line.strip() for line in render_template(
                'deposit/tickets/user_rejected.html',
                user=user,
                title=d.title
            ).split("\n")])
        except Exception:
            current_app.logger.exception("Failed to load rejection_text")
            rejection_text = ""
        return render_template(
            'workflows/actions/core_approval_mini.html',
            message=obj.get_action_message(),
            object=obj,
            resolve_url=self.url,
            rejection_text=rejection_text
        )

    def render(self, obj):
        """Method to render the action."""
        try:
            user = User.query.get(obj.id_user)
            d = Deposition(obj)
            rejection_text = "\n".join([line.strip() for line in render_template(
                'deposit/tickets/user_rejected.html',
                user=user,
                title=d.title
            ).split("\n")])
        except Exception:
            current_app.logger.exception("Failed to load rejection_text")
            rejection_text = ""
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
