# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

from invenio.modules.workflows.definitions import WorkflowBase


class HarvestingWorkflowBase(WorkflowBase):

    """Base harvesting definition."""

    @staticmethod
    def get_title(bwo, **kwargs):
        """Return the value to put in the title column of HoldingPen."""
        args = bwo.get_extra_data().get("args", {})
        return "Summary of {0} harvesting from {1} to {2}".format(
            args.get("workflow", "unknown"),
            args.get("from_date", "unknown"),
            args.get("to_date", "unknown"),
        )

    @staticmethod
    def get_description(bwo, **kwargs):
        """Return the value to put in the title  column of HoldingPen."""
        return "No description. See log for details."

    @staticmethod
    def formatter(obj, **kwargs):
        """Format the object."""
        return "No data. See log for details."
