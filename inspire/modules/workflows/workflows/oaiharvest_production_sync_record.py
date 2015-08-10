# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
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
# 59 Temple Place, Suite 330, Boston, MA 02111 1307, USA.

"""Generic record process in harvesting with backwards compatibility."""

from invenio.modules.workflows.definitions import RecordWorkflow

from inspire.modules.oaiharvester.tasks.filtering import get_content_from_file


class oaiharvest_production_sync_record(RecordWorkflow):

    """Workflow run for each file containing OAI records harvested."""

    object_type = "OAI harvest"

    workflow = [
        get_content_from_file,
        # TODO: Add new records with records API.
        # convert_record_with_repository("oaimarc2marcxml.xsl"),
        # upload_step_marcxml,
    ]

    @staticmethod
    def get_title(bwo):
        """Get the title."""
        data = bwo.get_data()
        count = 0
        if data and hasattr(data, "count"):
            count = data.count("<record>")

        repository = bwo.get_extra_data().get("repository")
        name = "Unknown"
        if repository:
            name = repository.get("name", "")
        return "{0} harvested records from {1}".format(count, name)

    @staticmethod
    def get_description(bwo):
        """Get the title."""
        return "Bundle of harvested records in MARCXML."
