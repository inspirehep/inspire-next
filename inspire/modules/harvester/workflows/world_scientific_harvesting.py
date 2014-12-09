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

"""Implements an example of a typical ingestion workflow for MARCXML records"""
from invenio.modules.workflows.definitions import WorkflowBase

from ..tasks.world_scientific import (
    get_files,
    unzip_file,
    convert_files,
    create_collection,
    upload_to_desy,
)


class world_scientific_harvesting(WorkflowBase):

    """Main workflow for harvesting arXiv via OAI-PMH (oaiharvester)."""

    object_type = "workflow"
    workflow = [
        get_files,
        unzip_file,
        convert_files,
        create_collection,
        upload_to_desy,
    ]

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        return world_scientific_harvesting.get_description(bwo)
