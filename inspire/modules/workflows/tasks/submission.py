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


from functools import wraps

from invenio.modules.deposit.models import Deposition
from invenio.modules.formatter import format_record
from flask.ext.login import current_user
from invenio.base.globals import cfg
from .actions import was_approved


def halt_to_render(obj, eng):
    """Halt the workflow - waiting to be resumed."""
    d = Deposition(obj)
    sip = d.get_latest_sip(sealed=False)
    d.set_render_context(dict(
        template_name_or_list="deposit/completed.html",
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
    send_email(cfg.get("CFG_SITE_SUPPORT_EMAIL"), email, 'Subject', body, header='header')


def create_ticket(template, queue="Test", ticket_id_key="ticket_id"):
    """Create a ticket for the submission.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key."""
    @wraps(create_ticket)
    def _create_ticket(obj, eng):
        from invenio.modules.access.control import acc_get_user_email
        from inspire.utils.tickets import get_instance
        from flask import render_template

        d = Deposition(obj)
        email = acc_get_user_email(obj.id_user)
        rt_queue = cfg.get("CFG_BIBCATALOG_QUEUES") or queue
        sip = d.get_latest_sip(sealed=False)
        subject = u"Your suggestion to INSPIRE: {0}".format(d.title)
        body = render_template(
            template,
            email=email,
            title=d.title,
            identifier=sip.metadata.get("system_number_external", {}).get("value", ""),
            object=obj,
        ).strip()

        # Trick to prepare ticket body
        body = "\n ".join([line.strip() for line in body.split("\n")])
        rt = get_instance() if cfg.get("PRODUCTION_MODE") else None
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
            obj.log.info("Ticket ignored.")
        else:
            ticket_id = rt.create_ticket(
                Queue=rt_queue,
                Subject=subject,
                Text=body,
                Requestors=email
            )
            obj.extra_data[ticket_id_key] = ticket_id
            obj.log.info("Ticket {0} created:\n{1}".format(
                ticket_id,
                body.encode("utf-8", "ignore")
            ))
    return _create_ticket


def reply_ticket(template=None, keep_new=False):
    """Reply to a ticket for the submission."""
    @wraps(reply_ticket)
    def _reply_ticket(obj, eng):
        from invenio.modules.access.control import acc_get_user_email
        from invenio.modules.workflows.errors import WorkflowError
        from inspire.utils.tickets import get_instance
        from flask import render_template

        ticket_id = obj.extra_data.get("ticket_id", "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        if template:
            # Body rendered by template.
            d = Deposition(obj)
            email = acc_get_user_email(obj.id_user)

            context = {
                "object": obj,
                "email": email,
                "title": d.title,
                "reason": obj.extra_data.get("reason", ""),
                "record_url": obj.extra_data.get("url", ""),
            }

            body = render_template(
                template,
                **context
            )
        else:
            # Body already rendered in reason.
            body = obj.extra_data.get("reason").strip()
        if not body:
            raise WorkflowError("No body for ticket reply")
        # Trick to prepare ticket body
        body = "\n ".join([line.strip() for line in body.strip().split("\n")])

        rt = get_instance()
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
        else:
            rt.reply(
                ticket_id=ticket_id,
                text=body,
            )
            obj.log.info("Reply created:\n{0}".format(
                body.encode("utf-8", "ignore")
            ))
            if keep_new:
                # We keep the state as new
                rt.edit_ticket(
                    ticket_id=ticket_id,
                    Status="new"
                )
    return _reply_ticket


def close_ticket(ticket_id_key="ticket_id"):
    """Close the ticket associated with this record found in given key."""
    @wraps(close_ticket)
    def _close_ticket(obj, eng):
        from inspire.utils.tickets import get_instance

        ticket_id = obj.extra_data.get(ticket_id_key, "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        rt = get_instance()
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
        else:
            rt.edit_ticket(
                ticket_id=ticket_id,
                Status="resolved"
            )
    return _close_ticket


def halt_record_with_action(action, message):
    """Halt the record and set an action (with message)."""
    @wraps(halt_record_with_action)
    def _halt_record(obj, eng):
        """Halt the workflow for approval."""
        eng.halt(action=action,
                 msg=message)
    return _halt_record


def finalize_and_post_process(workflow_name, **kwargs):
    """Finalize the submission and starts post-processing."""
    @wraps(finalize_and_post_process)
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
    @wraps(send_robotupload_deposit)
    def _send_robotupload_deposit(obj, eng):
        import os

        from invenio.base.globals import cfg
        from invenio.modules.deposit.models import Deposition
        from invenio.modules.workflows.errors import WorkflowError
        from inspire.utils.robotupload import make_robotupload_marcxml

        callback_url = os.path.join(cfg["CFG_SITE_URL"],
                                    "callback/workflows/robotupload")

        d = Deposition(obj)

        sip = d.get_latest_sip(d.submitted)

        if not sip:
            raise WorkflowError("No sip found", eng.uuid, obj.id)
        if not d.submitted:
            sip.seal()
            d.update()

        marcxml = sip.package

        result = make_robotupload_marcxml(
            url=url,
            marcxml=marcxml,
            callback_url=callback_url,
            mode='insert',
            nonce=obj.id
        )
        if "[INFO]" not in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in "
                              "CFG_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                              "on host")
                obj.log.error(result.text)
            from invenio.modules.workflows.errors import WorkflowError
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise WorkflowError(txt, eng.uuid, obj.id)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
            eng.halt("Waiting for robotupload: {0}".format(result.text))
        obj.log.info("end of upload")

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


def add_note_entry(obj, eng):
    """Add note entry to sip metadata on approval."""
    entry = {'value': '*Temporary entry*'} if obj.extra_data.get("core") \
        else {'value': '*Brief entry*'}
    deposition = Deposition(obj)
    metadata = deposition.get_latest_sip(sealed=False).metadata
    if metadata.get('note', None):
        metadata['note'].append(entry)
    else:
        metadata['note'] = [entry]
    deposition.save()
