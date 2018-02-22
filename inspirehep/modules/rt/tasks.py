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

"""INSPIRE-HEP ticketing system tasks."""

from __future__ import absolute_import, division, print_function

from functools import wraps

from flask import current_app
from invenio_accounts.models import User

from .api import submit_ticket
from .proxies import rt_instance
from .tickets import reply_ticket as _reply_tickets_ticket, \
    reply_ticket_with_template, resolve_ticket


def create_ticket(template, context_factory=None, queue="Test",
                  ticket_id_key="ticket_id"):
    """Create a ticket for the submission.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key.
    """
    @wraps(create_ticket)
    def _create_ticket(obj, eng):
        user = User.query.get(obj.id_user)

        context = {}
        if context_factory:
            context = context_factory(user, obj)

        if not current_app.config.get("PRODUCTION_MODE", False):
            obj.log.info(
                u'Was going to create ticket: {subject}\n'
                u'To: {requestors} Queue: {queue}'.format(
                    queue=queue,
                    subject=context.get('subject'),
                    requestors=user.email if user else '',
                )
            )
            return

        recid = obj.extra_data.get("recid") or obj.data.get("control_number")

        submit_ticket(obj, queue, template, context,
                      user.email if user else '', recid, ticket_id_key)

    return _create_ticket


def reply_ticket(template=None, context_factory=None, keep_new=False):
    """Reply to a ticket for the submission."""
    @wraps(reply_ticket)
    def _reply_ticket(obj, eng):
        ticket_id = obj.extra_data.get("ticket_id", "")
        if not rt_instance:
            obj.log.error("No RT instance available. Skipping!")
            obj.log.info(
                "Was going to reply to {ticket_id}\n".format(
                    ticket_id=ticket_id,
                )
            )
            return

        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        user = User.query.get(obj.id_user)
        if not user:
            obj.log.error(
                "No user found for object %s, skipping ticket creation",
                obj.id
            )
            return

        if template:
            context = {}
            if context_factory:
                context = context_factory(user, obj)
            reply_ticket_with_template(ticket_id, template, context, keep_new)
        else:
            # Body already rendered in reason.
            body = obj.extra_data.get("reason", "")
            if body:
                _reply_tickets_ticket(ticket_id, body, keep_new)
            else:
                obj.log.error("No body for ticket reply. Skipping reply.")
                return

    return _reply_ticket


def close_ticket(ticket_id_key="ticket_id"):
    """Close the ticket associated with this record found in given key."""
    @wraps(close_ticket)
    def _close_ticket(obj, eng):
        ticket_id = obj.extra_data.get(ticket_id_key, "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        if not rt_instance:
            obj.log.error("No RT instance available. Skipping!")
            obj.log.info(
                "Was going to close ticket {ticket_id}".format(
                    ticket_id=ticket_id,
                )
            )
            return

        resolve_ticket(ticket_id)

    return _close_ticket
