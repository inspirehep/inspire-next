# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Author Approval action."""

from flask import render_template

from invenio_db import db


class AuthorApproval(object):
    """Class representing the approval action."""
    name = "Approve author update"

    @staticmethod
    def render_mini(obj):
        """Method to render the minified action."""
        return ""

    @staticmethod
    def render(obj):
        """Method to render the action."""
        return {
            "side": "",
            "main": render_template('inspire_workflows/actions/author_approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj)
        }

    @staticmethod
    def resolve(obj, *args, **kwargs):
        """Resolve the action taken in the approval action."""
        request_data = kwargs.get("request_data", {})
        value = request_data.get("value", "")
        approved = value in ('accept', 'accept_curate')
        ticket = value == 'accept_curate'

        obj.extra_data["approved"] = approved
        obj.extra_data["ticket"] = ticket
        obj.save()
        db.session.commit()

        obj.continue_workflow(delayed=True)
