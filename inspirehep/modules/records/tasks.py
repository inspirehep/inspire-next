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

"""Records tasks."""

from __future__ import absolute_import, division, print_function

from celery import shared_task
from elasticsearch.helpers import scan
from flask import current_app
from six import iteritems

from invenio_db import db
from invenio_records.api import Record
from invenio_search import current_search_client as es

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_schema,
    get_index_from_endpoint,
)


@shared_task(ignore_result=True)
def update_refs(old, new):
    records = get_records_to_update(old)

    with db.session.begin_nested():
        for record in records:
            update_links(record, old, new)
            record.commit()
    db.session.commit()


def update_links(record, old, new):
    def _update_links(record, parts, old, new):
        for i, part in enumerate(parts):
            if isinstance(record, dict):
                try:
                    record = record[part]
                except KeyError:
                    return
            elif isinstance(record, list):
                for el in record:
                    _update_links(el, parts[i:], old, new)
                return

        if record['$ref'] == old:
            record['$ref'] = new

    endpoint = get_endpoint_from_schema(record['$schema'])
    whitelist = current_app.config['INSPIRE_REF_UPDATER_WHITELIST'][endpoint]

    for path in whitelist:
        _update_links(record, path.split('.'), old, new)


def get_records_to_update(old):
    def _get_uuids_to_update(old):
        def _replace_record_with_recid(path):
            return path.replace('record', 'recid')

        def _ref_to_recid(ref):
            return int(ref.split('/')[-1])

        whitelists = current_app.config['INSPIRE_REF_UPDATER_WHITELIST']

        for endpoint, whitelist in iteritems(whitelists):
            fields = [_replace_record_with_recid(path) for path in whitelist]
            body = {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'term': {
                                    field: {
                                        'value': _ref_to_recid(old),
                                    },
                                },
                            } for field in fields
                        ],
                    },
                },
            }

            index = get_index_from_endpoint(endpoint)
            query = scan(es, query=body, index=index)

            for result in query:
                yield result['_id']

    def _get_records_to_update(uuids):
        return Record.get_records(uuids)

    uuids = _get_uuids_to_update(old)
    records = _get_records_to_update(uuids)

    return records
