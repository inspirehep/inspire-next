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

from inspire_utils.date import format_date
from inspirehep.modules.records.wrappers import LiteratureRecord


def _get_ui_metadata(record):
    """Record extra metadata for the UI.

    Args:
        record(dict): the record.

    Returns:
        dict: the extra metadata.
    """
    # FIXME: Deprecated, must be removed once the new UI is released
    display = {}
    record = LiteratureRecord(record)
    if 'references' in record:
        display['number_of_references'] = len(record['references'])
    if 'earliest_date' in record:
        display['date'] = format_date(record['earliest_date'])
    if 'publication_info' in record:
        display['publication_info'] = record.publication_information
        display['conference_info'] = record.conference_information
    if 'authors' in record:
        display['number_of_authors'] = len(record['authors'])
    if 'external_system_identifiers' in record:
        display['external_system_identifiers'] = \
            record.external_system_identifiers
    display['admin_tools'] = record.admin_tools

    return display


def get_citations_count(original_record):
    """ Try to get citations"""
    if hasattr(original_record, 'get_citations_count'):
        """Call it only when it has this method"""
        return original_record.get_citations_count()
    return None


def _preprocess_result(result, original_record=None):
    """Add additional fields to output json"""
    if original_record is not None:
        # If it is an db object then get citations from db
        # Otherwise if it is from ES it has citations already in json
        result['metadata']['citation_count'] = get_citations_count(original_record)
    record = result['metadata']
    ui_metadata = _get_ui_metadata(record)
    # FIXME: Deprecated, must be removed once the new UI is released
    result['display'] = ui_metadata
    result['metadata'] = record

    return result


class LiteratureJSONUISerializer(JSONSerializer):
    """JSON brief format serializer."""

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        result = super(LiteratureJSONUISerializer, self).preprocess_record(
            pid, record, links_factory=links_factory, **kwargs
        )
        return _preprocess_result(result, record)

    def preprocess_search_hit(self, pid, record_hit, links_factory=None,
                              **kwargs):
        result = super(LiteratureJSONUISerializer, self). \
            preprocess_search_hit(pid, record_hit,
                                  links_factory=links_factory, **kwargs)
        return _preprocess_result(result)


class LiteratureCitationsJSONSerializer(JSONSerializer):

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare a record and persistent identifier for serialization."""
        return record.dumps()

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
