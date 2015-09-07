# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Contains INSPIRE specific submission tasks"""

import os

from functools import wraps
from flask import render_template
from flask_login import current_user

from invenio.base.globals import cfg
from invenio_deposit.models import Deposition
from invenio_formatter import format_record

from retrying import retry


def halt_to_render(obj, eng):
    """Halt the workflow - waiting to be resumed."""
    deposition = Deposition(obj)
    sip = deposition.get_latest_sip(sealed=False)
    deposition.set_render_context(dict(
        template_name_or_list="deposit/completed.html",
        deposition=deposition,
        deposition_type=(
            None if deposition.type.is_default() else
            deposition.type.get_identifier()
        ),
        uuid=deposition.id,
        sip=sip,
        my_depositions=Deposition.get_depositions(
            current_user, type=deposition.type
        ),
        format_record=format_record,
    ))
    obj.last_task = "halt_to_render"
    eng.halt("User submission complete.")


def get_ticket_body(template, deposition, metadata, email, obj):
    """
    Get ticket content.

    Ticket used by the curator to get notified about the new submission.
    """
    subject = ''.join(["Your suggestion to INSPIRE: ", deposition.title])
    user_comment = obj.extra_data.get('submission_data').get('extra_comments')
    body = render_template(
        template,
        email=email,
        title=deposition.title,
        identifier=metadata.get("system_number_external", {}).get("value", ""),
        user_comment=user_comment,
        references=obj.extra_data.get("submission_data", {}).get("references"),
        object=obj,
    ).strip()

    return subject, body


def get_curation_body(template, metadata, email, extra_data):
    """
    Get ticket content.

    Ticket used by curators to curate the given record.
    """
    from invenio.utils.persistentid import is_arxiv_post_2007

    recid = extra_data.get('recid')
    record_url = extra_data.get('url')

    arxiv_id = metadata.get('arxiv_id')
    if arxiv_id and is_arxiv_post_2007(arxiv_id):
        arxiv_id = ''.join(['arXiv:', arxiv_id])

    report_number = metadata.get('report_number')
    if report_number:
        report_number = report_number[0].get('primary')

    link_to_pdf = extra_data.get('submission_data').get('pdf')

    subject = ' '.join(filter(lambda x: x is not None,
                       [arxiv_id,
                        metadata.get('doi'),
                        report_number,
                        '(#{0})'.format(recid)]))

    references = extra_data.get('submission_data').get('references')
    user_comment = extra_data.get('submission_data').get('extra_comments')

    body = render_template(
        template,
        recid=recid,
        record_url=record_url,
        link_to_pdf=link_to_pdf,
        email=email,
        references=references,
        user_comment=user_comment,
    ).strip()

    return subject, body


@retry(stop_max_attempt_number=5, wait_fixed=10000)
def submit_rt_ticket(obj, queue, subject, body, requestors, ticket_id_key):
    """Submit ticket to RT with the given parameters."""
    from inspire.utils.tickets import get_instance

    # Trick to prepare ticket body
    body = "\n ".join([line.strip() for line in body.split("\n")])
    rt_instance = get_instance() if cfg.get("PRODUCTION_MODE") else None
    rt_queue = cfg.get("CFG_BIBCATALOG_QUEUES") or queue
    recid = obj.extra_data.get("recid", "")
    if not recid:
        recid = obj.data.get("recid", "")
    if not rt_instance:
        obj.log.error("No RT instance available. Skipping!")
        obj.log.info("Ticket submission ignored.")
    else:
        ticket_id = rt_instance.create_ticket(
            Queue=rt_queue,
            Subject=subject,
            Text=body,
            Requestors=requestors,
            CF_RecordID=recid
        )
        obj.extra_data[ticket_id_key] = ticket_id
        obj.log.info("Ticket {0} created:\n{1}".format(
            ticket_id,
            body.encode("utf-8", "ignore")
        ))
    return True


def create_curation_ticket(template, queue="Test", ticket_id_key="ticket_id"):
    """Create a ticket for curation.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key."""
    @wraps(create_ticket)
    def _create_curation_ticket(obj, eng):
        from invenio.modules.access.control import acc_get_user_email

        deposition = Deposition(obj)
        requestors = acc_get_user_email(obj.id_user)
        metadata = deposition.get_latest_sip(sealed=True).metadata

        if obj.extra_data.get("core"):
            subject, body = get_curation_body(template,
                                              metadata,
                                              requestors,
                                              obj.extra_data)
            submit_rt_ticket(obj,
                             queue,
                             subject,
                             body,
                             requestors,
                             ticket_id_key)
    return _create_curation_ticket


