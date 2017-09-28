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

"""Crossref blueprints."""

from __future__ import absolute_import, division, print_function


from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from idutils import normalize_doi

from .core import get_json


blueprint = Blueprint(
    'inspirehep_crossref',
    __name__,
    url_prefix='/doi',
)


@blueprint.route('/search', methods=['GET'])
@login_required
def search(doi=None):
    provided_doi = doi or request.args.get('doi')
    try:
        normalized_doi = normalize_doi(provided_doi)
        result = get_json(normalized_doi)
    except AttributeError:
        result = {
            'query': {},
            'source': 'inspire',
            'status': 'badrequest',
        }

    resp = jsonify(result)
    resp.status_code = current_app.config['CROSSREF_RESPONSE_CODES'].get(result['status'], 200)
    return resp
