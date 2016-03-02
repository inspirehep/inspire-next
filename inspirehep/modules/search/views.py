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

"""Search blueprint in order for template and static files to be loaded."""

from __future__ import absolute_import, print_function

import datetime

from flask import (
    Blueprint,
    request,
    current_app,
    session,
    redirect,
    url_for,
    render_template
)

from invenio_search.walkers.elasticsearch import ElasticSearchDSL

from .pagination import Pagination
from .results import Results
from .query import InspireQuery


blueprint = Blueprint('inspirehep_search',
                      __name__,
                      url_prefix='',
                      template_folder='templates',
                      static_folder='static')


# @blueprint.route('/search', methods=['GET', 'POST'])
# def search():
#     """Main search view."""
#     # Get all request arguments
#     p = request.values.get('p', u'', type=unicode)
#     rg = request.values.get('rg', 25, type=int)
#     sf = request.values.get('sf', '', type=unicode)
#     so = request.values.get('so', '', type=unicode)
#     post_filter = request.values.get('post_filter', '', type=unicode)
#     cc = request.values.get('cc', 'hep', type=unicode).lower()
#     if not cc:
#         cc = 'hep'
#     jrec = request.values.get('jrec', 1, type=int)

#     # Create ES DSL
#     index = current_app.config[
#         'SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING'
#     ].get(cc, current_app.config['SEARCH_ELASTIC_DEFAULT_INDEX'])

#     response = InspireQuery(p)
#     response = Results(response.body, index=index, doc_type=index.split('-')[-1])

#     response.body.update({
#         'size': int(rg),
#         'from': jrec - 1,
#         'aggs': current_app.config['SEARCH_ELASTIC_AGGREGATIONS'].get(cc, {})
#     })

#     if sf in current_app.config['SEARCH_ELASTIC_SORT_FIELDS']:
#         so = so if so in ('asc', 'desc') else ''
#         sorting = {
#             'sort': {
#                 sf: {
#                     'order': so
#                 }
#             }
#         }
#         response.body.update(sorting)

#     filtered_facets = ''
#     if 'post_filter' in request.values and request.values['post_filter']:
#         parsed_post_filter = InspireQuery(request.values.get('post_filter'))
#         post_filter = parsed_post_filter.query.accept(
#             ElasticSearchDSL()
#         )
#         response.body['query'] = {
#             "filtered": {
#                 'query': response.body['query'],
#                 'filter': post_filter
#             }
#         }
#         # extracting the facet filtering
#         from .walkers.facets import FacetsVisitor
#         filtered_facets = parsed_post_filter.query.accept(
#             FacetsVisitor()
#         )
#         # sets cannot be converted to json. use facetsVisitor to convert them
#         # to lists
#         filtered_facets = FacetsVisitor.jsonable(filtered_facets)
#     else:
#         # Save current query and number of hits in the user session
#         session_key = 'last-query' + p + cc
#         if not session.get(session_key):
#             session[session_key] = {}

#         session[session_key] = {
#             "p": p,
#             "collection": cc,
#             "number_of_hits": len(response),
#             "timestamp": datetime.datetime.utcnow()
#         }

#     number_of_hits = len(response)

#     if number_of_hits and jrec > number_of_hits:
#         args = request.args.copy()
#         args['jrec'] = 1
#         return redirect(url_for('inspirehep_search.search', **args))

#     pagination = Pagination((jrec - 1) // rg + 1, rg, number_of_hits)

#     ctx = dict(
#         filtered_facets=filtered_facets,
#         response=response,
#         rg=rg,
#         pagination=pagination,
#         collection=cc,
#     )

#     return render_template("inspirehep_theme/search/results.html", **ctx)

@blueprint.route("/search")
def search():
    """Search page ui."""
    return render_template(current_app.config['SEARCH_UI_SEARCH_TEMPLATE'])


def sorted_options(sort_options):
    """Sort sort options for display."""
    return [
        dict(
            title=v['title'],
            value=('-{0}'.format(k)
                   if v.get('default_order', 'asc') == 'desc' else k),
        )
        for k, v in
        sorted(sort_options.items(), key=lambda x: x[1].get('order', 0))
    ]


@blueprint.app_template_filter('format_sortoptions')
def format_sortoptions(sort_options):
    """Create sort options JSON dump for Invenio-Search-JS."""
    return json.dumps(dict(
        options=sorted_options(sort_options)
    ))


@blueprint.app_template_filter('default_sortoption')
def default_sortoption(sort_options):
    """Get defualt sort option for Invenio-Search-JS."""
    return sorted_options(sort_options)[0]['value']
