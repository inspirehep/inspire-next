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

from __future__ import absolute_import, print_function

from flask import Blueprint, request, jsonify
from invenio_db import db
from sqlalchemy import text

from . import actions
from ..search.api import LiteratureSearch

blueprint = Blueprint(
    'multiedit',
    __name__,
    url_prefix='/multiedit',
)


@blueprint.route("/multiedit/update", methods=['POST'])
def index():
    """Basic view."""
    user_actions = request.json
    return jsonify(actions.run_user_actions(user_actions))


@blueprint.route("/multiedit/search")
def search():
    """Basic view."""
    records = []
    search = LiteratureSearch()
    results = search.query({'match_all': {}}).scan()
    for result in results:
        records.append(result.to_dict['control_number'])
    return records



    query = text("""
        select json from records_metadata AS r WHERE CAST(r.json->>'control_number' as INT) IN :record_list
    """).bindparams(record_list=records)

    json_records = db.session.execute(query)
    return json_records
