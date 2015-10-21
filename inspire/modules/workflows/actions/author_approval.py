# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

from invenio_base.i18n import _
from flask import render_template, url_for


class author_approval(object):
    """Class representing the approval action."""
    name = _("Approve")
    url = url_for("holdingpen.resolve_action")

    def render_mini(self, obj):
        """Method to render the minified action."""
        return ""

    def render(self, obj):
        """Method to render the action."""
        return {
            "side": "",
            "main": render_template('workflows/actions/author_approval_main.html',
                                    message=obj.get_action_message(),
                                    object=obj,
                                    resolve_url=self.url,)
        }

    def resolve(self, bwo):
        """Resolve the action taken in the approval action."""
        pass
