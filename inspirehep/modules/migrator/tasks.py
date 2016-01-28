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
import zlib

import re
import traceback

from celery.utils.log import get_task_logger

from dojson.contrib.marc21.utils import create_record as marc_create_record

from flask import current_app

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.hepnames import hepnames
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.journals import journals
from inspirehep.dojson.processors import _collection_in_record
from inspirehep.dojson.utils import legacy_export_as_marc
from inspirehep.dojson.utils import strip_empty_values

from inspirehep.modules.workflows.dojson import author_bibfield, bibfield
from inspirehep.modules.workflows.models import Payload

from invenio_celery import celery

from invenio_deposit.models import Deposition

from invenio_ext.es import es
from invenio_ext.sqlalchemy import db

from invenio_records.api import Record
from invenio_records.models import Record as RecordModel

from invenio_workflows.models import (
    BibWorkflowObject,
    ObjectVersion
)

from six import string_types, text_type

from .models import InspireProdRecords
from .utils import rename_object_action, reset_workflow_object_states


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


@celery.task(ignore_result=True)
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


@celery.task(ignore_result=True)
def migrate(source, broken_output=None, dry_run=False, wait_for_results=False):
    """Main migration function."""
    from celery.task.sets import TaskSet
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
    from invenio_celery.utils import disable_queue, enable_queue
    disable_queue("celery")

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
        job = TaskSet(tasks=tasks)
        result = job.apply_async()
        enable_queue("celery")
        result.join()
        migrate_chunk.ignore_result = True
        print('All migration tasks have been completed.')
    else:
        enable_queue("celery")


@celery.task(ignore_result=True)
def continuos_migration():
    """Task to continuosly migrate what is pushed up by Legacy."""
    from redis import StrictRedis
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    while r.llen('legacy_records'):
        try:
            record = r.lpop('legacy_records')
            if record:
                # The record might be None, in case a parallel
                # continuos_migration task has already consumed the queue.
                record = zlib.decompress(record)
                recid, dummy = create_record(record, force=True)
                logger.info("Successfully migrated record {}".format(recid))
        finally:
            db.session.close()


@celery.task(ignore_result=False, compress='zlib', acks_late=True)
def migrate_chunk(chunk, broken_output=None, dry_run=False):
    from flask_sqlalchemy import models_committed
    from invenio_records.receivers import record_modification
    from invenio_records.tasks.index import get_record_index
    from invenio.base.globals import cfg
    from elasticsearch.helpers import bulk as es_bulk
    from inspirehep.modules.citations.receivers import catch_citations_insert, add_citation_count_on_insert_or_update
    from invenio_records.signals import before_record_index, after_record_insert
    models_committed.disconnect(record_modification)
    after_record_insert.disconnect(catch_citations_insert)
    before_record_index.disconnect(add_citation_count_on_insert_or_update)

    records_to_index = []
    try:
        for record in chunk:
            recid = json = None
            try:
                recid, json = create_record(record,
                                            force=True, dry_run=dry_run)
                index = get_record_index(json) or \
                    cfg['SEARCH_ELASTIC_DEFAULT_INDEX']
                before_record_index.send(recid, json=json, index=index)
                json.update({'_index': index, '_type': 'record', '_id': recid, 'citation_count': 0})
                records_to_index.append(json)
            except Exception as err:
                logger.error("ERROR with record {} and json {}".format(recid, json))
                logger.exception(err)
                if broken_output:
                    broken_output_fd = open(broken_output, "a")
                    print(record, file=broken_output_fd)

        logger.info("Committing chunk")
        db.session.commit()
        logger.info("Sending chunk to elasticsearch")
        es_bulk(es, records_to_index, request_timeout=60)
    finally:
        models_committed.connect(record_modification)
        after_record_insert.connect(catch_citations_insert)
        before_record_index.connect(add_citation_count_on_insert_or_update)
        db.session.close()


