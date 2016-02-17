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

from flask import Blueprint, request, g

from invenio_collections.models import Collection
from invenio_search.api import Query


blueprint = Blueprint('inspirehep_search',
                      __name__,
                      url_prefix='/search',
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('', methods=['GET', 'POST'])
def search(p='', cc=''):
    # Get all request arguments
    # @wash_arguments does not exist anymore ?
    p = request.args.get('p', '')
    rg = request.args.get('rg', '')
    sf = request.args.get('sf', '')
    so = request.args.get('so', '')
    post_filter = request.args.get('post_filter', '')
    cc = request.args.get('cc', '')
    cc = request.args.get('jrec', 1)

    if cc:
        g.collection = collection = Collection.query.filter(
            Collection.name == cc).first_or_404()
    else:
        g.collection = collection = Collection.query.get_or_404(1)

    # Create ES DSL
    response = Query(p)
    response.build()

    response.body.update({
        'size': int(rg),
        'from': jrec-1,
        'aggs': cfg['SEARCH_ELASTIC_AGGREGATIONS'].get(
            collection.name.lower(), {}
        )
    })

    return "Hello"
