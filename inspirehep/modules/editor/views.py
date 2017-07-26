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

"""INSPIRE editor blueprint."""

from __future__ import absolute_import, division, print_function

from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask_login import current_user

from ...utils import tickets

from .permissions import editor_manage_tickets_permission


blueprint = Blueprint('inspirehep_editor',
                      __name__,
                      url_prefix='/editor',)


@blueprint.route('/rt/tickets/create', methods=['POST'])
@editor_manage_tickets_permission.require(http_exception=403)
def create_rt_ticket():
    """View to create an rt ticket"""
    json = request.json
    ticket_id = tickets.create_ticket(json['queue'],
                                      current_user.email,
                                      json.get('description'),
                                      json.get('subject'),
                                      int(json['recid']),
                                      Owner=json.get('owner'))
    if ticket_id != -1:
        return jsonify(
            success=True,
            data={
                'id': str(ticket_id),
                'link': tickets.get_rt_link_for_ticket(ticket_id)
            }
        )
    else:
        return jsonify(success=False), 500


@blueprint.route('/rt/tickets/<ticket_id>/resolve', methods=['GET'])
@editor_manage_tickets_permission.require(http_exception=403)
def resolve_rt_ticket(ticket_id):
    """View to resolve an rt ticket"""
    tickets.resolve_ticket(ticket_id)
    return jsonify(success=True)


@blueprint.route('/rt/tickets/<recid>', methods=['GET'])
@editor_manage_tickets_permission.require(http_exception=403)
def get_tickets_for_record(recid):
    """View to get rt ticket belongs to given record"""
    tickets_for_record = tickets.get_tickets_by_recid(recid)
    simplified_tickets = map(_simplify_ticket_response, tickets_for_record)
    return jsonify(simplified_tickets)


@blueprint.route('/rt/users', methods=['GET'])
@editor_manage_tickets_permission.require(http_exception=403)
def get_rt_users():
    """View to get all rt users"""

    return jsonify(tickets.get_users())


@blueprint.route('/rt/queues', methods=['GET'])
@editor_manage_tickets_permission.require(http_exception=403)
def get_rt_queues():
    """View to get all rt queues"""

    return jsonify(tickets.get_queues())


def _simplify_ticket_response(ticket):
    return dict(
        id=ticket['Id'],
        queue=ticket['Queue'],
        subject=ticket['Subject'],
        description=ticket['Text'],
        owner=ticket['Owner'],
        date=ticket['Created'],
        link=ticket['Link'])
