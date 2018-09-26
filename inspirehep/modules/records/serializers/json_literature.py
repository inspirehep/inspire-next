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

"""Marshmallow based JSON serializer for records."""

from __future__ import absolute_import, division, print_function

import json

from invenio_records_rest.serializers.json import JSONSerializer


class LiteratureJSONUISerializer(JSONSerializer):
    """JSON brief format serializer."""

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        result = super(LiteratureJSONUISerializer, self).preprocess_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        return result

    def preprocess_search_hit(self, pid, record_hit, links_factory=None,
                              **kwargs):
        result = super(LiteratureJSONUISerializer, self). \
            preprocess_search_hit(pid, record_hit,
                                  links_factory=links_factory, **kwargs)
        return result


class LiteratureCitationsJSONSerializer(JSONSerializer):

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare a record and persistent identifier for serialization."""
        return record

    def serialize(self, pid, data, links_factory=None, **kwargs):
        return json.dumps(
            {
                'metadata': {
                    'citations': [
                        self.transform_record(pid, record, **kwargs)
                        for record in data['citations']
                    ],
                    'citation_count': data['citation_count']
                },
            }, **self._format_args()
        )


class FacetsJSONUISerializer(JSONSerializer):
    """JSON brief format serializer."""

    def serialize_facets(self, query_results, **kwargs):
        return json.dumps(
            {
                'aggregations': query_results.aggregations.to_dict()
            }
        )