@celery.task()
def add_citation_counts():
    from elasticsearch.helpers import bulk as es_bulk
    from elasticsearch.helpers import scan as es_scan
    from collections import Counter

    def get_records_to_update_generator(citation_lookup):
        for recid, citation_count in citation_lookup.iteritems():
            yield {'_op_type': 'update',
                   '_index': 'hep',
                   '_type': 'record',
                   '_id': recid,
                   'doc': {'citation_count': citation_count}
                   }

    logger.info("Extracting all citations...")

    # lookup dictionary where key: recid of the record
    # and value: number of records that cite that record
    citations_lookup = Counter()
    for i, record in enumerate(es_scan(
            es,
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
            index="hep",
            doc_type="record")):

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

        if (i + 1) % LARGE_CHUNK_SIZE == 0:
            logger.info("Extracted citations from {} records".format(i + 1))

    logger.info("... DONE.")
    logger.info("Adding citation numbers...")

    success, failed = es_bulk(es, get_records_to_update_generator(citations_lookup), raise_on_exception=False, raise_on_error=False, stats_only=True)
    logger.info("... DONE: {} records updated with success. {} failures.".format(success, failed))


def create_record(data, force=False, dry_run=False):
    record = marc_create_record(data)
    recid = None
    if '001' in record:
        recid = int(record['001'][0])
    if not dry_run and recid:
        prod_record = InspireProdRecords(recid=recid)
        prod_record.marcxml = data
    try:
        if _collection_in_record(record, 'institution'):
            json = strip_empty_values(institutions.do(record))
        elif _collection_in_record(record, 'experiment'):
            json = strip_empty_values(experiments.do(record))
        elif _collection_in_record(record, 'journals'):
            json = strip_empty_values(journals.do(record))
        elif _collection_in_record(record, 'hepnames'):
            json = strip_empty_values(hepnames.do(record))
        elif _collection_in_record(record, 'job') or \
                _collection_in_record(record, 'jobhidden'):
            json = strip_empty_values(jobs.do(record))
        elif _collection_in_record(record, 'conferences'):
            json = strip_empty_values(conferences.do(record))
        else:
            json = strip_empty_values(hep.do(record))
        if dry_run:
            return recid, json

        if force and any(key in json for key in ('control_number', 'recid')):
            try:
                control_number = json['control_number']
            except KeyError:
                control_number = json['recid']
            control_number = int(control_number)
            # Searches if record already exists.
            record = Record.get_record(control_number)
            if record is None:
                # Adds the record to the db session.
                rec = RecordModel(id=control_number)
                db.session.merge(rec)
                record = Record.create(json)
            else:
                record = Record(json, model=record.model)
                record.commit()
            if recid:
                prod_record.successful = True
                db.session.merge(prod_record)
            logger.info("Elaborated record {}".format(control_number))
            return control_number, dict(record)
    except Exception:
        if recid:
            prod_record.successful = False
            db.session.merge(prod_record)
            logger.exception("Error in elaborating record ID {}".format(recid))
        raise


@celery.task(ignore_result=True)
def migrate_workflow_object(obj_id):
    try:
        obj = BibWorkflowObject.query.get(obj_id)
        rename_object_action(obj)
        if obj.workflow.name == "process_record_arxiv":
            metadata = obj.get_data()
            if isinstance(metadata, string_types):
                # Ignore records that have string as data
                return
            if 'drafts' in metadata:
                # New data model detected, just save and exit
                obj.save()
                return
            if hasattr(metadata, 'dumps'):
                metadata = metadata.dumps(clean=True)
            obj.data = bibfield.do(metadata)
            payload = Payload.create(
                type=obj.workflow.name,
                workflow_object=obj
            )
            payload.save()
        elif obj.workflow.name == "literature":
            d = Deposition(obj)
            sip = d.get_latest_sip()
            if sip:
                sip.metadata = bibfield.do(sip.metadata)
                sip.package = legacy_export_as_marc(hep2marc.do(sip.metadata))
                d.save()
        elif obj.workflow.name in ("authornew", "authorupdate"):
            data = obj.get_data()
            obj.set_data(author_bibfield.do(data))
            obj.save()
        else:
            obj.save()  # To update and trigger indexing
        reset_workflow_object_states(obj)
    except Exception as err:
        current_app.logger.error("Problem migrating record {0}".format(obj_id))
        current_app.logger.exception(err)
        msg = "Error: %r\n%s" % \
              (err, traceback.format_exc())
        obj.set_error_message(str(err), msg)
        obj.save(version=ObjectVersion.ERROR)
        raise


@celery.task(ignore_result=True)
def reindex_holdingpen_object(obj_id):
    from invenio_workflows.signals import workflow_object_saved

    obj = BibWorkflowObject.query.get(obj_id)
    workflow_object_saved.send(obj)
