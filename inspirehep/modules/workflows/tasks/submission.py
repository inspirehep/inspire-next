# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Contains INSPIRE specific submission tasks."""

from __future__ import absolute_import, division, print_function

import os
import logging
from functools import wraps
from pprint import pformat

from flask import current_app, render_template
from retrying import retry

from invenio_accounts.models import User

from ....utils.tickets import get_instance, retry_if_connection_problems
from .actions import in_production_mode, is_arxiv_paper


LOGGER = logging.getLogger(__name__)


@retry(
    stop_max_attempt_number=5,
    wait_fixed=10000,
    retry_on_exception=retry_if_connection_problems
)
def submit_rt_ticket(obj, queue, subject, body, requestors, ticket_id_key):
    """Submit ticket to RT with the given parameters."""
    rt_instance = get_instance() if in_production_mode() else None
    if not rt_instance:
        obj.log.error("No RT instance available. Skipping!")
        obj.log.info(
            "Was going to submit: {subject}\n\n{body}\n\n"
            "To: {requestors} Queue: {queue}".format(
                queue=queue,
                subject=subject,
                requestors=requestors,
                body=body
            )
        )
        return

    # Trick to prepare ticket body
    body = "\n ".join([line.strip() for line in body.split("\n")])
    rt_queue = current_app.config.get("BIBCATALOG_QUEUES") or queue

    payload = dict(
        Queue=rt_queue,
        Subject=subject,
        Text=body,
    )
    recid = obj.extra_data.get("recid") or obj.data.get("control_number") \
        or obj.data.get("recid")
    if recid:
        payload['CF_RecordID'] = recid

    # Check if requests is set and also ignore admin due to RT mail loop
    if requestors and "admin@inspirehep.net" not in requestors:
        payload['requestors'] = requestors

    ticket_id = rt_instance.create_ticket(**payload)

    obj.extra_data[ticket_id_key] = ticket_id
    obj.log.info("Ticket {0} created:\n{1}".format(
        ticket_id,
        body.encode("utf-8", "ignore")
    ))
    return True


def create_ticket(template,
                  context_factory=None,
                  queue="Test",
                  ticket_id_key="ticket_id"):
    """Create a ticket for the submission.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key.
    """

    @wraps(create_ticket)
    def _create_ticket(obj, eng):
        user = User.query.get(obj.id_user)
        if not user:
            obj.log.error(
                "No user found for object {0}, skipping ticket creation".format(
                    obj.id))
            return
        context = {}
        if context_factory:
            context = context_factory(user, obj)
        body = render_template(
            template,
            **context
        ).strip()

        submit_rt_ticket(obj,
                         queue,
                         context.get('subject'),
                         body,
                         user.email,
                         ticket_id_key)

    return _create_ticket


