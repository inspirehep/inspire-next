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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Contains INSPIRE specific submission tasks"""

from retrying import retry

from flask import current_app


@retry(stop_max_attempt_number=5, wait_fixed=10000)
def submit_rt_ticket(obj, queue, subject, body, requestors, ticket_id_key):
    """Submit ticket to RT with the given parameters."""
    from inspirehep.utils.tickets import get_instance

    # Trick to prepare ticket body
    body = "\n ".join([line.strip() for line in body.split("\n")])
    rt_instance = get_instance() if current_app.config.get("PRODUCTION_MODE") else None
    rt_queue = current_app.config.get("CFG_BIBCATALOG_QUEUES") or queue
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
