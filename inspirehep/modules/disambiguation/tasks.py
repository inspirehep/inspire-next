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

"""Celery tasks provided by Disambiguation module."""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from celery import current_app, shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import distinct
from sqlalchemy.orm.exc import StaleDataError

from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_indexer.signals import before_record_index
from invenio_records import Record

from inspirehep.modules.disambiguation.beard import make_beard_clusters
from inspirehep.modules.disambiguation.logic import process_clusters
from inspirehep.modules.disambiguation.models import DisambiguationRecord
from inspirehep.modules.disambiguation.search import (
    create_beard_record,
    create_beard_signatures,
    get_blocks_from_record,
    get_records_from_block,
)
from inspirehep.modules.disambiguation.receivers import (
    append_updated_record_to_queue,
)

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def disambiguation_daemon():
    """Run disambiguation daemon as Celery task.

    The method is invoked by Celery beat schedule and can be
    configured from 'config.py'.

    The method collects the records UUIDs from the database,
    dispatch each of the phonetic blocks found within
    these records to Celery workers and finally dumps the records.
    """
    phonetic_blocks = set()

    # Get the records classified for clustering.
    records_to_cluster = DisambiguationRecord.query.distinct(
        "disambiguation_records.record_id").all()

    # For each record get the phonetic blocks.
    for record in records_to_cluster:
        phonetic_blocks.update(
            get_blocks_from_record(record.record_id))

    # For each phonetic block, run clustering job.
    while phonetic_blocks:
        current_app.send_task('inspirehep.modules.disambiguation.tasks.'
                              'disambiguation_clustering',
                              args=(phonetic_blocks.pop(),))

    # Clear the database table.
    DisambiguationRecord.query.delete()
    db.session.commit()
    db.session.close()


@shared_task(ignore_result=True)
def disambiguation_clustering(phonetic_block):
    """Cluster phonetic blocks in parallel.

    The method receives a phonetic block as an argument.
    In order to proceed with clustering, the method
    creates two lists representing records containing given
    phonetic block (required by Beard) and signatures of the block.
    """
    try:
        logger.info("Clustering: %s" % phonetic_block)

        records = []
        signatures = []

        # Get all the records containing specific phonetic block.
        records_ids = get_records_from_block(phonetic_block)

        # Create records and signatures in Beard readable format.
        for record_id in records_ids:
            records.append(create_beard_record(record_id))
            signatures.extend(create_beard_signatures(
                record_id, phonetic_block))

        # Dispatch clustering job to Beard Celery service.
        try:
            clusters_matched, clusters_created = make_beard_clusters(
                records, signatures).get()
        except AttributeError:
            clusters_matched = {}
            clusters_created = {}

        # Update recids of signatures to existing profiles.
        if clusters_matched:
            for profile_recid, beard_uuids in clusters_matched.iteritems():
                process_clusters(beard_uuids, signatures, profile_recid)

        # Create new profiles.
        if clusters_created:
            for beard_uuids in list(clusters_created.values()):
                process_clusters(beard_uuids, signatures)

        db.session.commit()
    finally:
        db.session.close()


@shared_task
def update_authors_recid(record_id, uuid, profile_recid):
    """Update author profile for a given signature.

    The method receives UUIDs representing record and signature
    respectively together with an author profile recid.
    The new recid will be placed in the signature with the given
    UUID.

    :param record_id:
        A string representing UUID of a given record.

        Example:
            record_id = "a5afb151-8f75-4e91-8dc1-05e7e8e8c0b8"

    :param uuid:
        A string representing UUID of a given signature.

        Example:
            uuid = "c2f432bd-2f52-4c16-ac66-096f168c762f"

    :param profile_recid:
        A string representing author profile recid, that
        updated signature should point to.

        Example:
            profile_recid = "1"
    """
    try:
        record = Record.get_record(record_id)
        update_flag = False

        for author in record['authors']:
            if author['uuid'] == uuid:
                author['recid'] = str(profile_recid)
                update_flag = True

        if update_flag:
            # Disconnect the signal on insert of a new record.
            before_record_index.disconnect(append_updated_record_to_queue)

            # Update the record in the database.
            record.commit()
            db.session.commit()

            # Update the record in Elasticsearch.
            indexer = RecordIndexer()
            indexer.index_by_id(record.id)
    except StaleDataError as exc:
        raise update_authors_recid.retry(exc=exc)
    finally:
        # Reconnect the disconnected signal.
        before_record_index.connect(append_updated_record_to_queue)

    # Report.
    logger.info("Updated signature %s with profile %s",
                uuid, profile_recid)
