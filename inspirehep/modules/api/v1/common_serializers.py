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

"""Common (to all collections) API of INSPIRE."""

from __future__ import absolute_import, division, print_function

import json

from invenio_records_rest.serializers.response import search_responsify


class APIRecidsSerializer(object):
    """Recids serializer."""

    def serialize_search(self, pid_fetcher, search_result, item_links_factory=None, links=None):
        return json.dumps(dict(
            hits=dict(
                recids=[record['_source']['control_number'] for record in search_result['hits']['hits']],
                total=search_result['hits']['total'],
            ),
            links=links or {},
        ))


json_recids = APIRecidsSerializer()
json_recids_response = search_responsify(
    json_recids,
    'application/vnd+inspire.ids+json'
)