def reply_ticket(template=None,
                 context_factory=None,
                 keep_new=False):
    """Reply to a ticket for the submission."""

    @wraps(reply_ticket)
    def _reply_ticket(obj, eng):
        from inspirehep.utils.tickets import get_instance

        ticket_id = obj.extra_data.get("ticket_id", "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        user = User.query.get(obj.id_user)
        if not user:
            obj.log.error(
                "No user found for object {0}, skipping ticket creation".format(
                    obj.id))
            return

        if template:
            context = {}
            if context_factory:
                context = context_factory(user, obj)
            body = render_template(
                template,
                **context
            )
        else:
            # Body already rendered in reason.
            body = obj.extra_data.get("reason").strip()
        if not body:
            obj.log.error("No body for ticket reply. Skipping reply.")
            return

        # Trick to prepare ticket body
        body = "\n ".join([line.strip() for line in body.strip().split("\n")])

        rt = get_instance()
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
            obj.log.info(
                "Was going to reply to {ticket_id}\n\n{body}\n\n".format(
                    ticket_id=ticket_id,
                    body=body,
                )
            )
            return

        rt.reply(
            ticket_id=ticket_id,
            text=body,
        )

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
        from inspirehep.utils.tickets import get_instance

        ticket_id = obj.extra_data.get(ticket_id_key, "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        rt = get_instance()
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
            obj.log.info(
                "Was going to close ticket {ticket_id}".format(
                    ticket_id=ticket_id,
                )
            )
            return

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


def send_and_wait_robotupload(
    url=None,
    marcxml_processor=None,
    callback_url="callback/workflows/robotupload",
    mode="insert",
    extra_data_key=None
):
    """Get the MARCXML from the model and ship it."""

    @wraps(send_and_wait_robotupload)
    def _send_robotupload(obj, eng):
        from inspirehep.dojson.utils import legacy_export_as_marc
        from inspirehep.utils.robotupload import make_robotupload_marcxml

        combined_callback_url = os.path.join(
            current_app.config["SERVER_NAME"],
            callback_url
        )
        if not combined_callback_url.startswith('http'):
            combined_callback_url = "https://{0}".format(
                combined_callback_url
            )

        if extra_data_key is not None:
            data = obj.extra_data.get(extra_data_key) or {}
        else:
            data = obj.data
        marc_json = marcxml_processor.do(data)
        marcxml = legacy_export_as_marc(marc_json)

        if current_app.debug:
            # Log what we are sending
            LOGGER.debug(
                "Going to robotupload mode:%s to url:%s:\n%s\n",
                mode,
                url,
                marcxml,
            )

        if not in_production_mode():
            obj.log.debug(
                "Going to robotupload %s to %s:\n%s\n",
                mode,
                url,
                marcxml,
            )
            obj.log.debug(
                "Base object data:\n%s",
                pformat(data)
            )
            return

        result = make_robotupload_marcxml(
            url=url,
            marcxml=marcxml,
            callback_url=combined_callback_url,
            mode=mode,
            nonce=obj.id,
            priority=5,
        )
        if "[INFO]" not in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in "
                              "app.config_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                              "on host")
                obj.log.error(result.text)
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise Exception(txt)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
            eng.halt("Waiting for robotupload: {0}".format(result.text))

        obj.log.info("end of upload")

    return _send_robotupload


def wait_webcoll(obj, eng):
    if not in_production_mode():
        obj.log.debug("Would have wait for webcoll callback.")
        return

    eng.halt("Waiting for webcoll.")


def add_note_entry(obj, eng):
    """Add note entry to metadata on approval."""
    def _has_note(reference_note, notes):
        return any(reference_note == note for note in notes)

    entry = {'value': '*Temporary entry*'} if obj.extra_data.get("core") \
        else {'value': '*Brief entry*'}
    if obj.data.get('public_notes') is None or \
            not isinstance(obj.data.get("public_notes"), list):
        obj.data['public_notes'] = [entry]
    else:
        if not _has_note(entry, obj.data['public_notes']):
            obj.data['public_notes'].append(entry)


def filter_keywords(obj, eng):
    """Removes non-accepted keywords from the metadata"""
    prediction = obj.extra_data.get('keywords_prediction', {})
    if prediction:
        keywords = prediction.get('keywords')

        keywords = filter(lambda x: x['accept'], keywords)
        obj.extra_data['keywords_prediction']['keywords'] = keywords

        obj.log.debug('Filtered keywords: \n%s', pformat(keywords))

    obj.log.debug('Got no prediction for keywords')


def prepare_keywords(obj, eng):
    """Prepares the keywords in the correct format to be sent"""
    prediction = obj.extra_data.get('keywords_prediction', {})
    if not prediction:
        return

    keywords = obj.data.get('keywords', [])
    for keyword in prediction.get('keywords', []):
        # TODO: differentiate between curated and gueesed keywords
        keywords.append(
            {
                'value': keyword['label'],
                'source': 'curator' if keyword.get('curated') else 'magpie',
            }
        )

    obj.data['keywords'] = keywords

    obj.log.debug('Finally got keywords: \n%s', pformat(keywords))


def user_pdf_get(obj, eng):
    """Upload user PDF file, if requested."""
    if obj.extra_data.get('pdf_upload', False):
        fft = {'path': obj.extra_data.get('submission_pdf'),
               'type': 'INSPIRE-PUBLIC'}
        if obj.data.get('_fft'):
            obj.data['_fft'].append(fft)
        else:
            obj.data['_fft'] = [fft]
        obj.log.info("User PDF file added to FFT.")


def prepare_files(obj, eng):
    """Adds to the _fft field (files) the extracted pdfs if any"""
    def _get_fft(url, name):
        def _get_filename(obj, filename):
            if is_arxiv_paper(obj):
                return 'arxiv:' + filename

            return filename

        filename, filetype = os.path.splitext(name)

        return {
            'path': os.path.realpath(url),
            'type': is_arxiv_paper(obj) and 'arXiv' or 'INSPIRE-PUBLIC',
            'filename': _get_filename(obj, filename),
            'format': filetype,
        }

    if not obj.files:
        return

    pdf_file_objs = []
    for key in obj.files.keys:
        if key.endswith('.pdf'):
            pdf_file_objs.append((key, obj.files[key]))

    result = []
    for filename, pdf_file_obj in pdf_file_objs:
        if pdf_file_obj:
            result.append(_get_fft(pdf_file_obj.obj.file.uri, filename))

    if result:
        obj.data['_fft'] = obj.data.get('_fft', []) + result
        obj.log.info('Non-user PDF files added to FFT.')
        obj.log.debug('Added PDF files: {}'.format(result))


def remove_references(obj, eng):
    obj.log.info(obj.data)
    if 'references' in obj.data:
        del obj.data['references']
