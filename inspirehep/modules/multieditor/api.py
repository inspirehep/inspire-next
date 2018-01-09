# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Module for backend of multi record editor used in http://inspirehep.net."""

from __future__ import absolute_import, print_function, division

from flask import Blueprint, request, jsonify, session, current_app
import copy
import json

from inspire_schemas.api import load_schema
from inspirehep.modules.multieditor import tasks
from inspirehep.modules.migrator.tasks import chunker
from .actions import compare_records
from . import queries
from .permissions import multieditor_use_permission
from .serializers import get_actions
from .exceptions import InvalidValue, SchemaError, InvalidActions

blueprint = Blueprint(
    'inspirehep_multieditor',
    __name__,
    template_folder='templates',
    url_prefix='/multieditor',
)


@blueprint.route("/update", methods=['POST'])
@multieditor_use_permission.require(http_exception=403)
def update():
    """Apply the user actions to the database records."""
    form = json.loads(request.data)
    user_actions = form.get('userActions', {})
    all_selected = form.get('allSelected', False)
    multieditor_session = session.get('multieditor_session', {})
    user_selected_ids = form['ids']
    if multieditor_session:
        ids = multieditor_session['uuids']
        if all_selected:
            ids_to_update = set(ids) - set(user_selected_ids)
        else:
            ids_to_update = set(ids) & set(user_selected_ids)
    else:
        return jsonify({'message': 'Please use the search before you apply actions'}), 400

    try:
        get_actions(user_actions, multieditor_session['schema'])
    except InvalidActions as err:
        return jsonify({'message': err.message}), 400

    for i, chunk in enumerate(chunker(ids_to_update, 200)):
        tasks.process_records.delay(records_ids=chunk, user_actions=user_actions, schema=multieditor_session['schema'])
    return jsonify({'message': 'Records are being updated'})


@blueprint.route("/preview", methods=['POST'])
@multieditor_use_permission.require(http_exception=403)
def preview():
    """Preview the user actions in the first (page size) records."""
    form = json.loads(request.data)
    user_actions = form.get('userActions', {})
    page_size = form.get('pageSize', 10)
    page_number = form.get('pageNum', 1)
    multieditor_session = session.get('multieditor_session', {})

    if not multieditor_session:
        return jsonify({'message': 'Please use the search before you apply actions'}), 400

    uuids, records = queries.get_paginated_records(page_number=page_number,
                                                   page_size=page_size,
                                                   uuids=multieditor_session['uuids'])

    old_records = copy.deepcopy(records)
    try:
        actions = get_actions(user_actions, multieditor_session['schema'])
    except InvalidActions as err:
        return jsonify({'message': err.message}), 400
    for record in records:
        for action in actions:
            try:
                action.process(record, multieditor_session['schema'])
            except (SchemaError, InvalidValue) as err:
                return jsonify({'message': err.message}), 400
    json_patches, errors = compare_records(old_records, records, multieditor_session['schema'])

    return jsonify({'json_records': old_records, 'errors': errors, 'json_patches': json_patches, 'uuids': uuids})


@blueprint.route("/paginate", methods=['GET'])
@multieditor_use_permission.require(http_exception=403)
def paginate():
    """Get paginated records from the session"""
    page_number = int(request.args.get('pageNum', 1))
    page_size = int(request.args.get('pageSize', 10))
    multieditor_session = session.get('multieditor_session', {})
    if not multieditor_session:
        return jsonify({'message': 'Please refresh your page'}), 400
    uuids, records = queries.get_paginated_records(page_number=page_number,
                                                   page_size=page_size, uuids=multieditor_session['uuids'])
    return jsonify({'uuids': uuids, 'json_records': records})


@blueprint.route("/search", methods=['GET'])
@multieditor_use_permission.require(http_exception=403)
def search():
    """Search for records using the query and store the result's ids"""
    query_string = request.args.get('queryString', '')
    page_number = int(request.args.get('pageNum', 1))
    page_size = int(request.args.get('pageSize', 10))
    index_name = request.args.get('index', '')
    schema = load_schema(index_name, resolved=True)
    total_records = queries.get_total_records(query_string, index_name)
    if total_records > current_app.config['MULTI_MAX_RECORDS']:
        return jsonify({'message': 'Please narrow the results using a query to be less than 10000'}), 400
    uuids = queries.get_record_ids_from_query(query_string, index_name)
    session['multieditor_session'] = {
        'uuids': uuids,
        'schema': schema,
    }
    records_uuids, records = queries.get_paginated_records(page_number=page_number,
                                                           page_size=page_size,
                                                           uuids=uuids)
    return jsonify({'total_records': total_records,
                    'uuids': records_uuids,
                    'json_records': records})
