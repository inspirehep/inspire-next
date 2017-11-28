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

"""Editor views."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy_continuum import transaction_class, version_class

from invenio_db import db
from invenio_records.models import RecordMetadata

from inspirehep.modules.pidstore.utils import get_pid_type_from_endpoint
from inspirehep.modules.tools import authorlist
from inspirehep.modules.workflows.workflows.manual_merge import start_merger
from inspirehep.utils.record_getter import get_db_record
from inspirehep.utils.references import (
    get_refextract_kbs_path,
    map_refextract_to_schema,
)
from refextract import (
    extract_references_from_string,
    extract_references_from_url,
)

from .permissions import editor_permission, editor_use_api_permission
from ...utils import tickets


blueprint = Blueprint(
    'inspirehep_editor',
    __name__,
    url_prefix='/editor',
)


@blueprint.route('/<endpoint>/<pid_value>/permission', methods=['GET'])
@editor_permission
def check_permission(endpoint, pid_value):
    """Check if logged in user has permission to open the given record.

    Used by record-editor on startup.
    """
    return jsonify(success=True)


@blueprint.route('/authorlist/text', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def authorlist_text():
    """Run authorlist on a piece of text."""
    try:
        parsed_authors = authorlist(request.json['text'])
        return jsonify(parsed_authors)
    except Exception as err:
        return jsonify(status=500, message=u' / '.join(err.args)), 500


@blueprint.route('/refextract/text', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def refextract_text():
    """Run refextract on a piece of text."""
    extracted_references = extract_references_from_string(
        request.json['text'],
        override_kbs_files=get_refextract_kbs_path(),
        reference_format=u'{title},{volume},{page}'
    )
    references = map_refextract_to_schema(extracted_references)

    return jsonify(references)


@blueprint.route('/refextract/url', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def refextract_url():
    """Run refextract on a URL."""
    extracted_references = extract_references_from_url(
        request.json['url'],
        override_kbs_files=get_refextract_kbs_path(),
        reference_format=u'{title},{volume},{page}'
    )
    references = map_refextract_to_schema(extracted_references)

    return jsonify(references)


@blueprint.route('/<endpoint>/<int:pid_value>/revisions/revert', methods=['PUT'])
@editor_permission
def revert_to_revision(endpoint, pid_value):
    """Revert given record to given revision"""
    pid_type = get_pid_type_from_endpoint(endpoint)
    record = get_db_record(pid_type, pid_value)
    revision_id = request.json['revision_id']
    record.revert(revision_id)
    db.session.commit()
    return jsonify(success=True)


@blueprint.route('/<endpoint>/<int:pid_value>/revisions', methods=['GET'])
@editor_permission
def get_revisions(endpoint, pid_value):
    """Get revisions of given record"""
    Transaction = transaction_class(RecordMetadata)
    pid_type = get_pid_type_from_endpoint(endpoint)
    record = get_db_record(pid_type, pid_value)

    revisions = []
    for revision in reversed(record.revisions):
        transaction_id = revision.model.transaction_id

        user = Transaction.query.filter(
            Transaction.id == transaction_id).one().user
        if user:
            user_email = user.email
        else:
            user_email = 'system'

        revisions.append({
            'updated': revision.updated,
            'revision_id': revision.revision_id,
            'user_email': user_email,
            'transaction_id': transaction_id,
            'rec_uuid': record.id
        })
    return jsonify(revisions)


@blueprint.route('/<endpoint>/<int:pid_value>/revision/<rec_uuid>/<int:transaction_id>', methods=['GET'])
@editor_permission
def get_revision(endpoint, pid_value, transaction_id, rec_uuid):
    """Get the revision of given record (uuid)"""
    RecordMetadataVersion = version_class(RecordMetadata)

    revision = RecordMetadataVersion.query.with_entities(
        RecordMetadataVersion.json
    ).filter(
        RecordMetadataVersion.transaction_id == transaction_id,
        RecordMetadataVersion.id == rec_uuid
    ).one()

    return jsonify(revision.json)


@blueprint.route('/<endpoint>/<int:pid_value>/rt/tickets/create', methods=['POST'])
@editor_permission
def create_rt_ticket(endpoint, pid_value):
    """View to create an rt ticket"""
    json = request.json
    ticket_id = tickets.create_ticket(json['queue'],
                                      current_user.email,
                                      json.get('description'),
                                      json.get('subject'),
                                      pid_value,
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


@blueprint.route('/<endpoint>/<pid_value>/rt/tickets/<ticket_id>/resolve', methods=['GET'])
@editor_permission
def resolve_rt_ticket(endpoint, pid_value, ticket_id):
    """View to resolve an rt ticket"""
    tickets.resolve_ticket(ticket_id)
    return jsonify(success=True)


@blueprint.route('/<endpoint>/<pid_value>/rt/tickets', methods=['GET'])
@editor_permission
def get_tickets_for_record(endpoint, pid_value):
    """View to get rt ticket belongs to given record"""
    tickets_for_record = tickets.get_tickets_by_recid(pid_value)
    simplified_tickets = map(_simplify_ticket_response, tickets_for_record)
    return jsonify(simplified_tickets)


@blueprint.route('/rt/users', methods=['GET'])
@editor_use_api_permission.require(http_exception=403)
def get_rt_users():
    """View to get all rt users"""

    return jsonify(tickets.get_users())


@blueprint.route('/rt/queues', methods=['GET'])
@editor_use_api_permission.require(http_exception=403)
def get_rt_queues():
    """View to get all rt queues"""

    return jsonify(tickets.get_queues())


@blueprint.route('/manual_merge', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def start_manual_merge():
    """Initiate manual merge on two records."""
    assert request.json['head_recid']
    assert request.json['update_recid']

    workflow_id = start_merger(request.json['head_recid'], request.json['update_recid'], current_user.get_id())
    return jsonify(workflow_object_id=workflow_id)


def _simplify_ticket_response(ticket):
    return dict(
        id=ticket['Id'],
        queue=ticket['Queue'],
        subject=ticket['Subject'],
        description=ticket['Text'],
        owner=ticket['Owner'],
        date=ticket['Created'],
        link=ticket['Link'])
