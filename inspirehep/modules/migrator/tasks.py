# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, print_function

import gzip
import re
import zlib
import click

from jsonschema import ValidationError

from six import text_type

from celery.utils.log import get_task_logger

from collections import Counter

from dojson.contrib.marc21.utils import create_record as marc_create_record

from elasticsearch.helpers import bulk as es_bulk
from elasticsearch.helpers import scan as es_scan

from flask import current_app, url_for

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.hep import hep
from inspirehep.dojson.hepnames import hepnames
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.journals import journals
from inspirehep.dojson.processors import _collection_in_record

from celery import group, shared_task

from invenio_db import db

from invenio_indexer.api import RecordIndexer, _record_to_index
from invenio_pidstore.models import PersistentIdentifier, NoResultFound
from invenio_records import Record
from invenio_search import current_search_client
from invenio_search.utils import schema_to_index

from .models import InspireProdRecords
from ..pidstore.minters import inspire_recid_minter


logger = get_task_logger(__name__)

CHUNK_SIZE = 100
LARGE_CHUNK_SIZE = 10000

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
def migrate_broken_records(broken_output=None, dry_run=False):
    """Migrate records declared as broken.

    Directly migrates the records declared as broken, e.g. if the dojson
    conversion script have been corrected.
    """
    for i, chunk in enumerate(chunker(
            record.marcxml for record in
            db.session.query(InspireProdRecords).filter_by(successful=False))):
        logger.info("Processed {} records".format(i * CHUNK_SIZE))
        chunk_broken_output = None
        if broken_output:
            chunk_broken_output = "{}-{}".format(broken_output, i)
        migrate_chunk.delay(chunk, chunk_broken_output, dry_run)


@shared_task(ignore_result=True)
def migrate(source, broken_output=None, dry_run=False, wait_for_results=False):
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
        chunk_broken_output = None
        if broken_output:
            chunk_broken_output = "{}-{}".format(broken_output, i)
        if wait_for_results:
            tasks.append(migrate_chunk.s(chunk, chunk_broken_output, dry_run))
        else:
            migrate_chunk.delay(chunk, chunk_broken_output, dry_run)

    if wait_for_results:
        job = group(tasks)
        result = job.apply_async()
        result.join()
        migrate_chunk.ignore_result = True
        print('All migration tasks have been completed.')


@shared_task(ignore_result=True)
def continuous_migration():
    """Task to continuously migrate what is pushed up by Legacy."""
    from redis import StrictRedis
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)

    try:
        while r.llen('legacy_records'):
            raw_record = r.lpop('legacy_records')
            if raw_record:
                # The record might be None, in case a parallel
                # continuous_migration task has already consumed the queue.
                raw_record = zlib.decompress(raw_record)
                record = marc_create_record(raw_record, keep_singletons=False)
                recid = int(record['001'][0])
                prod_record = InspireProdRecords(recid=recid)
                prod_record.marcxml = raw_record
                try:
                    with db.session.begin_nested():
                        errors, dummy = create_record(
                            record, force=True
                        )
                        logger.info(
                            "Successfully migrated record {}".format(recid))
                        prod_record.successful = True
                        prod_record.valid = not errors
                        prod_record.errors = errors
                        db.session.merge(prod_record)
                except Exception as err:
                    logger.error(
                        "Error when migrating record {}".format(recid))
                    logger.exception(err)
                    prod_record.successful = False
                    db.session.merge(prod_record)
    finally:
        db.session.commit()
        db.session.close()


def create_index_op(record):
    index, doc_type = _record_to_index(record)

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
def migrate_chunk(chunk, broken_output=None, dry_run=False):
    index_queue = []
    try:
        for raw_record in chunk:
            record = marc_create_record(raw_record, keep_singletons=False)
            recid = int(record['001'])
            if not dry_run:
                prod_record = InspireProdRecords(recid=recid)
                prod_record.marcxml = raw_record
            json_record = create_record(record)
            if dry_run:
                continue
            with db.session.begin_nested():
                try:
                    record = Record.create(json_record, id_=None)
                except ValidationError as e:
                    # Invalid record, will not get indexed
                    errors = "ValidationError: Record {0}: {1}".format(
                        recid, e
                    )
                    current_app.logger.warning(errors)
                    prod_record.valid = False
                    prod_record.errors = errors
                    db.session.merge(prod_record)
                    continue

                index_queue.append(create_index_op(record))

                # Create persistent identifier.
                inspire_recid_minter(str(record.id), json_record)

                prod_record.valid = True
                db.session.merge(prod_record)
        db.session.commit()
    finally:
        db.session.close()

    req_timeout = current_app.config['INDEXER_BULK_REQUEST_TIMEOUT']
    es_bulk(
        current_search_client,
        index_queue,
        stats_only=True,
        request_timeout=req_timeout,
    )


