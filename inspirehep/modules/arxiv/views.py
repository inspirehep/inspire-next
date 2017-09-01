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

"""ArXiv blueprints."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from .core import get_json


blueprint = Blueprint(
    'inspirehep_arxiv',
    __name__,
    url_prefix='/arxiv',
)


@blueprint.route('/search', methods=['GET'])
@login_required
def search(arxiv=None):
    arxiv = arxiv or request.args.get("arxiv")

    result = get_json(arxiv)

    resp = jsonify(result)
    resp.status_code = current_app.config['ARXIV_RESPONSE_CODES'].get(result['status'], 200)
    return resp
