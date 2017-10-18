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


class HEPApproval(object):
    """Class representing the approval action."""
    name = "Approve record"

    @staticmethod
    def resolve(obj, *args, **kwargs):
        """Resolve the action taken in the approval action."""
        from invenio_workflows import ObjectStatus
        from inspirehep.modules.workflows.utils import log_workflows_action

        value = kwargs.get("request_data", {}).get("value", "")
        reason = kwargs.get("request_data", {}).get("reason", "")
        upload_pdf = kwargs.get("request_data", {}).get("pdf_upload", False)

        # Audit logging
        relevance_prediction = obj.extra_data.get("relevance_prediction", {})
        log_workflows_action(
            action="resolve",
            relevance_prediction=relevance_prediction,
            object_id=obj.id,
            user_id=kwargs.get('id_user'),
            source="holdingpen",
            user_action=value,
        )

        if not upload_pdf:
            if 'fulltext.pdf' in obj.files:
                del obj.files['fulltext.pdf']
            documents = obj.data.get('documents', [])
            for doc in documents:
                if doc['key'] == 'fulltext.pdf':
                    documents.remove(doc)
                    break

        approved = value in ('accept', 'accept_core')

        obj.extra_data["approved"] = approved
        obj.remove_action()

        obj.extra_data["user_action"] = value
        obj.extra_data["upload_pdf"] = upload_pdf
        obj.extra_data["core"] = value == "accept_core"
        obj.extra_data["reason"] = reason
        obj.status = ObjectStatus.WAITING
        obj.save()

        obj.continue_workflow(delayed=True)
        return approved
