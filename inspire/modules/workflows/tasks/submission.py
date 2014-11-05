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

"""Contains INSPIRE specific submission tasks"""


import os

from invenio.modules.deposit.models import Deposition
from invenio.modules.formatter import format_record
from flask.ext.login import current_user
from invenio.config import CFG_SITE_SUPPORT_EMAIL
from .actions import was_approved


def halt_to_render(obj, eng):
    """Halt the workflow - waiting to be resumed."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    d.set_render_context(dict(
        template_name_or_list="deposit/pending.html",
        deposition=d,
        deposition_type=(
            None if d.type.is_default() else
            d.type.get_identifier()
        ),
        uuid=d.id,
        sip=sip,
        my_depositions=Deposition.get_depositions(
            current_user, type=d.type
        ),
        format_record=format_record,
    ))
    obj.last_task = "halt_to_render"
    eng.halt("User submission complete.")


def inform_submitter(obj, eng):
    """Send a mail to submitter with the outcome of the submission."""
    from invenio.modules.access.control import acc_get_user_email
    from invenio.ext.email import send_email
    d = Deposition(obj)
    id_user = d.workflow_object.id_user
    email = acc_get_user_email(id_user)
    if was_approved(obj, eng):
        body = 'Accepted: '
        extra_data = d.workflow_object.get_extra_data()
        body += extra_data.get('url', '')
    else:
        body = 'Rejected'
    send_email(CFG_SITE_SUPPORT_EMAIL, email, 'Subject', body, header='header')


def halt_record_with_action(action, message):
    """Halt the record and set an action (with message)."""
    def _halt_record(obj, eng):
        """Halt the workflow for approval."""
        eng.halt(action=action,
                 msg=message)
    return _halt_record


def finalize_and_post_process(workflow_name, **kwargs):
    """Finalize the submission and starts post-processing."""
    def _finalize_and_post_process(obj, eng):
        from invenio.modules.workflows.api import start_delayed
        from invenio.modules.workflows.models import ObjectVersion

        obj.version = ObjectVersion.FINAL
        workflow_id = start_delayed(workflow_name,
                                    data=[obj],
                                    stop_on_error=True,
                                    **kwargs)
        obj.log.info("Started new workflow ({0})".format(workflow_id))
    return _finalize_and_post_process


def send_robotupload_deposit(url=None):
    """Get the MARCXML from the deposit object and ships it."""
    def _send_robotupload_deposit(obj, eng):
        from invenio.modules.deposit.models import Deposition
        from invenio.modules.workflows.errors import WorkflowError
        from inspire.modules.workflows.tasks.upload import send_robotupload
        d = Deposition(obj)

        sip = d.get_latest_sip(d.submitted)

        if not sip:
            raise WorkflowError("No sip found", eng.uuid, obj.id)
        if not d.submitted:
            sip.seal()
            d.update()

        marcxml = sip.package
        send_robotupload(url, marcxml, obj, eng)

    return _send_robotupload_deposit


def add_files_to_task_results(obj, eng):
    """Add Deposition attached files to task results."""
    from invenio.modules.deposit.models import Deposition
    d = Deposition(obj)
    for file_obj in d.files:
        fileinfo = {
            "type": "file",
            "filename": file_obj.name,
            "full_path": file_obj.get_syspath(),
        }
        obj.add_task_result(file_obj.name,
                            fileinfo,
                            "workflows/results/files.html")
