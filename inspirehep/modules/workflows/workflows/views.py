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

"""Blueprint for workflows"""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, current_app, jsonify, redirect
from inspirehep.utils.record_getter import get_db_record

from inspirehep.utils.record_getter import RecordGetterError


blueprint = Blueprint('workflow', __name__, url_prefix='/workflow')


@blueprint.route("/")
def root():
    return "Workflow endpoint"


@blueprint.route('/edit_lit/<rec_id>', methods=['GET'])
def edit_workflow(rec_id):
    try:
        record = get_db_record('lit', rec_id)
    except RecordGetterError as err:
        return jsonify(
            status=500,
            message='No record found for control number {}'.format(rec_id)
        )

    # TODO: workflow_object_class.create(data=record, data_type=edit_workflow)
    obj_id = 1
    url = "{}{}".format(current_app.config['WORKFLOWS_EDITOR_API_URL'], obj_id)
    return redirect(location=url, code=302)

