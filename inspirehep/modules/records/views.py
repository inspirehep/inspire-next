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

from functools import partial

from flask import Blueprint, request, abort
from invenio_rest.views import ContentNegotiatedMethodView
from invenio_records_rest.views import pass_record

from inspirehep.modules.search import LiteratureSearch
from inspirehep.modules.search.search_factory import inspire_facets_factory
from .serializers import json_literature_citations_v1_response, \
    json_literature_search_aggregations_ui_v1
from inspirehep.modules.records.utils import get_citations_from_es

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

        citing_records_results = get_citations_from_es(record, page, size)
        citing_records_count = citing_records_results.total
        citing_records = [citation.to_dict() for citation in citing_records_results]

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


class Facets(ContentNegotiatedMethodView):
    view_name = '{0}_facets'

    def __init__(self, **kwargs):
        search_factory = kwargs.pop('search_factory', inspire_facets_factory)
        self.search_factory = partial(search_factory, self)
        self.search_class = kwargs.pop('seartch_class', LiteratureSearch)
        default_media_type = kwargs.pop('default_media_type',
                                        'application/vnd+inspire.record.ui+json')
        serializers = kwargs.pop('serializers', {
            'application/vnd+inspire.record.ui+json': json_literature_search_aggregations_ui_v1
        })
        pid_type = kwargs.pop('pid_type', 'lit')
        super(Facets, self).__init__(
            serializers=serializers,
            default_method_media_type={
                'GET': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs)
        self.pid_type = pid_type

    def get(self, *args, **kwargs):
        urlkwargs = dict()
        search_obj = self.search_class()
        search = search_obj.with_preference_param().params(version=True)

        search, qs_kwargs = self.search_factory(search)
        urlkwargs.update(qs_kwargs)

        # Execute search
        search_result = search.execute()

        return self.make_response(
            query_results=search_result,
        )


facets_view = Facets.as_view(
    Facets.view_name,
)

blueprint.add_url_rule(
    '/facets',
    view_func=facets_view
)
