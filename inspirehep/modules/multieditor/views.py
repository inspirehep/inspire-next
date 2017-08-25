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

from flask import Blueprint, request, jsonify
from invenio_db import db
from sqlalchemy import text

from . import actions
from ..search.api import LiteratureSearch


blueprint = Blueprint(
    'inspirehep_multieditor',
    __name__,
    url_prefix='/multieditor',
)


@blueprint.route("/update", methods=['POST'])
def index():
    """Basic view."""
    user_actions = request.json
    return jsonify(actions.run_user_actions(user_actions))


@blueprint.route("/search")
def search():
    """Basic view."""
    records = []
    json_records = []
    query_string = request.args.get("query_string")
    page_num = int(request.args.get("page_num"))
    #  find record ids from elastic search
    query_result = LiteratureSearch().query_from_iq(query_string).params(size=10,
                                                                         from_=((page_num-1)*10),
                                                                         _source=['control_number']).execute()
    total_records = query_result.to_dict()['hits']['total']
    query_records = query_result.hits
    for result in query_records:
        records.append(result.to_dict()['control_number'])
    #  fetch records from database

    if records:
        records = tuple(records)
        query = text("""
            select json from records_metadata AS r WHERE CAST(r.json->>'control_number' as INT) IN :record_list
        """).bindparams(record_list=records)
        db_records = db.session.execute(query)

        for record in db_records:
            json_records.append(record[0])

    json_for_view = {'json_records': json_records, 'total_records': total_records}
    return jsonify(json_for_view)
