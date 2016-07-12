# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

from __future__ import absolute_import, division, print_function

import json

from collections import Counter

from flask import Blueprint, session, request, render_template

from inspirehep.modules.records.serializers.json_literature import process_es_hit

from .utils import assign_profile

# from inspirehep.modules.pidstore.fetchers import inspire_recid_fetcher as pid_fetcher
# from inspirehep.modules.records.serializers import JSONBriefSerializer
# from inspirehep.modules.records.serializers.schemas.json import RecordSchemaJSONBRIEFV1
blueprint = Blueprint(
    'inspire_oauthclient',
    __name__,
    url_prefix="/oauth",
    static_folder="static",
    template_folder="templates",
)


@blueprint.route('/signup/orcid/match_profile', methods=['GET'])
def match():
    """"""
    return render_template('match_profile.html')


@blueprint.route('/signup/orcid/get_matches', methods=['POST'])
def get_matches():
    """"""
    profiles = request.json
    if profiles:
        most_common, _ = Counter(profiles).most_common(1)[0]
        assign_profile(most_common)
    return 'OK'


@blueprint.route('/signup/orcid/match_data', methods=['GET'])
def match_data():
    """Extra signup step."""
    try:
        data = session['oauth_possible_profiles']

        records = [x for y, z in data.items() for x in z]

        response = dict(
            hits=dict(
                hits=[{'metadata': process_es_hit(
                    hit['_source']),
                    'id': hit['_source']['control_number']} for hit in records]
            )
        )
    except KeyError:
        response = {
            "hits": {
                "hits": [],
                "total": 0
            },
            "links": {
                "self": ""
            }
        }

    return json.dumps(response)
