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

"""Tasks to check if the incoming record already exist."""

from __future__ import absolute_import, division, print_function

import datetime
import os
import re
import traceback
import backoff
from functools import wraps
from itertools import chain

import requests
import six
from flask import current_app
from simplejson import JSONDecodeError

from inspire_utils.record import get_value
from inspirehep.utils.datefilter import date_older_than
from inspirehep.utils.record import get_arxiv_categories, get_arxiv_id

from ..utils import with_debug_logging


@with_debug_logging
@backoff.on_exception(backoff.expo, Exception, max_tries=7)
def search(query):
    """Perform a search and returns the matching ids."""
    params = dict(p=query, of='id')

    try:
        return requests.get(
            current_app.config["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            params=params
        ).json()
    except requests.ConnectionError:
        current_app.logger.error(
            "Error connecting to remote server:\n {0}".format(
                traceback.format_exc()
            )
        )
        raise
    except (ValueError, JSONDecodeError):
        current_app.logger.error(
            "Error decoding results from remote server:\n {0}".format(
                traceback.format_exc()
            )
        )
        raise


@with_debug_logging
def match_by_arxiv_id(record):
    """Match by arXiv identifier."""
    arxiv_id = get_arxiv_id(record)

    if arxiv_id:
        query = '035:"{0}"'.format(arxiv_id)
        return search(query)

    return list()


@with_debug_logging
def match_by_doi(record):
    """Match by DOIs."""
    dois = get_value(record, 'dois.value', [])

    result = set()
    for doi in dois:
        query = '0247:"{0}"'.format(doi)
        result.update(search(query))

    return list(result)


@with_debug_logging
def match_legacy_inspire(obj, eng):
    """Return True if the record already exists in INSPIRE.

    Searches by arXiv identifier and DOI, updates extra_data with results.
    """
    response = list(
        set(match_by_arxiv_id(obj.data)) | set(match_by_doi(obj.data))
    )

    base_url = current_app.config["LEGACY_ROBOTUPLOAD_URL"]
    if not re.match('^https?://', base_url):
        base_url = 'http://{}'.format(base_url)
    obj.extra_data['record_matches'] = {
        "recids": [str(recid) for recid in response],
        "records": [],
        "base_url": os.path.join(base_url, 'record')
    }
    return bool(obj.extra_data['record_matches']['recids'])


def match_with_invenio_matcher(queries=None, index="records-hep", doc_type="hep"):
    """Match record using Invenio Matcher."""
    @with_debug_logging
    @wraps(match_with_invenio_matcher)
    def _match_with_invenio_matcher(obj, eng):
        from invenio_matcher.api import match as _match

        if queries is None:
            queries_ = [
                {'type': 'exact', 'match': 'dois.value'},
                {'type': 'exact', 'match': 'arxiv_eprints.value'}
            ]
        else:
            queries_ = queries

        record_matches = {
            "recids": [],
            "records": [],
            "base_url": os.path.join(
                current_app.config["SERVER_NAME"],
                'record'
            )
        }

        record = {}
        record['dois.value'] = get_value(obj.data, 'dois.value')
        record['arxiv_eprints.value'] = get_value(
            obj.data, 'arxiv_eprints.value'
        )
        for matched_record in _match(
            record,
            queries=queries_,
            index=index,
            doc_type=doc_type
        ):
            matched_recid = matched_record.record.get('id')
            record_matches['recids'].append(matched_recid)
            record_matches['records'].append({
                "source": matched_record.record.dumps(),
                "score": matched_record.score
            })

        if len(record_matches['recids']) > 0:
            obj.extra_data["record_matches"] = record_matches
            return True
        return False
    return _match_with_invenio_matcher


@with_debug_logging
def is_too_old(record, days_ago=5):
    """Return True if the record is more than days_ago days old.

    If the record is older then it's probably an update of an earlier
    record, and we don't want those.
    """
    date_format = "%Y-%m-%d"
    earliest_date = record.get('earliest_date', '')
    if not earliest_date:
        earliest_date = record.get('preprint_date', '')

    if earliest_date:
        try:
            parsed_date = datetime.datetime.strptime(
                earliest_date,
                date_format,
            )

        except ValueError as err:
            raise ValueError(
                (
                    'Unrecognized earliest_date format "%s", valid formats is '
                    '%s: %s'
                ) % (earliest_date, date_format, err)
            )

        if not date_older_than(
            parsed_date,
            datetime.datetime.utcnow(),
            days=days_ago,
        ):
            return False
    return True


@with_debug_logging
def article_exists(obj, eng):
    """Check if an article exist in the system."""
    # For efficiency check special mark key.
    if obj.extra_data.get('match-found', False):
        return True
    # Use matcher if not on production
    if not current_app.config.get('PRODUCTION_MODE'):
        if match_with_invenio_matcher(index="records-hep", doc_type="hep")(obj, eng):
            obj.log.info("Record already exists in INSPIRE (using matcher).")
            return True
    else:
        obj.log.warning("Remote match is deprecated.")
        if match_legacy_inspire(obj, eng):
            obj.log.info("Record already exists in INSPIRE.")
            return True
    return False


@with_debug_logging
def is_being_harvested_on_legacy(record):
    """Return True if the record is being harvested on Legacy.

    If the record belongs to one of the CORE arXiv categories then it
    is already being harvested on Legacy.
    """
    arxiv_categories = get_arxiv_categories(record)
    legacy_categories = current_app.config.get(
        'ARXIV_CATEGORIES_ALREADY_HARVESTED_ON_LEGACY', [])

    return len(set(arxiv_categories) & set(legacy_categories)) > 0


@with_debug_logging
def already_harvested(obj, eng):
    """Check if record is already harvested."""
    if is_being_harvested_on_legacy(obj.data):
        obj.log.info((
            'Record with arXiv id {arxiv_id} is'
            ' already being harvested on Legacy.'
        ).format(arxiv_id=get_arxiv_id(obj.data)))
        return True
    return False


@with_debug_logging
def pending_in_holding_pen(obj, eng):
    """Check if a record exists in HP by looking in given KB."""
    from elasticsearch_dsl import Q
    from invenio_db import db
    from invenio_search import RecordsSearch
    from invenio_workflows.models import WorkflowObjectModel, ObjectStatus

    config = current_app.config['WORKFLOWS_UI_REST_ENDPOINT']
    index = config.get('search_index')
    doc_type = config.get('search_type')
    searcher = RecordsSearch(
        index=index, doc_type=doc_type
    ).params(version=True)

    identifiers = []
    for field, lookup in six.iteritems(
            current_app.config.get("HOLDING_PEN_MATCH_MAPPING", {})):
        # Add quotes around to make the search exact
        identifiers += ['{0}:"{1}"'.format(field, i)
                        for i in get_value(obj.data, lookup, [])]
    # Search for any existing record in Holding Pen, exclude self
    if identifiers:
        search = searcher.query(Q('query_string',
                                query=" OR ".join(identifiers),
                                allow_leading_wildcard=False))
        search_result = search.execute()
        id_list = [int(hit.id) for hit in search_result.hits]
        matches_excluding_self = set(id_list) - set([obj.id])
        if matches_excluding_self:
            obj.extra_data["holdingpen_ids"] = list(matches_excluding_self)
            pending_records = db.session.query(
                WorkflowObjectModel
            ).with_entities(WorkflowObjectModel.id).filter(
                WorkflowObjectModel.status != ObjectStatus.COMPLETED,
                WorkflowObjectModel.id.in_(matches_excluding_self)
            ).all()
            if pending_records:
                pending_ids = [o[0] for o in pending_records]
                obj.extra_data['pending_holdingpen_ids'] = pending_ids
                obj.log.info(
                    "Pending records already found in Holding Pen ({0})"
                    .format(
                        pending_ids
                    )
                )
                return True
    return False


@with_debug_logging
def delete_self_and_stop_processing(obj, eng):
    """Delete both versions of itself and stops the workflow."""
    from invenio_db import db
    db.session.delete(obj.model)
    eng.skip_token()


@with_debug_logging
def stop_processing(obj, eng):
    """Stop processing for object and return as completed."""
    eng.stopProcessing()


@with_debug_logging
def update_existing_workflow_object(obj, eng):
    """Update the data of the old object with the new data."""
    from invenio_workflows import workflow_object_class

    holdingpen_ids = obj.extra_data.get("holdingpen_ids", [])
    for matched_id in holdingpen_ids:
        existing_obj = workflow_object_class.get(matched_id)
        if (
                obj.data.get('acquisition_source') and
                existing_obj.data.get('acquisition_source')
        ):
            if (
                    obj.data['acquisition_source'].get('method') ==
                    existing_obj.data['acquisition_source'].get('method')
            ):
                # Method is the same, update obj
                existing_obj.data.update(obj.data)
                existing_obj.save()
                break
    else:
        msg = "Cannot update old object, non valid ids: %s"
        obj.log.error(msg, holdingpen_ids)
        raise Exception(msg % holdingpen_ids)
