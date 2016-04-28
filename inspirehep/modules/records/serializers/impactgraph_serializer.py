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

"""Impact Graph serializer for records."""

from __future__ import absolute_import, print_function

import json

from invenio_search import current_search_client

from inspirehep.utils.record import get_title
from inspirehep.modules.search import IQ


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

        es_query = IQ('refersto:' + record['control_number'])
        record_citations = current_search_client.search(
            index='records-hep',
            doc_type='hep',
            body={"query": es_query.to_dict()},
            size=9999,
            _source=[
                'control_number',
                'citation_count',
                'titles',
                'earliest_date'
            ]
        )['hits']['hits']
        for citation in record_citations:
            citation = citation['_source']
            citations.append({
                "inspire_id": citation['control_number'],
                "citation_count": citation.get('citation_count', 0),
                "title": get_title(citation),
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
            mget_body = {
                "ids": reference_recids
            }

            record_references = current_search_client.mget(
                index='records-hep',
                doc_type='hep',
                body=mget_body,
                _source=[
                    'control_number',
                    'citation_count',
                    'titles',
                    'earliest_date'
                ]
            )

            for reference in record_references["docs"]:
                ref_info = reference["_source"]

                references.append({
                    "inspire_id": ref_info['control_number'],
                    "citation_count": ref_info.get('citation_count', 0),
                    "title": get_title(ref_info),
                    "year": ref_info['earliest_date'].split('-')[0]
                })

        out['references'] = references

        return json.dumps(out)
