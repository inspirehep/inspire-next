# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""Impact Graph serializer for records."""

from __future__ import absolute_import, division, print_function

import json

from inspirehep.utils.record import get_title
from inspirehep.utils.record_getter import get_es_records
from inspirehep.modules.search import LiteratureSearch


class ImpactGraphSerializer(object):

    """Impact Graph serializer for records."""

    def serialize(self, pid, record, links_factory=None):
        """
        Serialize a single impact graph from a record.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for the link generation,
                              which are added to the response.
        """
        out = {}

        # Add information about current record
        out['inspire_id'] = record['control_number']
        out['title'] = get_title(record)
        out['year'] = record['earliest_date'].split('-')[0]

        # Get citations
        citations = []

        record_citations = LiteratureSearch().query(
            'match', references__recid=record['control_number'],
        ).params(
            size=9999,
            _source=[
                'control_number',
                'citation_count',
                'titles',
                'earliest_date'
            ]
        ).execute().hits

        for citation in record_citations:
            try:
                citation_count = citation.citation_count
            except AttributeError:
                citation_count = 0
            citations.append({
                "inspire_id": citation['control_number'],
                "citation_count": citation_count,
                "title": get_title(citation.to_dict()),
                "year": citation['earliest_date'].split('-')[0]
            })

        out['citations'] = citations

        # Get references
        record_references = record.get('references', [])
        references = []

        reference_recids = [
            ref['recid'] for ref in record_references if ref.get('recid')
        ]

        if reference_recids:
            record_references = get_es_records(
                'lit',
                reference_recids,
                _source=[
                    'control_number',
                    'citation_count',
                    'titles',
                    'earliest_date'
                ]
            )

            for reference in record_references:
                try:
                    citation_count = reference.citation_count
                except AttributeError:
                    citation_count = 0
                references.append({
                    "inspire_id": reference['control_number'],
                    "citation_count": citation_count,
                    "title": get_title(reference),
                    "year": reference['earliest_date'].split('-')[0]
                })

        out['references'] = references

        return json.dumps(out)
