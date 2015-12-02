# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, print_function

import gzip

import re

from celery.utils.log import get_task_logger

from flask import current_app
from dojson.contrib.marc21.utils import create_record as marc_create_record

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.hep import hep
from inspirehep.dojson.hepnames import hepnames
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.journals import journals
from inspirehep.dojson.processors import _collection_in_record

from invenio_celery import celery

from invenio_ext.es import es
from invenio_ext.sqlalchemy import db

from invenio_records.api import Record as record_api
from invenio_records.models import Record

from six import text_type

from .models import InspireProdRecords

logger = get_task_logger(__name__)

CHUNK_SIZE = 1000

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
def migrate(source, broken_output=None, dry_run=False):
    """Main migration function."""
    if source.endswith('.gz'):
        fd = gzip.open(source)
    else:
        fd = open(source)

    for i, chunk in enumerate(chunker(split_stream(fd), CHUNK_SIZE)):
        logger.info("Processed {} records".format(i * CHUNK_SIZE))
        chunk_broken_output = None
        if broken_output:
            chunk_broken_output = "{}-{}".format(broken_output, i)
        migrate_chunk.delay(chunk, chunk_broken_output, dry_run)


@celery.task(ignore_result=True)
def continuos_migration():
    """Task to continuosly migrate what is pushed up by Legacy."""
    from redis import StrictRedis
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    while r.llen('legacy_records'):
        record = r.lpop('legacy_records')
        create_record(record, force=True)


@celery.task(ignore_result=True, compress='zlib', acks_late=True)
def migrate_chunk(chunk, broken_output=None, dry_run=False):
    from flask_sqlalchemy import models_committed
    from invenio_records.receivers import record_modification
    from invenio_records.tasks.index import get_record_index
    from invenio.base.globals import cfg
    from elasticsearch.helpers import bulk as es_bulk
    from invenio_records.signals import before_record_index
    models_committed.disconnect(record_modification)

    records_to_index = []
    try:
        for record in chunk:
            try:
                recid, json = create_record(record,
                                            force=True, dry_run=dry_run)
                index = get_record_index(json) or \
                    cfg['SEARCH_ELASTIC_DEFAULT_INDEX']
                before_record_index.send(recid, json=json)
                json.update({'_index': index, '_type': 'record', '_id': recid})
                records_to_index.append(json)
            except Exception as err:
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


@celery.task(ignore_result=True)
def add_citation_counts():
    from elasticsearch.helpers import bulk as es_bulk
    from elasticsearch.helpers import scan as es_scan
    from collections import Counter

    # list of update-jsons for each record
    records_to_update = []

    # lookup dictionary where key: recid of the record
    # and value: number of records that cite that record
    citations_lookup = Counter()
    for record in es_scan(
            es,
            query={
                "_source": "references.recid",
                "filter": {
                    "exists": {
                        "field": "references.recid"
                    }
                },
                "size": CHUNK_SIZE
            },
            scroll=u'1m',
            index="hep",
            doc_type="record"):

        # update lookup dictionary based on references of the record
        if 'references' in record['_source']:
            references = record['_source']['references']
            for reference in references:
                recid = unicode(reference.get('recid'))
                if recid is not None:
                    citations_lookup[recid] += 1

        # prepare json to update the record
        json = {'_op_type': 'update',
                '_index': 'hep',
                '_type': 'record',
                '_id': record['_id'],
                }
        records_to_update.append(json)

    for json in records_to_update:
        citation_count = citations_lookup[json['_id']]
        json.update({'doc': {'citation_count': citation_count}})

    for chunk in chunker(records_to_update, CHUNK_SIZE):
        es_bulk(es, chunk)


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
        if dry_run:
            return recid, json

        if force and any(key in json for key in ('control_number', 'recid')):
            try:
                control_number = json['control_number']
            except KeyError:
                control_number = json['recid']
            control_number = int(control_number)
            # Searches if record already exists.
            record = record_api.get_record(control_number)
            if record is None:
                # Adds the record to the db session.
                rec = Record(id=control_number)
                db.session.add(rec)
                record = record_api.create(json)
            else:
                record.update(json)
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
