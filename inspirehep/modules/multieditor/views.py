# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""Module for backend of multieditor used in http://inspirehep.net."""

from __future__ import absolute_import, print_function, division

from flask import Blueprint, request, jsonify, session, current_app, abort
from flask.views import MethodView
import copy
import json

from inspire_schemas.api import load_schema
from inspirehep.modules.multieditor import tasks
from inspirehep.modules.migrator.tasks import chunker

from .utils import compare_records, match_records
from . import queries
from .permissions import multieditor_use_permission
from .serializers import get_actions
from .errors import InvalidValue, SchemaError, InvalidActions

blueprint = Blueprint(
    'inspirehep_multieditor',
    __name__,
    url_prefix='/multieditor',
)


class UpdateAPI(MethodView):
    """The update api is used for editing the records with the provided actions and
     depositing them to the database."""
    decorators = [multieditor_use_permission.require(http_exception=403)]

    def post(self):
        """Apply the user actions to the searched records and deposit the changed records to the database."""
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
            abort(401)

        try:
            get_actions(user_actions, multieditor_session['schema'])
        except InvalidActions as err:
            return jsonify({'message': err.message}), 400

        for i, chunk in enumerate(chunker(ids_to_update, 200)):
            tasks.process_records.delay(records_ids=chunk, user_actions=user_actions, schema=multieditor_session['schema'])
        return jsonify({'message': 'Records are being updated'})


update_api = UpdateAPI.as_view('update_api')
blueprint.add_url_rule('/update', view_func=update_api, methods=['POST'])


class SearchAPI(MethodView):
    """The search api is used to provide the user with the records that
    correspond to her query."""
    decorators = [multieditor_use_permission.require(http_exception=403)]

    def get(self):
        """Search for records using the provided query and store the result's ids,
        or paginate through the allready searched records."""
        query = request.args.get('q', '', type=str)
        page = int(request.args.get('page', 1, type=int))
        size = int(request.args.get('size', 10, type=int))
        if request.args.get('q') is not None:
            index_name = request.args.get('index', '')
            schema = load_schema(index_name, resolved=True)
            total_records = queries.get_total_records(query, index_name)
            if total_records > current_app.config['MULTI_MAX_RECORDS']:
                return jsonify({'message': 'Please narrow the results using a query to be less than 10000'}), 400
            uuids = queries.get_record_ids_from_query(query, index_name)
            session['multieditor_session'] = {
                'uuids': uuids,
                'schema': schema,
            }
        else:
            uuids, records, schema = check_session_and_get_paginated_records(page, size)
            total_records = None
        records_uuids, records = queries.get_paginated_records(page=page,
                                                               size=size,
                                                               uuids=uuids)
        return jsonify({'total_records': total_records,
                        'uuids': records_uuids,
                        'json_records': records})
    
    def post(self):
        """Preview the user actions in the corresponding page's records,
        returning the old records with JSON patches for the changed ones."""
        form = json.loads(request.data)
        user_actions = form.get('userActions', {})
        size = form.get('size', 10)
        page = form.get('page', 1)
        uuids, records, schema = check_session_and_get_paginated_records(page, size)

        old_records = copy.deepcopy(records)
        try:
            actions = get_actions(user_actions, schema)
        except InvalidActions as err:
            return jsonify({'message': err.message}), 400
        for record in records:
            for action in actions:
                try:
                    action.process(record, schema)
                except (SchemaError, InvalidValue) as err:
                    return jsonify({'message': err.message}), 400
        json_patches, errors = compare_records(old_records, records, schema)
        if not form.get('page'):
            multieditor_session = session.get('multieditor_session', {})
            if not multieditor_session:
                abort(401)
            affected_records = match_records(multieditor_session['uuids'], actions, schema)
        else:
            affected_records = None
        return jsonify({'json_records': old_records, 'errors': errors, 'json_patches': json_patches, 'uuids': uuids,
                        'affected_records': affected_records})


search_api = SearchAPI.as_view('search_api')
blueprint.add_url_rule('/search', view_func=search_api, methods=['GET', 'POST'])


def check_session_and_get_paginated_records(page, size):
    multieditor_session = session.get('multieditor_session', {})
    if not multieditor_session:
        abort(401)
    uuids, records = queries.get_paginated_records(page=page, size=size, uuids=multieditor_session['uuids'])
    schema = multieditor_session['schema']
    return uuids, records,  schema


@blueprint.errorhandler(401)
def expired_session():
    return jsonify({'message': 'Please use the search before you apply actions'}), 401
