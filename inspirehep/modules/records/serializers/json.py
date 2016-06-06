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

import json

from flask import get_flashed_messages

from inspirehep.modules.theme.jinja2filters import (
    format_date, publication_info
)

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
    if 'earliest_date' in record:
        display['date'] = format_date(record['earliest_date'])
    if 'publication_info' in record:
        display['publication_info_line'] = publication_info(record)
    if 'authors' in record:
        display['number_of_authors'] = len(record['authors'])

    return display


def get_all_warnings():
    warnings = []
    flashed_mesagges = dict(get_flashed_messages(
        with_categories=True, category_filter=["query_suggestion"]))
    if flashed_mesagges:
        warnings.append(flashed_mesagges)
    return warnings


class JSONBriefSerializer(JSONSerializer):
    """JSON brief format serializer."""

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """Serialize a search result.
        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        return json.dumps(dict(
            hits=dict(
                hits=[self.transform_search_hit(
                    pid_fetcher(hit['_id'], hit['_source']),
                    hit,
                    links_factory=item_links_factory,
                ) for hit in search_result['hits']['hits']],
                total=search_result['hits']['total'],
            ),
            links=links or {},
            aggregations=search_result.get('aggregations', dict()),
            warnings=get_all_warnings(),
        ), **self._format_args())

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
