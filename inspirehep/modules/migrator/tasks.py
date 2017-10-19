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
import zlib
from collections import Counter
from itertools import chain

import click
from celery import group, shared_task
from celery.utils.log import get_task_logger
from elasticsearch.helpers import bulk as es_bulk
from elasticsearch.helpers import scan as es_scan
from flask import current_app, url_for
from flask_sqlalchemy import models_committed
from jsonschema import ValidationError
from redis import StrictRedis
from redis_lock import Lock
from six import text_type

from dojson.contrib.marc21.utils import create_record as marc_create_record
from invenio_db import db
from invenio_indexer.api import RecordIndexer, current_record_to_index
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es
from invenio_search.utils import schema_to_index

from inspire_dojson.processors import overdo_marc_dict
from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.dedupers import dedupe_list
from inspire_utils.helpers import force_list
from inspire_utils.record import get_value
from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.pidstore.utils import get_pid_type_from_schema
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.receivers import index_after_commit
from inspirehep.modules.records.utils import file_resolving

from .models import InspireProdRecords


logger = get_task_logger(__name__)

CHUNK_SIZE = 100
LARGE_CHUNK_SIZE = 2000

split_marc = re.compile('<record.*?>.*?</record>', re.DOTALL)


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
    """Split the stream using <record.*?>.*?</record> as pattern."""
    buf = []
    for row in stream:
        row = text_type(row, 'utf8')
        index = row.rfind('</record>')
        if index >= 0:
            buf.append(row[:index + 9])
            for blob in split_blob(''.join(buf)):
                yield blob.encode('utf8')
            buf = [row[index + 9:]]
        else:
            buf.append(row)


@shared_task(ignore_result=True)
def remigrate_records(only_broken=True):
    """Remigrate records.

    Directly migrates the records (declared as broken), e.g. if the dojson
    conversion script have been corrected.
    """
    query = db.session.query(InspireProdRecords).filter_by(valid=False) if only_broken else db.session.query(InspireProdRecords)
    for i, chunk in enumerate(chunker(query.yield_per(CHUNK_SIZE))):
        records = [record.marcxml for record in chunk]
        logger.info("Processed {} records".format(i * CHUNK_SIZE))
        migrate_chunk.delay(records)


@shared_task(ignore_result=True)
def migrate(source, wait_for_results=False):
    """Main migration function."""
    if source.endswith('.gz'):
        fd = gzip.open(source)
    else:
        fd = open(source)

    if wait_for_results:
        # if the wait_for_results is true we enable returning results from migrate_chunk task
        # so that we could use them to synchronize migrate task (which in that case waits for
        # the migrate_chunk tasks to complete before it finishes).
        tasks = []
        migrate_chunk.ignore_result = False

    for i, chunk in enumerate(chunker(split_stream(fd), CHUNK_SIZE)):
        print("Processed {} records".format(i * CHUNK_SIZE))
        if wait_for_results:
            tasks.append(migrate_chunk.s(chunk))
        else:
            migrate_chunk.delay(chunk)

    if wait_for_results:
        job = group(tasks)
        result = job.apply_async()
        result.join()
        migrate_chunk.ignore_result = True
        print('All migration tasks have been completed.')


@shared_task(ignore_result=True)
def continuous_migration():
    """Task to continuously migrate what is pushed up by Legacy."""
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    lock = Lock(r, 'continuous_migration', expire=120, auto_renewal=True)
    if lock.acquire(blocking=False):
        try:
            while r.llen('legacy_records'):
                raw_record = r.lrange('legacy_records', 0, 0)
                if raw_record:
                    migrate_and_insert_record(zlib.decompress(raw_record[0]))
                    db.session.commit()
                r.lpop('legacy_records')
        finally:
            lock.release()
    else:
        logger.info("Continuous_migration already executed. Skipping.")


def create_index_op(record):
    index, doc_type = current_record_to_index(record)

    return {
        '_op_type': 'index',
        '_index': index,
        '_type': doc_type,
        '_id': str(record.id),
        '_version': record.revision_id,
        '_version_type': 'external_gte',
        '_source': RecordIndexer._prepare_record(record, index, doc_type),
    }


