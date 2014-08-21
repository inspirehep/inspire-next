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

from flask import render_template

from invenio.modules.deposit.models import Deposition
from invenio.modules.workflows.utils import WorkflowBase

from ..tasks.submission import (
    approve_record,
    send_robotupload,
)
from ..config import CFG_ROBOTUPLOAD_SUBMISSION_BASEURL


class process_record_submission(WorkflowBase):

    """Sub-workflow for post-processing of submissions."""

    object_type = "deposit"
    workflow = [
        # Halt the record for approval
        approve_record,
        send_robotupload(CFG_ROBOTUPLOAD_SUBMISSION_BASEURL),
    ]

    @staticmethod
    def get_title(bwo):
        """Get the title."""
        deposit_object = Deposition(bwo)
        submission_data = deposit_object.get_latest_sip()

        # Get the SmartJSON object
        record = submission_data.metadata
        return record.get("title", "No title").get("main")

    @staticmethod
    def get_description(bwo):
        """Get the description column part."""
        deposit_object = Deposition(bwo)
        submission_data = deposit_object.get_latest_sip()

        # Get the SmartJSON object
        record = submission_data.metadata
        identifiers = [record.get("arxiv_id", "")]
        categories = [record.get("type_of_doc", "")]
        return render_template('workflows/styles/submission_record.html',
                               categories=categories,
                               identifiers=identifiers)

    @staticmethod
    def formatter(bwo, **kwargs):
        from invenio.modules.formatter.engine import format_record
        deposit_object = Deposition(bwo)
        submission_data = deposit_object.get_latest_sip()
        marcxml = submission_data.package

        of = kwargs.get("format", "hd")
        if of == "xm":
            return marcxml
        else:
            return format_record(
                recID=None,
                of=kwargs.get("format", "hd"),
                xml_record=marcxml
            )
