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

"""Merge action for INSPIRE."""

from __future__ import absolute_import, division, print_function


class MergeApproval(object):
    """Class representing the merge action."""
    name = "Merge records"

    @staticmethod
    def resolve(obj, *args, **kwargs):
        """Resolve the action taken in the approval action."""

        obj.extra_data["approved"] = True
        obj.extra_data["auto-approved"] = False
        obj.remove_action()
        obj.save()

        delayed = True
        if obj.workflow.name == 'manual_merge':
            # the manual merge wf should be sync
            delayed = False

        obj.continue_workflow(delayed=delayed)
        return True