@shared_task()
def add_citation_counts(chunk_size=500, request_timeout=120):
    index, doc_type = schema_to_index('records/hep.json')

    def get_records_to_update_generator(citation_lookup):
        with click.progressbar(citation_lookup.items()) as items:
            for recid, citation_count in items:
                try:
                    uuid = PersistentIdentifier.query.filter(
                        PersistentIdentifier.object_type == "rec",
                        PersistentIdentifier.pid_value == str(recid)
                    ).one().object_uuid

                    yield {
                        '_op_type': 'update',
                        '_index': index,
                        '_type': doc_type,
                        '_id': str(uuid),
                        'doc': {'citation_count': citation_count}
                    }
                except NoResultFound:
                    continue

    click.echo("Extracting all citations...")

    # lookup dictionary where key: recid of the record
    # and value: number of records that cite that record
    citations_lookup = Counter()
    with click.progressbar(es_scan(
            current_search_client,
            query={
                "_source": "references.recid",
                "filter": {
                    "exists": {
                        "field": "references.recid"
                    }
                },
                "size": LARGE_CHUNK_SIZE
            },
            scroll=u'2m',
            index=index,
            doc_type=doc_type)) as records:
        for record in records:
            # update lookup dictionary based on references of the record
            if 'references' in record['_source']:
                unique_refs_ids = set()
                references = record['_source']['references']
                for reference in references:
                    recid = reference.get('recid')
                    if recid:
                        if isinstance(recid, list):
                            # Sometimes there is more than one recid in the
                            # reference.
                            recid = recid.pop()
                        unique_refs_ids.add(recid)

            for unique_refs_id in unique_refs_ids:
                citations_lookup[unique_refs_id] += 1

    click.echo("... DONE.")
    click.echo("Adding citation numbers...")

    success, failed = es_bulk(
        current_search_client,
        get_records_to_update_generator(citations_lookup),
        chunk_size=chunk_size,
        raise_on_exception=True,
        raise_on_error=True,
        request_timeout=request_timeout,
        stats_only=True)
    click.echo("... DONE: {} records updated with success. {} failures.".format(
        success, failed))


def create_record(record, force=True, dry_run=False):
    """Create record from marc21 model."""
    if _collection_in_record(record, 'institution'):
        json = institutions.do(record)
    elif _collection_in_record(record, 'experiment'):
        json = experiments.do(record)
    elif _collection_in_record(record, 'journals'):
        json = journals.do(record)
    elif _collection_in_record(record, 'hepnames'):
        json = hepnames.do(record)
    elif _collection_in_record(record, 'job') or \
            _collection_in_record(record, 'jobhidden'):
        json = jobs.do(record)
    elif _collection_in_record(record, 'conferences'):
        json = conferences.do(record)
    else:
        json = hep.do(record)

    if '$schema' in json:
        json['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(json['$schema'])
        )

    return json
    # control_number = json.get('control_number', json.get('recid'))
    # if control_number:
    #     control_number = int(control_number)

    # if force and control_number:
    #     # Searches if record already exists.
    #     with db.session.begin_nested():
    #         record = Record.get_record(control_number)
    #         if record is None:
    #             # Adds the record to the db session.
    #             record = Record.create(json, _id=control_number)
    #         else:
    #             record.update(json)
    #         record.commit()
    #     db.session.commit()
    #     logger.info("Elaborated record {}".format(control_number))
    #     return errors, dict(record)


@shared_task(ignore_result=True)
def reindex_holdingpen_object(obj_id):
    from invenio_workflows.signals import workflow_object_after_save
    from invenio_workflows import WorkflowObject

    obj = WorkflowObject.query.get(obj_id)
    workflow_object_after_save.send(obj)