@shared_task(ignore_result=False, compress='zlib', acks_late=True)
def migrate_chunk(chunk):
    models_committed.disconnect(index_after_commit)

    index_queue = []

    try:
        for raw_record in chunk:
            with db.session.begin_nested():
                record = migrate_and_insert_record(raw_record)
                if record:
                    index_queue.append(create_index_op(record))
        db.session.commit()
    finally:
        db.session.close()

    req_timeout = current_app.config['INDEXER_BULK_REQUEST_TIMEOUT']
    es_bulk(
        es,
        index_queue,
        stats_only=True,
        request_timeout=req_timeout,
    )

    models_committed.connect(index_after_commit)


@shared_task()
def add_citation_counts(chunk_size=500, request_timeout=120):
    def _build_recid_to_uuid_map(citations_lookup):
        pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.object_type == 'rec').yield_per(1000)

        with click.progressbar(pids) as bar:
            return {
                pid.object_uuid: citations_lookup[int(pid.pid_value)]
                for pid in bar if int(pid.pid_value) in citations_lookup
            }

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
                '_source': 'references.recid',
                'filter': {
                    'exists': {
                        'field': 'references.recid'
                    }
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


def create_record(record):
    """Create record from marc21 model."""
    json = overdo_marc_dict(record)

    if '$schema' in json:
        json['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(json['$schema'])
        )

    return json


def attach_documents_and_figures(record):
    control_number = record.get('control_number', record.get('recid'))
    for attachment in chain(record.get('documents', []), record.get('figures', [])):
        file_url = attachment.get('url')
        if control_number:
            filename = '{}_{}'.format(control_number, attachment.get('key'))
        else:
            filename = attachment.get('key')
        with file_resolving(file_url) as fp:
            record.files[filename] = fp
            record_file_obj = record.files[filename]
            attachment['url'] = '/api/files/{bucket}/{key}'.format(
                bucket=record_file_obj.bucket_id,
                key=record_file_obj.key
            )


def record_insert_or_replace(json):
    """Insert or replace a record."""
    control_number = json.get('control_number', json.get('recid'))

    if control_number:
        pid_type = get_pid_type_from_schema(json['$schema'])
        try:
            pid = PersistentIdentifier.get(pid_type, control_number)
            record = InspireRecord.get_record(pid.object_uuid)
            record.clear()
            record.update(json)
            record.commit()
        except PIDDoesNotExistError:
            record = InspireRecord.create(json, id_=None)
            # Create persistent identifier.
            inspire_recid_minter(str(record.id), json)

        attach_documents_and_figures(record)

        if json.get('deleted'):
            new_recid = get_recid_from_ref(json.get('new_record'))
            if not new_recid:
                record.delete()

        return record


def migrate_and_insert_record(raw_record):
    """Convert a marc21 record to JSON and insert it into the DB."""
    try:
        record = marc_create_record(raw_record, keep_singletons=False)
    except Exception as e:
        logger.exception('Migrator MARC 21 read Error')
        return None

    recid = int(record['001'])
    prod_record = InspireProdRecords(recid=recid)
    prod_record.marcxml = raw_record
    error = None

    try:
        json_record = create_record(record)
    except Exception as e:
        logger.exception('Migrator DoJSON Error')
        error = e

    try:
        if not error:
            record = record_insert_or_replace(json_record)
    except ValidationError as e:
        # Aggregate logs by part of schema being validated.
        pattern = u'Migrator Validator Error: {}, Value: %r, Record: %r'
        logger.error(pattern.format('.'.join(e.schema_path)), e.instance, recid)
        error = e
    except Exception as e:
        # Receivers can always cause exceptions and we could dump the entire
        # chunk because of a single broken record.
        logger.exception('Migrator Record Insert Error')
        error = e

    if error:
        # Invalid record, will not get indexed.
        error_str = u'{0}: Record {1}: {2}'.format(type(error), recid, e)
        prod_record.valid = False
        prod_record.errors = error_str
        db.session.merge(prod_record)
        return None
    else:
        prod_record.valid = True
        db.session.merge(prod_record)
        return record
