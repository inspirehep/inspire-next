# -*- coding: utf-8 -*-
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, print_function

from celery.utils.log import get_task_logger

import gzip
import re

from six import text_type

from dojson.contrib.marc21.utils import create_record as marc_create_record
from invenio_celery import celery
from invenio_records.api import Record as record_api
from invenio_records.models import Record

from inspire.dojson.conferences import conferences
from inspire.dojson.experiments import experiments
from inspire.dojson.hep import hep
from inspire.dojson.hepnames import hepnames
from inspire.dojson.institutions import institutions
from inspire.dojson.jobs import jobs
from inspire.dojson.journals import journals
from inspire.dojson.processors import _collection_in_record
from invenio_ext.sqlalchemy import db
from invenio_ext.es import es
from invenio_records.recordext.functions.get_record_collections import update_collections

from .models import InspireProdRecords

logger = get_task_logger(__name__)

CHUNK_SIZE = 1000

split_marc = re.compile('<record.*?>.*?</record>', re.DOTALL)


def chunker(iterable, chunksize):
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
                recid, json = create_record(record, force=True, dry_run=dry_run)
                index = get_record_index(json) or cfg['SEARCH_ELASTIC_DEFAULT_INDEX']
                before_record_index.send(recid, json=json)
                json.update({'_index': index, '_type': 'record', '_id': recid})
                records_to_index.append(json)
            except Exception:
                if broken_output:
                    broken_output_fd = open(broken_output, "a")
                    print(record, file=broken_output_fd)
        logger.info("Committing chunk")
        db.session.commit()
        logger.info("Sending chunk to elasticsearch")
        es_bulk(es, records_to_index)
    finally:
        models_committed.connect(record_modification)


def create_record(data, force=False, dry_run=False):
    record = marc_create_record(data)
    recid = None
    if '001' in record:
        recid = int(record['001'][0])
    if not dry_run and recid:
        prod_record = InspireProdRecords(recid=recid, marcxml=data)
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
