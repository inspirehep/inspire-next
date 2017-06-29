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

"""Records tasks."""

from __future__ import absolute_import, division, print_function

from celery import shared_task
from celery.utils.log import get_task_logger
from elasticsearch.helpers import scan
from flask import current_app
from six import iteritems

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es

from inspire_dojson.utils import get_recid_from_ref
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.utils import get_endpoint_from_record
from inspirehep.utils.record_getter import get_db_record


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def update_refs(old_ref, new_ref):
    """Update references in the entire database.

    Replaces all occurrences of ``old_ref`` with ``new_ref``,
    provided that they happen at one of the paths listed in
    ``INSPIRE_REF_UPDATER_WHITELISTS``.
    """
    records = get_records_to_update(old_ref)

    with db.session.begin_nested():
        for record in records:
            logger.info('Updated reference: %s -> %s, Record: %s', old_ref, new_ref, record.id)
            update_links(record, old_ref, new_ref)
            record.commit()
    db.session.commit()


def update_links(record, old_ref, new_ref):
    def _update_links(record, parts, old_ref, new_ref):
        for i, part in enumerate(parts):
            if isinstance(record, dict):
                try:
                    record = record[part]
                except KeyError:
                    return
            elif isinstance(record, list):
                for el in record:
                    _update_links(el, parts[i:], old_ref, new_ref)
                return

        if record['$ref'] == old_ref:
            record['$ref'] = new_ref

    endpoint = get_endpoint_from_record(record)
    whitelist = current_app.config['INSPIRE_REF_UPDATER_WHITELISTS'][endpoint]

    for path in whitelist:
        _update_links(record, path.split('.'), old_ref, new_ref)


def get_records_to_update(old_ref):
    def _get_uuids_to_update(old_ref):
        def _replace_record_with_recid(path):
            return path.replace('record', 'recid')

        def _ref_to_recid(ref):
            return int(ref.split('/')[-1])

        result = []

        whitelists = current_app.config['INSPIRE_REF_UPDATER_WHITELISTS']
        for endpoint, whitelist in iteritems(whitelists):
            fields = [_replace_record_with_recid(path) for path in whitelist]
            body = {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'term': {
                                    field: {
                                        'value': _ref_to_recid(old_ref),
                                    },
                                },
                            } for field in fields
                        ],
                    },
                },
            }

            index = current_app.config['INSPIRE_ENDPOINT_TO_INDEX'][endpoint]
            query = scan(es, query=body, index=index)

            result.extend(el['_id'] for el in list(query))

        return result

    def _get_records_to_update(uuids):
        return InspireRecord.get_records(uuids)

    uuids = _get_uuids_to_update(old_ref)
    records = _get_records_to_update(uuids)

    return records


@shared_task
def merge_merged_records():
    """Merge all records that were marked as merged."""
    def _get_record(recid):
        pid = PersistentIdentifier.query.filter_by(pid_value=str(recid)).one()
        return get_db_record(pid.pid_type, recid)

    records = get_records_to_merge()

    with db.session.begin_nested():
        for record in records:
            recid = record['control_number']
            other_recid = get_recid_from_ref(record['new_record'])
            other_record = _get_record(other_recid)

            logger.info('Merged records: %d and %d', recid, other_recid)
            record.merge(other_record)
            record.commit()
    db.session.commit()


def get_records_to_merge():
    def _get_uuids_to_merge():
        body = {
            'query': {
                'exists': {
                    'field': 'new_record',
                },
            },
        }

        index = 'records-*'
        query = scan(es, query=body, index=index)

        for result in query:
            yield result['_id']

    def _get_records_to_merge(uuids):
        return InspireRecord.get_records(uuids)

    uuids = _get_uuids_to_merge()
    records = _get_records_to_merge(uuids)

    return records
