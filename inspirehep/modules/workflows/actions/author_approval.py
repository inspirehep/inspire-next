# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Approval action for INSPIRE arXiv harvesting."""

from __future__ import absolute_import, division, print_function

from invenio_db import db


class AuthorApproval(object):
    """Class representing the author approval action."""
    name = "Approve author"

    @staticmethod
    def resolve(obj, *args, **kwargs):
        """Resolve the action taken in the approval action."""
        request_data = kwargs.get("request_data", {})
        value = request_data.get("value", "")
        approved = value in ('accept', 'accept_curate')
        ticket = value == 'accept_curate'

        obj.extra_data["approved"] = approved
        obj.extra_data["ticket"] = ticket
        obj.extra_data["user_action"] = value
        obj.save()
        db.session.commit()

        obj.continue_workflow(delayed=True)
