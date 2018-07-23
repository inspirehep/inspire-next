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

"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

import gzip
import re
import tarfile
import zlib
from collections import Counter
from contextlib import closing
from itertools import chain

import click
import requests

from celery import group, shared_task
from elasticsearch.helpers import bulk as es_bulk
from elasticsearch.helpers import scan as es_scan
from flask import current_app
from flask_sqlalchemy import models_committed
from functools import wraps
from jsonschema import ValidationError
from redis import StrictRedis
from redis_lock import Lock

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es
from invenio_search.utils import schema_to_index

from inspire_dojson import marcxml2record
from inspire_utils.dedupers import dedupe_list
from inspire_utils.helpers import force_list
from inspire_utils.logging import getStackTraceLogger
from inspire_utils.record import get_value
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.pidstore.utils import (
    get_pid_types_from_endpoints,
)
from inspirehep.modules.records.receivers import index_after_commit
from inspirehep.utils.schema import ensure_valid_schema
from inspirehep.utils.record import create_index_op

from .models import LegacyRecordsMirror

LOGGER = getStackTraceLogger(__name__)

CHUNK_SIZE = 100
LARGE_CHUNK_SIZE = 2000

split_marc = re.compile('<record.*?>.*?</record>', re.DOTALL)


def disable_orcid_push(task_function):
    """Temporarily disable ORCID push

    Decorator to temporarily disable ORCID push while a given task is running,
    and only for that task. Takes care of restoring the previous state in case
    of errors or when the task is finished. This does not interfere with other
    tasks, firstly because of ditto, secondly because configuration is only
    changed within the worker's process (thus doesn't affect parallel tasks).
    """
    @wraps(task_function)
    def _task_function(*args, **kwargs):
        initial_state = current_app.config['FEATURE_FLAG_ENABLE_ORCID_PUSH']
        current_app.config['FEATURE_FLAG_ENABLE_ORCID_PUSH'] = False
        try:
            task_function(*args, **kwargs)
        finally:
            current_app.config['FEATURE_FLAG_ENABLE_ORCID_PUSH'] = initial_state

    return _task_function


def chunker(iterable, chunksize=CHUNK_SIZE):
    buf = []
    for elem in iterable:
        buf.append(elem)
        if len(buf) == chunksize:
            yield buf
            buf = []
    if buf:
        yield buf


def split_blob(blob):
    """Split the blob using <record.*?>.*?</record> as pattern."""
    for match in split_marc.finditer(blob):
        yield match.group()


def split_stream(stream):
    """Split the stream using <record.*?>.*?</record> as pattern.

    This operates line by line in order not to load the entire file in memory.
    """
    len_closing_tag = len('</record>')
    buf = []
    for row in stream:
        row = row.decode('utf8')
        index = row.rfind('</record>')
        if index >= 0:
            buf.append(row[:index + len_closing_tag])
            for blob in split_blob(''.join(buf)):
                yield blob.encode('utf8')
            buf = [row[index + len_closing_tag:]]
        else:
            buf.append(row)


def read_file(source):
    if source.endswith('.gz'):
        with gzip.open(source, 'rb') as fd:
            for line in fd:
                yield line
    elif source.endswith('.tar'):  # assuming prodsync tarball
        with closing(tarfile.open(source)) as tar:
            for file_ in tar:
                print('Processing {}'.format(file_.name))
                unzipped = gzip.GzipFile(fileobj=tar.extractfile(file_), mode='rb')
                for line in unzipped:
                    yield line
    else:
        with open(source, 'rb') as fd:
            for line in fd:
                yield line


def migrate_record_from_legacy(recid):
    response = requests.get('http://inspirehep.net/record/{recid}/export/xme'.format(recid=recid))
    response.raise_for_status()
    migrate_and_insert_record(next(split_blob(response.content)))
    db.session.commit()


