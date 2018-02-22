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

"""INSPIRE-HEP ticketing system API."""

from __future__ import absolute_import, division, print_function

import backoff
import rt

from .tickets import create_ticket_with_template


@backoff.on_exception(backoff.expo, rt.ConnectionError, base=4, max_tries=5)
def submit_ticket(obj, queue, template, context, requestors, recid,
                  ticket_id_key):
    """Create a ticket."""
    new_ticket_id = create_ticket_with_template(
        queue,
        requestors,
        template,
        context,
        context.get("subject"),
        recid
    )
    obj.extra_data[ticket_id_key] = new_ticket_id
    obj.log.info(u'Ticket {0} created'.format(new_ticket_id))
    return True
