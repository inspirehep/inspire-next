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

"""Search blueprint in order for template and static files to be loaded."""

from __future__ import absolute_import, division, print_function

import json

import six
from flask import Blueprint, current_app, jsonify, request, render_template

from elasticsearch_dsl import Q

from invenio_records.api import Record

from inspirehep.modules.records.serializers import json_literature_brief_v1_search
from inspirehep.modules.search import LiteratureSearch
from inspirehep.modules.pidstore.fetchers import inspire_recid_fetcher as pid_fetcher
from inspirehep.utils.record_getter import get_es_record

blueprint = Blueprint(
    'inspirehep_search',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/search")
def search():
    """Search page ui."""
    collection = request.values.get('cc', 'hep', type=unicode).lower()
    ctx = {}
    if collection == 'conferences':
        ctx['search_api'] = '/api/conferences/'
        return render_template('search/search_conferences.html', **ctx)
    if collection == 'authors':
        ctx['search_api'] = '/api/authors/'
        return render_template('search/search_authors.html', **ctx)
    if collection == 'data':
        ctx['search_api'] = 'https://hepdata.net/search/'
        return render_template('search/search_data.html', **ctx)
    if collection == 'experiments':
        ctx['search_api'] = '/api/experiments/'
        return render_template('search/search_experiments.html', **ctx)
    if collection == 'institutions':
        ctx['search_api'] = '/api/institutions/'
        return render_template('search/search_institutions.html', **ctx)
    if collection == 'journals':
        ctx['search_api'] = '/api/journals/'
        return render_template('search/search_journals.html', **ctx)
    if collection == 'jobs':
        ctx['search_api'] = '/api/jobs/'
        return render_template('search/search_jobs.html', **ctx)

    ctx['search_api'] = current_app.config['SEARCH_UI_SEARCH_API']
    return render_template(current_app.config['SEARCH_UI_SEARCH_TEMPLATE'],
                           **ctx)


@blueprint.route('/search/claimedRecords', methods=['GET'])
def get_claimed_records():
    full_name = request.values.get('full_name')
    orcid_id = request.values.get('orcid_id')

    return jsonify({
        'records': [1309999, 1335135]
    })
#   results = query_for_records_using_orcid_id(orcid_id)
#   record_ids = []
#
#   for record in results:
#       record_ids.append(record.get('control_number'))
#
#   return jsonify({
#       'records': record_ids
#   })
#


@blueprint.route('/search/claimRecord', methods=['POST'])
def claim_record():

    body = json.loads(request.data)
    recordId = body.get('recordId')
    users_orcid = body.get('orcid_id')
    phonetic_block = body.get('phonetic_block')

    record = get_es_record('literature', recordId)
    record = Record(record)

    possible_authors = []

    for author in record['authors']:
        for id in author['ids']:
            if id['value'] == users_orcid:
                author['curated_relation'] = True
                record.commit()
                return 'Record Claimed'
        if author.get('signature_block') == phonetic_block:
            author['curated_relation'] = True
            possible_authors.append(author)

    if len(possible_authors) is 1:
        record.commit()
        return 'Record Claimed'

    return 'Somebody should first check that.'


@blueprint.route('/search/claimableRecords', methods=['GET'])
def get_claimable_records():
    full_name = request.values.get('full_name')
    full_name = 'Gao, Yuanning'
    orcidId = request.values.get('orcid_id')

    records = query_for_records_using_full_name(full_name, orcidId)

    record_ids = []
    for record in records:
        record_ids.append(record.control_number)


    return jsonify({
        'records': record_ids
    })


def query_for_records_using_full_name(full_name, orcidId):

    query = Q(
        'bool',
        must=Q('bool', should=[
            Q("match", authors__name_variations=full_name),
            Q("term", authors__ids__value=orcidId)
        ]),
        should=[
            Q("match", authors__full_name=str())
        ]
    )

    results = LiteratureSearch().query(query).execute()

    return results


def query_for_records_using_orcid_id(orcid_id):

    es_query = {"term": {
        "authors.curated_relation": True
        }
    }

    es_filter = {"nested": {
        "path": "authors",
        "filter": {
            "term": {
                "authors.ids.value": {
                    "value": orcid_id
                }
            }
        },
        "inner_hits": {}
    }}

    search = LiteratureSearch().query(es_query).filter(
        es_filter).execute()

    return search


@blueprint.route('/search/suggest', methods=['GET'])
def suggest():
    """Power typeahead.js search bar suggestions."""
    field = request.values.get('field')
    query = request.values.get('query')

    search = LiteratureSearch()
    search = search.suggest(
        'suggestions', query, completion={"field": field}
    )
    suggestions = search.execute_suggest()

    if field == "authors.name_suggest":
        bai_name_map = {}
        for suggestion in suggestions['suggestions'][0]['options']:
            bai = suggestion['payload']['bai']
            if bai in bai_name_map:
                bai_name_map[bai].append(
                    suggestion['text']
                )
            else:
                bai_name_map[bai] = [suggestion['text']]

        result = []
        for key, value in six.iteritems(bai_name_map):
            result.append(
                {
                    'name': max(value, key=len),
                    'value': key,
                    'template': 'author'
                }
            )

        return jsonify({
            'results': result
        })

    return jsonify({
        'results': [
            {'value': s['text']}
            for s in suggestions['suggestions'][0]['options']
        ]
    })


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
    ), sort_keys=True)


@blueprint.app_template_filter('default_sortoption')
def default_sortoption(sort_options):
    """Get defualt sort option for Invenio-Search-JS."""
    return sorted_options(sort_options)[0]['value']