def migrate_from_mirror(also_migrate=None, wait_for_results=False, skip_files=None):
    """Migrate legacy records from the local mirror.

    By default, only the records that have not been migrated yet are migrated.

    Args:
        also_migrate(Optional[string]): if set to ``'broken'``, also broken
            records will be migrated. If set to ``'all'``, all records will be
            migrated.
        skip_files(Optional[bool]): flag indicating whether the files in the
            record metadata should be copied over from legacy and attach to the
            record. If None, the corresponding setting is read from the
            configuration.
        wait_for_results(bool): flag indicating whether the task should wait
            for the migration to finish (if True) or fire and forget the migration
            tasks (if False).
    """
    if skip_files is None:
        skip_files = current_app.config.get(
            'RECORDS_MIGRATION_SKIP_FILES',
            False,
        )

    query = LegacyRecordsMirror.query.with_entities(LegacyRecordsMirror.recid)
    if also_migrate is None:
        query = query.filter(LegacyRecordsMirror.valid.is_(None))
    elif also_migrate == 'broken':
        query = query.filter(LegacyRecordsMirror.valid.isnot(True))
    elif also_migrate != 'all':
        raise ValueError('"also_migrate" should be either None, "all" or "broken"')

    if wait_for_results:
        # if the wait_for_results is true we enable returning results from the
        # migrate_recids_from_mirror task so that we could use them to
        # synchronize migrate task (which in that case waits for the
        # migrate_recids_from_mirror tasks to complete before it finishes).
        tasks = []
        migrate_recids_from_mirror.ignore_result = False

    chunked_recids = chunker(res.recid for res in query.yield_per(CHUNK_SIZE))
    for i, chunk in enumerate(chunked_recids):
        print("Scheduled {} records for migration".format(i * CHUNK_SIZE + len(chunk)))
        if wait_for_results:
            tasks.append(migrate_recids_from_mirror.s(chunk, skip_files=skip_files))
        else:
            migrate_recids_from_mirror.delay(chunk, skip_files=skip_files)

    if wait_for_results:
        job = group(tasks)
        result = job.apply_async()
        result.join()
        migrate_recids_from_mirror.ignore_result = True
        print('All migration tasks have been completed.')


def migrate_from_file(source, wait_for_results=False):
    populate_mirror_from_file(source)
    migrate_from_mirror(wait_for_results=wait_for_results)


def populate_mirror_from_file(source):
    for i, chunk in enumerate(chunker(split_stream(read_file(source)), CHUNK_SIZE)):
        insert_into_mirror(chunk)
        print("Inserted {} records into mirror".format(i * CHUNK_SIZE + len(chunk)))


@shared_task(ignore_result=True)
def continuous_migration(skip_files=None):
    """Task to continuously migrate what is pushed up by Legacy."""
    if skip_files is None:
        skip_files = current_app.config.get(
            'RECORDS_MIGRATION_SKIP_FILES',
            False,
        )
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    lock = Lock(r, 'continuous_migration', expire=120, auto_renewal=True)
    if lock.acquire(blocking=False):
        try:
            while r.llen('legacy_records'):
                raw_record = r.lrange('legacy_records', 0, 0)
                if raw_record:
                    migrate_and_insert_record(
                        zlib.decompress(raw_record[0]),
                        skip_files=skip_files,
                    )
                    db.session.commit()
                r.lpop('legacy_records')
        finally:
            lock.release()
    else:
        LOGGER.info("Continuous_migration already executed. Skipping.")


@shared_task(ignore_result=False, queue='migrator')
@disable_orcid_push
def migrate_recids_from_mirror(prod_recids, skip_files=False):
    models_committed.disconnect(index_after_commit)

    index_queue = []

    for recid in prod_recids:
        with db.session.begin_nested():
            record = migrate_record_from_mirror(
                LegacyRecordsMirror.query.get(recid),
                skip_files=skip_files,
            )
            if record:
                index_queue.append(create_index_op(record))
    db.session.commit()

    req_timeout = current_app.config['INDEXER_BULK_REQUEST_TIMEOUT']
    es_bulk(
        es,
        index_queue,
        stats_only=True,
        request_timeout=req_timeout,
    )

    models_committed.connect(index_after_commit)


