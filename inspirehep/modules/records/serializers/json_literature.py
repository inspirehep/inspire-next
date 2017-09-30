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

from invenio_records_rest.serializers.json import JSONSerializer

from inspire_utils.date import format_date
from inspirehep.modules.records.wrappers import LiteratureRecord


def process_es_hit(record):
    """
    Process record coming from Elasticsearch.

    Allows to remove unnecessary fields to reduce bandwidth and speed
    up the client application.
    """
    if 'authors' in record:
        record['authors'] = record['authors'][:10]
    if 'references' in record:
        del record['references']

    return record


def get_display_fields(record):
    """
    Add extra fields used for display by client application.

    Jinja2 filters can be applied here to format certain fields.
    """
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
    display['admin_tools'] = record.admin_tools

    return display


class LiteratureJSONBriefSerializer(JSONSerializer):
    """JSON brief format serializer."""

    @staticmethod
    def preprocess_search_hit(pid, record_hit, links_factory=None):
        """Prepare a record hit from Elasticsearch for serialization."""
        links_factory = links_factory or (lambda x: dict())
        # Get extra display fields before the ES hit gets processed
        display = get_display_fields(record_hit['_source'])
        record = dict(
            pid=pid,
            metadata=process_es_hit(record_hit['_source']),
            links=links_factory(pid),
            display=display,
            revision=record_hit['_version'],
            created=None,
            updated=None,
        )
        # Move created/updated attrs from source to object.
        for key in ['_created', '_updated']:
            if key in record['metadata']:
                record[key[1:]] = record['metadata'][key]
                del record['metadata'][key]
        return record
