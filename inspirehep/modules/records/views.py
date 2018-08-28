# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

"""Data model package."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, request, abort
from inspirehep.modules.records.api import InspireRecord
from invenio_rest.views import ContentNegotiatedMethodView
from invenio_records_rest.views import pass_record

from .serializers import json_literature_citations_v1_response

blueprint = Blueprint(
    'inspirehep_records',
    __name__,
    url_prefix='/literature',
)


class LiteratureCitationsResource(ContentNegotiatedMethodView):

    view_name = 'literature_citations'

    def __init__(self, **kwargs):
        super(LiteratureCitationsResource, self).__init__(
            serializers={
                'application/json': json_literature_citations_v1_response
            },
            default_method_media_type={
                'GET': 'application/json',
            },
            default_media_type='application/json',
            **kwargs)

    @pass_record
    def get(self, pid, record):
        page = request.values.get('page', 1, type=int)
        size = request.values.get('size', 10, type=int)

        if page < 1 or size < 1:
            abort(400)

        citing_records_results = record.get_citing_records_query.paginate(
            page, size, False)
        citing_records_count = citing_records_results.total
        citing_records_uuids = [result[0] for result in citing_records_results.items]
        citing_records = InspireRecord.get_records(citing_records_uuids)
        data = {'citations': citing_records,
                'citation_count': citing_records_count}
        return self.make_response(pid, data)


literature_citations_view = LiteratureCitationsResource.as_view(
    LiteratureCitationsResource.view_name,
)

blueprint.add_url_rule(
    '/<pid(lit,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citations',
    view_func=literature_citations_view
)
