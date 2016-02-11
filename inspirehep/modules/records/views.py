# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from flask import Blueprint, jsonify

from invenio_base.decorators import wash_arguments
from invenio_ext.es import es
from invenio_search.api import Query

from inspirehep.utils.record import get_title


blueprint = Blueprint(
    'inspire_records',
    __name__,
    url_prefix='/record',
    template_folder='templates',
    static_folder="static",
)


@blueprint.route('/api/impactgraph', methods=['GET'])
@wash_arguments({'recid': (unicode, "")})
def impactgraph(recid):
    """Handler for impact graph information retrieval."""
    record = es.get_source(index='hep', id=recid, doc_type='record')

    out = {}

    # Add information about current record
    out['inspire_id'] = record['control_number']
    out['title'] = get_title(record)
    out['year'] = record['earliest_date'].split('-')[0]

    # Get citations
    citations = []

    es_query = Query('refersto:' + recid).search()
    es_query.body.update(
        {
            'size': 9999
        }
    )
    record_citations = es_query.records()
    for citation in record_citations:
        citations.append({
            "inspire_id": citation['control_number'],
            "citation_count": citation['citation_count'],
            "title": get_title(citation),
            "year": citation['earliest_date'].split('-')[0]
        })

    out['citations'] = citations

    # Get references
    record_references = record.get('references')
    references = []

    reference_recids = [
        ref['recid'] for ref in record_references if ref.get('recid')
    ]

    if reference_recids:
        mget_body = {
            "ids": reference_recids
        }

        record_references = es.mget(
            index='hep',
            doc_type='record',
            body=mget_body
        )

        for reference in record_references["docs"]:
            ref_info = reference["_source"]

            references.append({
                "inspire_id": ref_info['control_number'],
                "citation_count": ref_info['citation_count'],
                "title": get_title(ref_info),
                "year": ref_info['earliest_date'].split('-')[0]
            })

    out['references'] = references

    return jsonify(out)
