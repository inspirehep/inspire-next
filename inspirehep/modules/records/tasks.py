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
from elasticsearch.helpers import bulk
from flask import current_app
from sqlalchemy import tuple_
from sqlalchemy.orm.exc import NoResultFound, StaleDataError

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.errors import MissingCitedRecordError
from inspirehep.utils.record import create_index_op
from inspirehep.utils.record_getter import get_db_record, RecordGetterError

logger = get_task_logger(__name__)


@shared_task(ignore_result=False, max_retries=0)
def batch_reindex(uuids, request_timeout=None):
    """Task for bulk reindexing records."""
    def actions():
        for uuid in uuids:
            try:
                record = InspireRecord.get_record(uuid)
                if record.get('deleted', False):
                    logger.debug("Record already %s deleted, not indexing!", uuid)
                    continue
                yield create_index_op(record, version_type='force')
            except NoResultFound as e:
                logger.warn('Record %s failed to load: %s', uuid, e)

    if not request_timeout:
        request_timeout = current_app.config['INDEXER_BULK_REQUEST_TIMEOUT']

    success, failures = bulk(
        es,
        actions(),
        request_timeout=request_timeout,
        raise_on_error=False,
        raise_on_exception=False,
    )

    return {
        'success': success,
        'failures': [failure for failure in failures or []],
    }


@shared_task(ignore_result=False, bind=True, max_retries=12)
def index_modified_citations_from_record(self, pid_type, pid_value, db_version):
    """Index records from the record's citations.

    This tasks retries itself in 2 scenarios:
    - A new record is saved but it is not yet visible by this task bacause the
    transaction is not finished yet (RecordGetterError).

    - When a record is updated, but new changes are not yet in DB, for the
    same reason as above (StaleDataError).

    Args:
        pid_type(String): pid type of the record
        pid_value(String): pid value of the record
        db_version(Int): the correct version of the record that we expect
            to index. This prevents loading stale data from the DB.

    Raise:
      MissingCitedRecordError in case cited records are not found
    """
    logger.info("Starting index_modified_citations_from_record for {pid_value}"
                " with db version: {db_version}".format(
                    pid_value=pid_value, db_version=db_version))
    try:
        record = get_db_record(pid_type, pid_value)
        if record.model.version_id < db_version:
            raise StaleDataError

    except (RecordGetterError, StaleDataError) as e:
        logger.warn(
            'Record {} not yet at version {} on DB'.format(
                (pid_type, pid_value), db_version)
        )
        backoff = 2 ** (self.request.retries + 1)
        if self.max_retries < self.request.retries + 1:
            logger.warn("({pid_value}) - Failing - too many retries".format(
                pid_value=pid_value)
            )
        raise self.retry(countdown=backoff, exc=e)

    pids = record.get_modified_references()

    if not pids:
        logger.info('No references change for record {}'.format((pid_type, pid_value)))
        return None
    logger.info(
        "({pid_value}) There are {count_pids}"
        " records references changed".format(pid_value=pid_value,
                                             count_pids=len(pids))
    )

    uuids = [
        str(pid.object_uuid) for pid in
        db.session.query(PersistentIdentifier.object_uuid).filter(
            PersistentIdentifier.object_type == 'rec',
            tuple_(PersistentIdentifier.pid_type, PersistentIdentifier.pid_value).in_(pids)
        )
    ]

    if uuids:
        logger.info("({pid_value}) contains pids - starting batch".format(
            pid_value=pid_value)
        )
        return batch_reindex(uuids)

    raise MissingCitedRecordError(
        'Cited records to reindex not found:\nuuids: {}'.format(uuids)
    )
