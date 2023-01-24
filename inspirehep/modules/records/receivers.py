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

"""Records receivers."""

from __future__ import absolute_import, division, print_function

import uuid
import logging
from copy import deepcopy

from flask import current_app
from flask_sqlalchemy import models_committed
from elasticsearch import NotFoundError
from time_execution import time_execution

from invenio_records.models import RecordMetadata
from invenio_records.signals import (
    after_record_update,
    before_record_insert,
    before_record_update,
)

from inspirehep.modules.orcid import (
    push_access_tokens,
    tasks as orcid_tasks,
)
from inspirehep.modules.orcid.utils import get_orcids_for_push
from inspirehep.modules.pidstore.utils import get_pid_type_from_schema
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.errors import MissingInspireRecordError
from inspirehep.modules.records.serializers.schemas.json import RecordMetadataSchemaV1
from inspirehep.modules.records.tasks import index_modified_citations_from_record
from inspirehep.modules.records.utils import (
    is_author,
    is_book,
    is_data,
    is_experiment,
    is_hep,
    is_institution,
    is_journal,
    populate_abstract_source_suggest,
    populate_affiliation_suggest,
    populate_author_count,
    populate_author_suggest,
    populate_authors_full_name_unicode_normalized,
    populate_authors_name_variations,
    populate_bookautocomplete,
    populate_citations_count,
    populate_earliest_date,
    populate_experiment_suggest,
    populate_inspire_document_type,
    populate_name_variations,
    populate_number_of_references,
    populate_recid_from_ref,
    populate_title_suggest,
    populate_facet_author_name,
    populate_ui_display,
)
from invenio_indexer.api import RecordIndexer

LOGGER = logging.getLogger(__name__)


@before_record_insert.connect
@before_record_update.connect
def assign_uuid(sender, record, *args, **kwargs):
    """Assign a UUID to each signature of a Literature record."""
    if not is_hep(record):
        return

    authors = record.get('authors', [])

    for author in authors:
        if 'uuid' not in author:
            author['uuid'] = str(uuid.uuid4())


@after_record_update.connect
@time_execution
def push_to_orcid(sender, record, *args, **kwargs):
    """If needed, queue the push of the new changes to ORCID."""
    if not current_app.config['FEATURE_FLAG_ENABLE_ORCID_PUSH']:
        LOGGER.warning('ORCID push feature flag not enabled')
        return

    if not is_hep(record):
        return

    # Ensure there is a control number. This is not always the case because of broken store_record.
    if 'control_number' not in record:
        return

    orcids = get_orcids_for_push(record)
    orcids_and_tokens = push_access_tokens.get_access_tokens(orcids)

    kwargs_to_pusher = dict(record_db_version=record.model.version_id)

    for orcid, access_token in orcids_and_tokens:
        orcid_tasks.orcid_push.apply_async(
            queue='orcid_push',
            kwargs={
                'orcid': orcid,
                'rec_id': record['control_number'],
                'oauth_token': access_token,
                'kwargs_to_pusher': kwargs_to_pusher,
            },
        )


@after_record_update.connect
def enhance_record(sender, record, *args, **kwargs):
    """Enhance the record for ES"""
    if not isinstance(record, InspireRecord):
        raise MissingInspireRecordError("Record is not InspireRecord!")
    enhanced_record = deepcopy(record)
    enhance_before_index(enhanced_record)
    record.model._enhanced_record = enhanced_record


@models_committed.connect
def index_after_commit(sender, changes):
    """Index a record in ES after it was committed to the DB.

    This cannot happen in an ``after_record_commit`` receiver from Invenio-Records
    because, despite the name, at that point we are not yet sure whether the record
    has been really committed to the DB.
    """
    indexer = RecordIndexer()
    for model_instance, change in changes:
        if isinstance(model_instance, RecordMetadata):
            if change in ('insert', 'update') and not model_instance.json.get("deleted"):
                if hasattr(model_instance, '_enhanced_record'):
                    record = model_instance._enhanced_record
                else:
                    record = model_instance.json
                indexer.index(InspireRecord(record, model_instance))
            else:
                try:
                    indexer.delete(InspireRecord(
                        model_instance.json, model_instance))
                except NotFoundError:
                    # Record not found in ES
                    LOGGER.debug('Record %s not found in ES',
                                 model_instance.json.get("id"))
                    pass

            pid_type = get_pid_type_from_schema(model_instance.json['$schema'])
            pid_value = model_instance.json['control_number']
            db_version = model_instance.version_id

            index_modified_citations_from_record.delay(pid_type, pid_value, db_version)


def enhance_before_index(record):
    """Run all the receivers that enhance the record for ES in the right order.

    .. note::

       ``populate_recid_from_ref`` **MUST** come before ``populate_bookautocomplete``
       because the latter puts a JSON reference in a completion _source, which
       would be expanded to an incorrect ``_source_recid`` by the former.

    """
    populate_recid_from_ref(record)

    if is_hep(record):
        populate_abstract_source_suggest(record)
        populate_earliest_date(record)
        populate_author_count(record)
        populate_authors_full_name_unicode_normalized(record)
        populate_inspire_document_type(record)
        populate_name_variations(record)
        populate_number_of_references(record)
        populate_citations_count(record)
        populate_facet_author_name(record)
        populate_ui_display(record, RecordMetadataSchemaV1)

        if is_book(record):
            populate_bookautocomplete(record)

    elif is_author(record):
        populate_authors_name_variations(record)
        populate_author_suggest(record)

    elif is_institution(record):
        populate_affiliation_suggest(record)

    elif is_experiment(record):
        populate_experiment_suggest(record)

    elif is_journal(record):
        populate_title_suggest(record)

    elif is_data(record):
        populate_citations_count(record)
