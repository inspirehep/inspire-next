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

"""INSPIRE authors publications views."""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

from elasticsearch.helpers import scan
from flask import (
    Blueprint,
    jsonify,
    request)

from invenio_search import current_search_client

from inspirehep.utils.record import get_title


blueprint = Blueprint('inspirehep_authors_blueprints',
                      __name__,
                      url_prefix='/author',
                      template_folder='../templates',
                      static_folder='../static')


@blueprint.route('/publications', methods=['GET'])
def get_publications():
    recid = request.values.get('recid', 0, type=int)

    publications = []
    collaborations = set()
    keywords = set()

    for result in scan(
            current_search_client,
            query={
                '_source': ['accelerator_experiments',
                            'control_number',
                            'earliest_date',
                            'facet_inspire_doc_type',
                            'publication_info',
                            'titles',
                            'thesaurus_terms'
                            ],
                'query': {"match": {"authors.recid": recid}}
            },
            index='records-hep',
            doc_type='hep'):

        try:
            result_source = result['_source']
            publication = {}

            # Get publication title (required).
            publication['title'] = get_title(result_source)

            # Get publication recid (required).
            publication['recid'] = result_source['control_number']
        except (IndexError, KeyError):
            continue

        # Get publication type.
        try:
            publication['type'] = result_source.get(
                'facet_inspire_doc_type', [])[0]
        except IndexError:
            publication['type'] = "Not defined"

        # Get journal title.
        try:
            publication['journal_title'] = result_source.get(
                'publication_info', [])[0]['journal_title']

            # Get journal recid.
            try:
                publication['journal_recid'] = result_source.get(
                    'publication_info', [])[0]['journal_recid']
            except KeyError:
                pass
        except (IndexError, KeyError):
            pass

        # Get publication year.
        try:
            publication['year'] = result_source.get(
                'publication_info', [])[0]['year']
        except (IndexError, KeyError):
            pass

        # Get keywords.
        for keyword in result_source.get('thesaurus_terms', []):
            if keyword.get('keyword') is not "* Automatic Keywords *" \
                    and keyword.get('keyword'):
                keywords.add(keyword.get('keyword'))

        # Get collaborations.
        for experiment in result_source.get(
                'accelerator_experiments', []):
            collaborations.add(experiment.get('experiment'))

        # Append to the list.
        publications.append(publication)

    response = {}
    response['publications'] = publications
    response['keywords'] = list(keywords)
    response['collaborations'] = list(collaborations)

    return jsonify(response)
