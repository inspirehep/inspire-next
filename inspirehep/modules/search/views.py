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

from flask import Blueprint, request, g, current_app, session, redirect, url_for, render_template

from invenio_search.api import Query
from invenio_search.walkers.elasticsearch import ElasticSearchDSL

from .pagination import Pagination
from .results import Results

blueprint = Blueprint('inspirehep_search',
                      __name__,
                      url_prefix='/search',
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/', methods=['GET', 'POST'])
def search():
    # Get all request arguments
    # @wash_arguments does not exist anymore ?
    p = request.values.get('p', "", type=unicode)
    rg = request.values.get('rg', 25, type=int)
    sf = request.values.get('sf', '', type=unicode)
    so = request.values.get('so', '', type=unicode)
    post_filter = request.values.get('post_filter', '', type=unicode)
    cc = request.values.get('cc', 'hep', type=unicode)
    jrec = request.values.get('jrec', 1, type=int)


    # if cc:
    #     g.collection = collection = Collection.query.filter(
    #         Collection.name == cc).first_or_404()
    # else:
    #     g.collection = collection = Collection.query.get_or_404(1)

    # # Create ES DSL
    response = Query(p)
    response.build()
    response = Results(response.body, index="records-hep") # FIXME do not hardcode index

    response.body.update({
        'size': int(rg),
        'from': jrec-1,
        'aggs': current_app.config['SEARCH_ELASTIC_AGGREGATIONS']['hep'] #FIXME avoid hardcoding it
    })

    if sf in current_app.config['SEARCH_ELASTIC_SORT_FIELDS']:
        so = so if so in ('asc', 'desc') else ''
        sorting = {
            'sort': {
                sf: {
                    'order': so
                }
            }
        }
        response.body.update(sorting)

    filtered_facets = ''
    if 'post_filter' in request.values and request.values['post_filter']:
        parsed_post_filter = Query(request.values.get('post_filter'))
        post_filter = parsed_post_filter.query.accept(
            ElasticSearchDSL()
        )
        response.body['query'] = {
            "filtered": {
                'query': response.body['query'],
                'filter': post_filter
            }
        }
        # extracting the facet filtering
        from .walkers.facets import FacetsVisitor
        filtered_facets = parsed_post_filter.query.accept(
            FacetsVisitor()
        )
        # sets cannot be converted to json. use facetsVisitor to convert them
        # to lists
        filtered_facets = FacetsVisitor.jsonable(filtered_facets)
    else:
        # Save current query and number of hits in the user session
        session_key = 'last-query' + p + cc
        if not session.get(session_key):
            session[session_key] = {}

        session[session_key] = {
            "p": p,
            "collection": cc,
            "number_of_hits": len(response),
            "timestamp": datetime.datetime.utcnow()
        }

    number_of_hits = len(response)

    if number_of_hits and jrec > number_of_hits:
        args = request.args.copy()
        args['jrec'] = 1
        return redirect(url_for('inspirehep_search.search', **args))

    pagination = Pagination((jrec-1) // rg + 1, rg, number_of_hits)

    ctx = dict(
        filtered_facets=filtered_facets,
        response=response,
        rg=rg,
        pagination=pagination,
        collection=cc,
    )

    return render_template("inspirehep_theme/search/results.html", **ctx)
