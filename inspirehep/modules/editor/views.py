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

from flask import Blueprint, jsonify, request
from flask_login import current_user

from inspire_schemas.api import ReferenceBuilder

from inspirehep.utils.helpers import force_list

from refextract import (extract_references_from_string,
                        extract_references_from_url)

from .permissions import editor_manage_tickets_permission
from ...utils import tickets


blueprint = Blueprint('inspirehep_editor',
                      __name__,
                      url_prefix='/editor',)


@blueprint.route('/refextract/from_text', methods=['POST'])
def ref_extract_from_text():
    """View to extract references from text"""
    json = request.json
    references = extract_references_from_string(json['text'])
    return jsonify(_build_references(references))


@blueprint.route('/refextract/from_url', methods=['POST'])
def ref_extract_from_url():
    """View to extract references from text"""
    json = request.json
    references = extract_references_from_url(json['url'])
    return jsonify(_build_references(references))


def _build_references(references):
    """Converts ref extract output to referece builder output"""
    # TODO: move it to a utility (duplicate of workflows.tasks.refactract)
    result = []
    for reference in references:
        rb = ReferenceBuilder()
        mapping = [
            ('author', rb.add_refextract_authors_str),
            ('collaboration', rb.add_collaboration),
            ('doi', rb.add_uid),
            ('hdl', rb.add_uid),
            ('isbn', rb.add_uid),
            ('journal_reference', rb.set_pubnote),
            ('linemarker', rb.set_label),
            ('misc', rb.add_misc),
            ('publisher', rb.set_publisher),
            ('raw_ref', rb.add_raw_reference),
            ('reportnumber', rb.add_report_number),
            ('texkey', rb.set_texkey),
            ('title', rb.add_title),
            ('url', rb.add_url),
            ('year', rb.set_year),
        ]

        for field, method in mapping:
            for el in force_list(reference.get(field)):
                if el:
                    method(el)

        result.append(rb.obj)

    return result


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
