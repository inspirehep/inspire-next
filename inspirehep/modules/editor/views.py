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

"""Invenio module for editing JSON records."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, current_app, render_template, request
from flask_login import login_required

from inspirehep.modules.records.utils import get_endpoint_from_record

blueprint = Blueprint(
    'inspirehep_editor',
    __name__,
    url_prefix='/editor',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
@login_required
def index(path):
    """Render base view."""
    return render_template('editor/index.html')


@blueprint.route('/preview', methods=['POST'])
@login_required
def preview():
    """Preview the record being edited."""
    record = request.get_json()
    endpoint = get_endpoint_from_record(record)
    template = current_app.config['RECORDS_UI_ENDPOINTS'][endpoint]['template']
    return render_template(template, record=record)
