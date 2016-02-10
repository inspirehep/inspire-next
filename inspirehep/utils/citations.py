# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from invenio_ext.template import render_template_to_string

from invenio_search.api import Query


def render_citations(recid):
    """Citation export for single record in datatables format.

        :returns: list
            List of lists where every item represents a datatables row.
            A row consists of [reference, num_citations]
    """
    out = []
    row = []
    es_query = Query('refersto:' + str(recid)).search()
    es_query.body.update({
        'sort': [{'citation_count': {'order': 'desc'}}]
    })
    citations = es_query.records()

    for citation in citations:
        row.append(render_template_to_string("citations.html",
                                             record=citation, reference=None))
        row.append(citation.get('citation_count', ''))
        out.append(row)
        row = []

    return out
