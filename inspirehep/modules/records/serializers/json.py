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

"""Marshmallow based JSON serializer for records."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.json import JSONSerializer


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
    if 'references' in record:
        display['number_of_references'] = len(record['references'])

    return display


class JSONBriefSerializer(JSONSerializer):
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