def create_ticket(template, queue="Test", ticket_id_key="ticket_id"):
    """Create a ticket for the submission.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key."""
    @wraps(create_ticket)
    def _create_ticket(obj, eng):
        from invenio.modules.access.control import acc_get_user_email

        deposition = Deposition(obj)
        requestors = acc_get_user_email(obj.id_user)

        subject, body = get_ticket_body(template,
                                        deposition,
                                        deposition.get_latest_sip(sealed=True).metadata,
                                        requestors,
                                        obj)
        submit_rt_ticket(obj,
                         queue,
                         subject,
                         body,
                         requestors,
                         ticket_id_key)
    return _create_ticket


def reply_ticket(template=None, keep_new=False):
    """Reply to a ticket for the submission."""
    @wraps(reply_ticket)
    def _reply_ticket(obj, eng):
        from invenio_accounts.models import User
        from invenio_workflows.errors import WorkflowError
        from inspire.utils.tickets import get_instance

        ticket_id = obj.extra_data.get("ticket_id", "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        if template:
            # Body rendered by template.
            deposition = Deposition(obj)
            user = User.query.get(obj.id_user)

            context = {
                "object": obj,
                "user": user,
                "title": deposition.title,
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
            raise WorkflowError("No body for ticket reply", eng.uuid, obj.id)
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
            try:
                rt.edit_ticket(
                    ticket_id=ticket_id,
                    Status="resolved"
                )
            except IndexError:
                # Probably already resolved, lets check
                ticket = rt.get_ticket(ticket_id)
                if ticket["Status"] != "resolved":
                    raise
                obj.log.warning("Ticket is already resolved.")
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
        from invenio_workflows.api import start_delayed
        from invenio_workflows.models import ObjectVersion

        obj.version = ObjectVersion.FINAL
        workflow_id = start_delayed(workflow_name,
                                    data=[obj],
                                    stop_on_error=True,
                                    **kwargs)
        obj.log.info("Started new workflow ({0})".format(workflow_id))
    return _finalize_and_post_process


def send_robotupload(url=None,
                     callback_url="callback/workflows/continue",
                     mode="insert"):
    """Get the MARCXML from the model and ship it."""
    @wraps(send_robotupload)
    def _send_robotupload(obj, eng):
        from invenio_workflows.errors import WorkflowError
        from inspire.utils.robotupload import make_robotupload_marcxml

        combined_callback_url = os.path.join(cfg["CFG_SITE_URL"], callback_url)
        model = eng.workflow_definition.model(obj)
        sip = model.get_latest_sip()
        marcxml = sip.package
        result = make_robotupload_marcxml(
            url=url,
            marcxml=marcxml,
            callback_url=combined_callback_url,
            mode=mode,
            nonce=obj.id
        )
        if "[INFO]" not in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in "
                              "CFG_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                              "on host")
                obj.log.error(result.text)
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise WorkflowError(txt, eng.uuid, obj.id)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
            eng.halt("Waiting for robotupload: {0}".format(result.text))
        obj.log.info("end of upload")
    return _send_robotupload


def add_files_to_task_results(obj, eng):
    """Add Deposition attached files to task results."""
    deposition = Deposition(obj)
    for file_obj in deposition.files:
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
    metadata = deposition.get_latest_sip(sealed=True).metadata
    if metadata.get('note') is None or not isinstance(metadata.get("note"), list):
        metadata['note'] = [entry]
    else:
        metadata['note'].append(entry)
    deposition.update()


def user_pdf_get(obj, eng):
    """Upload user PDF file, if requested."""
    if obj.extra_data.get('pdf_upload', False):
        fft = {'url': obj.extra_data.get('submission_data').get('pdf'),
               'docfile_type': 'INSPIRE-PUBLIC'}
        deposition = Deposition(obj)
        metadata = deposition.get_latest_sip(sealed=True).metadata
        if metadata.get('fft'):
            metadata['fft'].append(fft)
        else:
            metadata['fft'] = [fft]
        deposition.update()
        obj.log.info("PDF file added to FFT.")


def finalize_record_sip(processor):
    """Finalize the SIP by generating the MARC and storing it in the SIP."""
    @wraps(finalize_record_sip)
    def _finalize_sip(obj, eng):
        from inspire.dojson.utils import legacy_export_as_marc
        model = eng.workflow_definition.model(obj)
        sip = model.get_latest_sip()
        sip.package = legacy_export_as_marc(processor.do(sip.metadata))
        model.update()
    return _finalize_sip