def _build_recid_to_uuid_map(citations_lookup):
    numeric_pid_types = get_pid_types_from_endpoints()
    pids = PersistentIdentifier.query.filter(
        PersistentIdentifier.object_type == 'rec',
        PersistentIdentifier.pid_type.in_(numeric_pid_types)).yield_per(
        1000)
    with click.progressbar(pids) as bar:
        return {
            pid.object_uuid: citations_lookup[int(pid.pid_value)]
            for pid in bar if int(pid.pid_value) in citations_lookup
        }


@shared_task()
def add_citation_counts(chunk_size=500, request_timeout=120):
    def _get_records_to_update_generator(citations_lookup):
        with click.progressbar(citations_lookup.iteritems()) as bar:
            for uuid, citation_count in bar:
                yield {
                    '_op_type': 'update',
                    '_index': index,
                    '_type': doc_type,
                    '_id': str(uuid),
                    'doc': {'citation_count': citation_count}
                }

    index, doc_type = schema_to_index('records/hep.json')
    citations_lookup = Counter()

    click.echo('Extracting all citations...')
    with click.progressbar(es_scan(
            es,
            query={
                'query': {
                    'exists': {
                        'field': 'references.recid'
                    },
                },
                'size': LARGE_CHUNK_SIZE
            },
            scroll=u'2m',
            index=index,
            doc_type=doc_type)) as records:
        for record in records:
            unique_refs_ids = dedupe_list(list(chain.from_iterable(map(
                force_list, get_value(record, '_source.references.recid')))))

            for unique_refs_id in unique_refs_ids:
                citations_lookup[unique_refs_id] += 1
    click.echo('... DONE.')

    click.echo('Mapping recids to UUIDs...')
    citations_lookup = _build_recid_to_uuid_map(citations_lookup)
    click.echo('... DONE.')

    click.echo('Adding citation numbers...')
    success, failed = es_bulk(
        es,
        _get_records_to_update_generator(citations_lookup),
        chunk_size=chunk_size,
        raise_on_exception=False,
        raise_on_error=False,
        request_timeout=request_timeout,
        stats_only=True,
    )
    click.echo('... DONE: {} records updated with success. {} failures.'.format(
        success, failed))


def insert_into_mirror(raw_records):
    for raw_record in raw_records:
        prod_record = LegacyRecordsMirror.from_marcxml(raw_record)
        db.session.merge(prod_record)
    db.session.commit()


def migrate_and_insert_record(raw_record, skip_files=False):
    """Migrate a record and insert it if valid, or log otherwise."""
    prod_record = LegacyRecordsMirror.from_marcxml(raw_record)
    db.session.merge(prod_record)
    return migrate_record_from_mirror(prod_record, skip_files=skip_files)


def migrate_record_from_mirror(prod_record, skip_files=False):
    """Migrate a mirrored legacy record into an Inspire record.

    Args:
        prod_record(LegacyRecordsMirror): the mirrored record to migrate.
        skip_files(bool): flag indicating whether the files in the record
            metadata should be copied over from legacy and attach to the
            record.

    Returns:
        dict: the migrated record metadata, which is also inserted into the database.
    """
    try:
        json_record = marcxml2record(prod_record.marcxml)
    except Exception as exc:
        LOGGER.exception('Migrator DoJSON Error')
        prod_record.error = exc
        db.session.merge(prod_record)
        return None

    if '$schema' in json_record:
        ensure_valid_schema(json_record)

    try:
        record = InspireRecord.create_or_update(json_record, skip_files=skip_files)
        record.commit()
    except ValidationError as exc:
        pattern = u'Migrator Validator Error: {}, Value: %r, Record: %r'
        LOGGER.error(pattern.format('.'.join(exc.schema_path)), exc.instance, prod_record.recid)
        prod_record.error = exc
        db.session.merge(prod_record)
    except Exception as exc:
        LOGGER.exception('Migrator Record Insert Error')
        prod_record.error = exc
        db.session.merge(prod_record)
    else:
        prod_record.valid = True
        db.session.merge(prod_record)
        return record
