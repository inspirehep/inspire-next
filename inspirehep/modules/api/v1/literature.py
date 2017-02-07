# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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
# or submit itself to any jurisdiction

"""API of Literature records."""

from __future__ import absolute_import, division, print_function

import json

from inspirehep.modules.records.serializers.response import (
    record_responsify_nocache,
)
from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.record import get_title

from ..utils import (
    get_date,
    get_document_type,
    get_id,
    get_subject,
    is_collaboration,
    is_core,
    is_selfcite,
)


class APILiteratureCitesummary(object):

    """Implementation of citesummary for Literature records."""

    def serialize(self, pid, record, links_factory=None):
        citesummary = [
            {
                'citations': [],
                'collaboration': is_collaboration(record),
                'core': is_core(record),
                'date': get_date(record),
                'document_type': get_document_type(record),
                'id': get_id(record),
                'subject': get_subject(record),
                'title': get_title(record),
            },
        ]

        search = LiteratureSearch().query(
            'match', references__recid=get_id(record)
        ).params(
            _source=[
                'authors.recid',
                'collaborations.value',
                'control_number',
                'earliest_date',
                'facet_inspire_doc_type',
                'inspire_categories',
                'titles.title',
            ],
        )

        for el in search.scan():
            result = el.to_dict()

            citesummary[0]['citations'].append({
                'collaboration': is_collaboration(result),
                'core': is_core(result),
                'date': get_date(result),
                'document_type': get_document_type(result),
                'id': get_id(result),
                'subject': get_subject(result),
                'selfcite': is_selfcite(record, result),
                'title': get_title(result),
            })

        return json.dumps(citesummary)


citesummary = APILiteratureCitesummary()
citesummary_response = record_responsify_nocache(
    citesummary, 'application/json')
