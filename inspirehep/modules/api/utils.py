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

"""API utils."""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_title, get_value


def build_citesummary(search):
    citesummary = []

    for i, el in enumerate(search.scan()):
        result = el.to_dict()

        citesummary.append({
            'citations': [],
            'collaboration': is_collaboration(result),
            'core': is_core(result),
            'date': get_date(result),
            'document_type': get_document_type(result),
            'id': get_id(result),
            'subject': get_subject(result),
            'title': get_title(result),
        })

        search_by_literature = LiteratureSearch().query(
            'match', references__recid=get_id(result)
        ).params(
            _source=[
                'authors.recid',
                'collaborations.value',
                'control_number',
                'earliest_date',
                'facet_inspire_doc_type',
                'inspire_categories',
                'titles.title',
            ]
        )

        for el in search_by_literature.scan():
            literature_result = el.to_dict()

            citesummary[i]['citations'].append({
                'collaboration': is_collaboration(literature_result),
                'core': is_core(literature_result),
                'date': get_date(literature_result),
                'document_type': get_document_type(literature_result),
                'id': get_id(literature_result),
                'selfcite': is_selfcite(
                    result, literature_result),
                'subject': get_subject(literature_result),
                'title': get_title(literature_result),
            })

    return citesummary


def get_date(record):
    return record['earliest_date']


def get_document_type(record):
    return get_value(record, 'facet_inspire_doc_type[0]')


def get_id(record):
    return record['control_number']


def get_subject(record):
    inspire_categories = force_force_list(get_value(record, 'inspire_categories'))
    terms = [ic['term'] for ic in inspire_categories if ic.get('term')]

    if terms:
        return terms[0]


def is_collaboration(record):
    return force_force_list(get_value(record, 'collaborations.value')) != []


def is_core(record):
    return 'core' in record and record['core']


def is_selfcite(citee, citer):
    def _get_authors_recids(record):
        return set(force_force_list(get_value(record, 'authors.recid')))

    citee_authors_recids = _get_authors_recids(citee)
    citer_authors_recids = _get_authors_recids(citer)

    return len(citee_authors_recids & citer_authors_recids) > 0
