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

"""Tasks related to user actions."""

from __future__ import absolute_import, division, print_function

import logging

import re
from elasticsearch_dsl import Q, Search
from invenio_search import current_search_client
from inspirehep.modules.refextract.tasks import create_journal_kb_dict
from urlparse import urljoin
from urllib import quote

import sys
import time
import backoff

import json
import requests
from copy import deepcopy
from functools import wraps
from six import reraise
from itertools import chain

from flask import current_app
from jsonschema.exceptions import ValidationError
from parsel import Selector
from six.moves.urllib.parse import urlparse
from sqlalchemy import (
    JSON,
    String,
    cast,
    type_coerce,
)
from werkzeug import secure_filename

from invenio_db import db
from invenio_workflows import ObjectStatus, workflow_object_class, start
from invenio_workflows.errors import WorkflowsError
from invenio_records.models import RecordMetadata
from inspire_json_merger.api import merge
from inspire_json_merger.config import GrobidOnArxivAuthorsOperations
from inspire_schemas.builders import LiteratureBuilder
from inspire_schemas.readers import LiteratureReader
from inspire_schemas.utils import validate, classify_field
from inspire_utils.record import get_value
from inspire_utils.dedupers import dedupe_list

from inspirehep.modules.pidstore.utils import get_pid_type_from_schema
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.modules.records.utils import get_linked_records_in_field
from inspirehep.modules.workflows.tasks.refextract import (
    extract_references_from_pdf_url,
    extract_references_from_raw_refs,
    extract_references_from_pdf,
    extract_references_from_text,
    extract_references_from_text_data,
)
from inspirehep.modules.workflows.utils import _get_headers_for_hep_root_table_request, create_error
from inspirehep.modules.workflows.errors import BadGatewayError, MissingRecordControlNumber
from inspirehep.modules.workflows.utils import (
    copy_file_to_workflow,
    download_file_to_workflow,
    get_document_url_for_reference_extraction,
    get_document_in_workflow,
    get_resolve_validation_callback_url,
    get_validation_errors,
    log_workflows_action,
    with_debug_logging, check_mark, set_mark, get_mark, get_record_from_hep,
    delete_empty_key
)
from inspirehep.modules.workflows.utils.grobid_authors_parser import GrobidAuthors
from inspirehep.utils.url import is_pdf_link


LOGGER = logging.getLogger(__name__)


EXPERIMENTAL_ARXIV_CATEGORIES = [
    'astro-ph',
    'astro-ph.CO',
    'astro-ph.EP',
    'astro-ph.GA',
    'astro-ph.HE',
    'astro-ph.IM',
    'astro-ph.SR',
    'hep-ex',
    'nucl-ex',
    'physics.ins-det',
]
EXPERIMENTAL_INSPIRE_CATEGORIES = [
    'Astrophysics',
    'Experiment-HEP',
    'Experiment-Nucl',
    'Instrumentation',
]

GROBID_EXCEPTIONS = (
    BadGatewayError,
    requests.exceptions.RequestException,
)


def mark(key, value):
    """Mark the workflow object by putting a value in a key in extra_data.

    Note:
        Important. Committing a change to the database before saving the
        current workflow object will wipe away any content in ``extra_data``
        not saved previously.

    Args:
        key: the key used to mark the workflow
        value: the value assigned to the key

    Return:
        func: the decorator to decorate a workflow object
    """
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        return set_mark(obj, key, value)

    _mark.__doc__ = 'Mark the workflow object with %s:%s.' % (key, value)
    return _mark


def is_marked(key):
    """Check if the workflow object has a specific mark."""
    @with_debug_logging
    @wraps(is_marked)
    def _mark(obj, eng):
        return check_mark(obj, key)

    _mark.__doc__ = 'Check if the workflow object has the mark %s.' % key
    return _mark


@with_debug_logging
def is_record_accepted(obj, *args, **kwargs):
    """Check if the record was approved."""
    return obj.extra_data.get("approved", False)


@with_debug_logging
def shall_halt_workflow(obj, *args, **kwargs):
    """Check if the workflow shall be halted."""
    return obj.extra_data.get("halt_workflow", False)


def in_production_mode(*args, **kwargs):
    """Check if we are in production mode"""
    return current_app.config.get(
        "PRODUCTION_MODE", False
    )


@with_debug_logging
def add_core(obj, eng):
    """Mark a record as CORE if it was approved as CORE."""
    if 'core' in obj.extra_data:
        obj.data['core'] = obj.extra_data['core']


def is_core(obj, eng):
    """Check if workflow is CORE."""
    return obj.data.get("core")


def halt_record(action=None, message=None):
    """Halt the workflow for approval with optional action."""
    @with_debug_logging
    @wraps(halt_record)
    def _halt_record(obj, eng):
        eng.halt(
            action=obj.extra_data.get("halt_action") or action,
            msg=obj.extra_data.get("halt_message") or message,
        )

    _halt_record.__doc__ = (
        'Halt the workflow object, action=%s, message=%s' % (action, message)
    )
    _halt_record.description = '"%s"' % (message or 'unspecified')
    return _halt_record


def reject_record(message):
    """Reject record with message."""
    @with_debug_logging
    @wraps(reject_record)
    def _reject_record(obj, *args, **kwargs):
        relevance_prediction = obj.extra_data.get("relevance_prediction")
        log_workflows_action(
            action="reject_record",
            relevance_prediction=relevance_prediction,
            object_id=obj.id,
            user_id=None,
            source="workflow",
        )

        obj.extra_data["approved"] = False
        obj.extra_data["reason"] = message
        obj.log.info(message)

    _reject_record.__doc__ = 'Reject the record, message=%s' % message
    return _reject_record


def _is_auto_rejected(workflow_obj):
    relevance_prediction = workflow_obj.extra_data.get('relevance_prediction')
    classification_results = workflow_obj.extra_data.get('classifier_results', {})
    fulltext_used = classification_results.get('fulltext_used')
    if not relevance_prediction or not classification_results or not fulltext_used:
        return False

    decision = relevance_prediction.get('decision')
    all_class_results = classification_results.get('complete_output')
    core_keywords = all_class_results.get('core_keywords')

    return decision.lower() == 'rejected' and len(core_keywords) == 0


def _is_auto_approved(workflow_obj):
    return workflow_obj.extra_data.get('auto-approved', False)


def _is_journal_coverage_full(workflow_obj):
    if workflow_obj.extra_data.get('journal_coverage') == 'full':
        return True


@with_debug_logging
def is_record_relevant(obj, eng):
    """Shall we halt this workflow for potential acceptance or just reject?"""
    # We do not auto-reject any user submissions
    if is_submission(obj, eng):
        return True

    if _is_journal_coverage_full(workflow_obj=obj):
        return True

    if _is_auto_approved(workflow_obj=obj):
        return True

    if _is_auto_rejected(workflow_obj=obj):
        return False

    return True


@with_debug_logging
def is_experimental_paper(obj, eng):
    """Check if a workflow contains an experimental paper.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: whether the workflow contains an experimental paper.

    """
    reader = LiteratureReader(obj.data)
    arxiv_categories = reader.arxiv_categories
    inspire_categories = reader.inspire_categories

    has_experimental_arxiv_category = len(
        set(arxiv_categories) & set(EXPERIMENTAL_ARXIV_CATEGORIES)) > 0
    has_experimental_inspire_category = len(
        set(inspire_categories) & set(EXPERIMENTAL_INSPIRE_CATEGORIES)) > 0

    return has_experimental_arxiv_category or has_experimental_inspire_category


@with_debug_logging
def is_arxiv_paper(obj, eng):
    """Check if a workflow contains a paper from arXiv.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: whether the workflow contains a paper from arXiv.

    """
    reader = LiteratureReader(obj.data)
    method = reader.method
    source = reader.source

    is_submission_with_arxiv = method == 'submitter' and 'arxiv_eprints' in obj.data
    is_harvested_from_arxiv = method == 'hepcrawl' and source.lower() == 'arxiv'

    return is_submission_with_arxiv or is_harvested_from_arxiv


@with_debug_logging
def is_submission(obj, eng):
    """Check if a workflow contains a submission.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        bool: whether the workflow contains a submission.

    """
    source = LiteratureReader(obj.data).method
    return source == 'submitter'


def validate_record(schema):
    @with_debug_logging
    @wraps(validate_record)
    def _validate_record(obj, eng):
        try:
            validate(obj.data, schema)
        except ValidationError:
            obj.extra_data['validation_errors'] = \
                get_validation_errors(obj.data, schema)
            obj.extra_data['callback_url'] = \
                get_resolve_validation_callback_url()
            obj.save()
            db.session.commit()
            reraise(*sys.exc_info())

    _validate_record.__doc__ = 'Validate the workflow record against the "%s" schema.' % schema
    return _validate_record


@with_debug_logging
def populate_journal_coverage(obj, eng):
    """Populate ``journal_coverage`` from the Journals DB.

    Searches in the Journals DB if the current article was published in a
    journal that we harvest entirely, then populates the ``journal_coverage``
    key in ``extra_data`` with ``'full'`` if it was, ``'partial' otherwise.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    journals = replace_refs(get_value(obj.data, 'publication_info.journal_record'), 'db')
    if not journals:
        return

    if any(get_value(journal, '_harvesting_info.coverage') == 'full' for journal in journals):
        obj.extra_data['journal_coverage'] = 'full'
    else:
        obj.extra_data['journal_coverage'] = 'partial'


@with_debug_logging
def fix_submission_number(obj, eng):
    """Ensure that the submission number contains the workflow object id.

    Unlike form submissions, records coming from HEPCrawl can't know yet which
    workflow object they will create, so they use the crawler job id as their
    submission number. We would like to have there instead the id of the workflow
    object from which they came from, so that, given a record, we can link to their
    original Holding Pen entry.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    method = get_value(obj.data, 'acquisition_source.method', default='')
    if method == 'hepcrawl':
        obj.data['acquisition_source']['submission_number'] = str(obj.id)


@with_debug_logging
def populate_submission_document(obj, eng):
    submission_pdf = obj.extra_data.get('submission_pdf')
    if submission_pdf and is_pdf_link(submission_pdf):
        filename = secure_filename('fulltext.pdf')
        obj.data['documents'] = [
            document for document in obj.data.get('documents', ())
            if document.get('key') != filename
        ]
        lb = LiteratureBuilder(
            source=obj.data['acquisition_source']['source'], record=obj.data)
        lb.add_document(
            filename,
            fulltext=True,
            url=submission_pdf,
            original_url=submission_pdf,
        )

        obj.data = lb.record
        LOGGER.info('Workflow data updated with %s new documents' % len(obj.data.get('documents', [])))
    else:
        LOGGER.info('Submission document not found or in an incorrect format (%s)', submission_pdf)
    delete_empty_key(obj, 'documents')
    save_workflow(obj, eng)


@with_debug_logging
def download_documents(obj, eng):
    LOGGER.info('Downloading documents for %s', obj.id)
    documents = obj.data.get('documents', [])
    for document in documents:
        url = document['url']
        if url.startswith('/api/files'):
            obj.log.info('Document already downloaded from %s', url)
            continue

        filename = document['key']
        scheme = urlparse(url).scheme
        LOGGER.info(
            'Downloading document key:%s url:%s scheme:%s', document['key'], document['url'], scheme
        )

        if scheme == 'file':
            downloaded = copy_file_to_workflow(obj, filename, url)
        else:
            downloaded = download_file_to_workflow(
                workflow=obj,
                name=filename,
                url=url,
            )
        if downloaded:
            document['url'] = '/api/files/{bucket}/{key}'.format(
                bucket=obj.files[filename].bucket_id, key=quote(filename))
            obj.log.info('Document downloaded from %s', url)
        else:
            obj.log.error(
                'Cannot download document from %s', url)
    delete_empty_key(obj, 'documents')
    if current_app.config['FEATURE_FLAG_ENABLE_SAVE_WORFLOW_ON_DOWNLOAD_DOCUMENTS']:
        save_workflow(obj, eng)
    LOGGER.info('Documents downloaded: %s', len(obj.data.get('documents', [])))


@backoff.on_exception(backoff.expo, (BadGatewayError, requests.exceptions.ConnectionError), base=4, max_tries=5)
def match_references_hep(references):
    headers = {
        "content-type": "application/json",
    }
    data = {'references': references}
    inspirehep_url = current_app.config.get("INSPIREHEP_URL")
    response = requests.post(
        "{inspirehep_url}/matcher/linked_references/".format(
            inspirehep_url=inspirehep_url,
        ),
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        return response.json()['references']
    create_error(response)


@with_debug_logging
def refextract(obj, eng):
    """Extract references from various sources and add them to the workflow.

    Runs ``refextract`` on both the PDF attached to the workflow and the
    references provided by the submitter, if any, then chooses the one
    that generated the most and attaches them to the workflow object.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    if 'references' in obj.data:
        extracted_raw_references = dedupe_list(extract_references_from_raw_refs(obj.data['references']))
        obj.log.info('Extracted %d references from raw refs.', len(extracted_raw_references))
        obj.data['references'] = match_references_hep(extracted_raw_references)
        return

    matched_pdf_references, matched_text_references = [], []
    source = LiteratureReader(obj.data).source
    journal_kb_dict = create_journal_kb_dict()

    url = get_document_url_for_reference_extraction(obj)
    if current_app.config.get("FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE") and url:
        pdf_references = dedupe_list(
            extract_references_from_pdf_url(
                url, source=source, custom_kbs_file=journal_kb_dict
            )
        )
        matched_pdf_references = match_references_hep(pdf_references)
    else:
        with get_document_in_workflow(obj) as tmp_document:
            if tmp_document:
                pdf_references = dedupe_list(extract_references_from_pdf(tmp_document, source))
                matched_pdf_references = match_references_hep(pdf_references)

    text = get_value(obj.extra_data, 'formdata.references')
    if text and current_app.config.get("FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE"):
        text_references = dedupe_list(
            extract_references_from_text_data(
                text, source=source, custom_kbs_file=journal_kb_dict
            )
        )
        matched_text_references = match_references_hep(text_references)
    elif text:
        text_references = dedupe_list(extract_references_from_text(text, source))
        matched_text_references = match_references_hep(text_references)

    if not matched_pdf_references and not matched_text_references:
        obj.log.info('No references extracted.')
    elif len(matched_pdf_references) > len(matched_text_references):
        obj.log.info('Extracted %d references from PDF.', len(matched_pdf_references))
        obj.data['references'] = matched_pdf_references
    elif len(matched_text_references) >= len(matched_pdf_references):
        obj.log.info('Extracted %d references from text.', len(matched_text_references))
        obj.data['references'] = matched_text_references


@with_debug_logging
def count_reference_coreness(obj, eng):
    """Count number of core/non-core matched references."""
    cited_records = list(get_linked_records_in_field(obj.data, 'references.record'))
    count_core = len([rec for rec in cited_records if rec.get('core') is True])
    count_non_core = len(cited_records) - count_core

    obj.extra_data['reference_count'] = {
        'core': count_core,
        'non_core': count_non_core,
    }


@with_debug_logging
def save_workflow(obj, eng):
    """Save the current workflow.

    Saves the changes applied to the given workflow object in the database.

    Note:
        The ``save`` function only indexes the current workflow. For this
        reason, we need to ``db.session.commit()``.

    TODO:
        Refactor: move this logic inside ``WorkflowObject.save()``.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    obj.save()
    db.session.commit()


def error_workflow(message):
    """Force an error in the workflow with the given message."""
    @with_debug_logging
    @wraps(error_workflow)
    def _error_workflow(obj, eng):
        obj.log.error(message)
        obj.extra_data['_error_msg'] = message
        obj.status = ObjectStatus.ERROR
        raise WorkflowsError(message)

    _error_workflow.__doc__ = (
        'Force an error in the workflow object with the message "%s".'
        % message
    )
    return _error_workflow


@with_debug_logging
def preserve_root(obj, eng):
    """Save the current workflow payload to be used as root for the merger.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    if not current_app.config.get('FEATURE_FLAG_ENABLE_MERGER', False):
        return

    obj.extra_data['merger_root'] = deepcopy(obj.data)
    obj.save()


@backoff.on_exception(backoff.expo, (BadGatewayError, requests.exceptions.ConnectionError), base=4, max_tries=5)
def _get_all_journal_titles_to_normalize(obj_data):
    """Get all journal titles to normalize."""

    publication_journal_titles = get_value(obj_data, 'publication_info.journal_title', [])
    references_journal_titles = get_value(obj_data, 'references.reference.publication_info.journal_title', [])
    all_titles_to_normalize = publication_journal_titles + references_journal_titles

    response = requests.get(
        "{inspirehep_url}/curation/literature/normalize-journal-titles".format(
            inspirehep_url=current_app.config["INSPIREHEP_URL"]
        ),
        headers=_get_headers_for_hep_root_table_request(),
        data=json.dumps({'journal_titles_list': all_titles_to_normalize})
    )
    response.raise_for_status()
    normalized_journal_titles_mapping = response.json()['normalized_journal_titles']
    return normalized_journal_titles_mapping


@with_debug_logging
def normalize_journal_titles(obj, eng):
    """Normalize the journal titles

    Normalize the journal titles stored in the `journal_title` field of each object
    contained in `publication_info` and for each `publication_info.journal_title` in references.

    Note:
        The DB is queried in order to get the `$ref` of each journal and add it in
        `journal_record` as well as inspire categories.

    TODO:
        Refactor: it must be checked that `normalize_journal_title` is appropriate.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
       None
    """
    normalized_journal_titles_mapping = _get_all_journal_titles_to_normalize(obj.data)
    publications = obj.data.get('publication_info', [])

    for publication in publications:
        if 'journal_title' not in publication:
            continue
        normalized_journal_title = normalized_journal_titles_mapping[publication['journal_title']]
        normalize_journal_title_entry(obj, publication, normalized_journal_title, add_inspire_categories=True)

    references = obj.data.get("references", [])
    for reference in references:
        publication_info = get_value(reference, 'reference.publication_info', {})
        journal_title = publication_info.get('journal_title')
        if not journal_title:
            continue
        normalized_joutnal_title = normalized_journal_titles_mapping[journal_title]
        normalize_journal_title_entry(obj, publication_info, normalized_joutnal_title)

    if obj.extra_data.get('journal_inspire_categories'):
        obj.extra_data['journal_inspire_categories'] = dedupe_list(obj.extra_data['journal_inspire_categories'])


def normalize_journal_title_entry(obj, publication_info, normalized_title, add_inspire_categories=False):
    publication_info['journal_title'] = normalized_title

    ref_query = RecordMetadata.query.filter(
        RecordMetadata.json['_collections'].op('?')('Journals')).filter(
        cast(RecordMetadata.json['short_title'], String) == type_coerce(normalized_title, JSON))
    result = db.session.execute(ref_query).fetchone()
    journal_data = result.records_metadata_json if result else None

    if not journal_data:
        return

    journal_record = journal_data['self']

    if journal_record:
        publication_info['journal_record'] = journal_record

    if add_inspire_categories and journal_data.get('inspire_categories'):
        obj.extra_data.setdefault('journal_inspire_categories', []).extend(journal_data['inspire_categories'])


def update_inspire_categories(obj, eng):
    if obj.extra_data.get('journal_inspire_categories') and 'inspire_categories' not in obj.data:
        obj.data['inspire_categories'] = obj.extra_data['journal_inspire_categories']


@with_debug_logging
def set_refereed_and_fix_document_type(obj, eng):
    """Set the ``refereed`` field using the Journals DB.

    Searches in the Journals DB if the current article was published in journals
    that we know for sure to be peer-reviewed, or that publish both peer-reviewed
    and non peer-reviewed content but for which we can infer that it belongs to
    the former category, and sets the ``refereed`` key in ``data`` to ``True`` if
    that was the case. If instead we know for sure that all journals in which it
    published are **not** peer-reviewed we set it to ``False``.

    Also replaces the ``article`` document type with ``conference paper`` if the
    paper was only published in non refereed proceedings.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    journals = replace_refs(get_value(obj.data, 'publication_info.journal_record'), 'db')
    if not journals:
        return

    is_published_in_a_refereed_journal_that_does_not_publish_proceedings = any(
        journal.get('refereed') and not journal.get('proceedings') for journal in journals)
    is_published_in_a_refereed_journal_that_also_publishes_proceedings = any(
        journal.get('refereed') and journal.get('proceedings') for journal in journals)
    is_not_a_conference_paper = 'conference paper' not in obj.data['document_type']

    is_published_exclusively_in_non_refereed_journals = all(
        not journal.get('refereed', True) for journal in journals)

    if is_published_in_a_refereed_journal_that_does_not_publish_proceedings:
        obj.data['refereed'] = True
    elif is_not_a_conference_paper and is_published_in_a_refereed_journal_that_also_publishes_proceedings:
        obj.data['refereed'] = True
    elif is_published_exclusively_in_non_refereed_journals:
        obj.data['refereed'] = False

    is_published_only_in_proceedings = all(journal.get('proceedings') for journal in journals)
    is_published_only_in_non_refereed_journals = all(not journal.get('refereed') for journal in journals)

    if is_published_only_in_proceedings and is_published_only_in_non_refereed_journals:
        try:
            obj.data['document_type'].remove('article')
            obj.data['document_type'].append('conference paper')
        except ValueError:
            pass


@with_debug_logging
def jlab_ticket_needed(obj, eng):
    """Check if the a JLab curation ticket is needed."""
    jlab_categories = set(current_app.config['JLAB_ARXIV_CATEGORIES'])
    arxiv_categories = set(LiteratureReader(obj.data).arxiv_categories)
    return bool(jlab_categories & arxiv_categories)


@with_debug_logging
def load_from_source_data(obj, eng):
    """Restore the workflow data and extra_data from source_data."""
    try:
        source_data = obj.extra_data['source_data']
        source_data['extra_data']['_task_history'] = obj.extra_data.get('_task_history', [])
        obj.data = source_data['data']
        obj.extra_data = source_data['extra_data']
        obj.extra_data['source_data'] = deepcopy(source_data)
        obj.save()
    except KeyError:
        raise ValueError("Can't start/restart workflow as 'source_data' is either missing or corrupted")


@with_debug_logging
def delay_if_necessary(obj, eng):
    """Delays workflow if necessary,
    delay timeout should be in `extra_data['source_data']['delay']` key """
    delay = get_value(obj.extra_data, 'source_data.extra_data.delay')
    if delay:
        time.sleep(float(delay))


def go_to_first_step(obj, eng):
    """Forces the workflow to continue from its first step."""
    obj.log.info('Continuing execution from first step.')
    save_workflow(obj, eng)
    eng.restart('first', 'first')

    # XXX: for some reasons, restarting a workflow generates a fork. The
    # current branch stops here, the other one will start from the beginning.
    eng.stop()


@with_debug_logging
def increase_restart_count_or_error(obj, eng):
    """Increase the `restart-count` of the current workflow.

    If `restart-count` contains a value greater than WORKFLOWS_RESTART_LIMIT it
    throws a WorkflowError. If `restart-count` is not in
    `extra_data.persistent_data.marks` the increment is skipped.
    """
    try:
        count = obj.extra_data['source_data']['persistent_data']['marks']['restart-count']
    except KeyError:
        count = None

    if count is None:
        return
    if count < current_app.config.get('WORKFLOWS_RESTART_LIMIT'):
        obj.extra_data['source_data']['persistent_data']['marks']['restart-count'] += 1
        save_workflow(obj, eng)
    else:
        raise WorkflowsError('Workflow restarted too many times')


def flatten_list(input_list):
    if isinstance(input_list, (list, tuple)):
        return [
            element for innerList in input_list for element in flatten_list(innerList)
        ]
    return [input_list]


@with_debug_logging
def affiliations_for_hidden_collections(obj):
    affiliations_mapping = current_app.config.get("AFFILIATIONS_TO_HIDDEN_COLLECTIONS_MAPPING", {})
    affiliations = flatten_list(get_value(obj.data, 'authors.raw_affiliations.value', []))

    query = u"|".join(ur"\b{aff}\b".format(aff=aff.replace(u" ", ur"\W+")) for aff in affiliations_mapping.keys())

    affiliations_set = set()
    for aff in affiliations:
        matches = re.findall(query, aff, re.IGNORECASE | re.UNICODE)
        affiliations_set.update([re.sub(ur"\W+", u" ", match.upper(), flags=re.UNICODE) for match in matches])
    return [affiliations_mapping[affiliation] for affiliation in affiliations_set]


def reports_for_hidden_collections(obj):
    hidden_collection_mapping = current_app.config.get(
        "AFFILIATIONS_TO_HIDDEN_COLLECTIONS_MAPPING", {}
    )
    hidden_collections = set()
    for report_number in obj.data.get("report_numbers", []):
        hidden_collections.update(
            [
                match.upper()
                for match in re.findall("cern|fermilab", report_number["value"], re.IGNORECASE)
            ]
        )
    return {hidden_collection_mapping[collection] for collection in hidden_collections}


@with_debug_logging
def should_be_hidden(obj, eng):
    """Checks if paper attached to this workflow is affiliated with one of affiliations which interests us."""
    return bool(affiliations_for_hidden_collections(obj)) or bool(
        reports_for_hidden_collections(obj)
    )


@with_debug_logging
def replace_collection_to_hidden(obj, eng):
    """Replaces collection to hidden based on authors affiliations"""
    hidden_collections = reports_for_hidden_collections(obj)
    hidden_collections.update(affiliations_for_hidden_collections(obj))
    obj.data["_collections"] = list(hidden_collections)
    return obj


@with_debug_logging
def is_fermilab_report(obj, eng):
    """Check if record is a Fermilab report."""
    report_numbers = get_value(obj.data, "report_numbers.value", [])
    return any(report_number.startswith("FERMILAB") for report_number in report_numbers)


def add_collection(collection):
    """Add specified collection to _collections in record."""
    @with_debug_logging
    @wraps(add_collection)
    def _add_collection(obj, eng):
        if collection not in obj.data['_collections']:
            obj.data['_collections'].append(collection)

    return _add_collection


@with_debug_logging
def is_suitable_for_pdf_authors_extraction(obj, eng):
    """Check if article is arXiv/PoS and if authors.xml were attached"""
    acquisition_source = get_value(obj.data, 'acquisition_source.source', '').lower()
    if acquisition_source in ['arxiv', 'pos'] and not get_mark(obj, "authors_xml", False):
        return True
    return False


@with_debug_logging
def extract_authors_from_pdf(obj, eng):
    # If there are more than specified number of authors then don't run Grobid authors extraction
    if len(obj.data.get('authors', [])) > current_app.config.get('WORKFLOWS_MAX_AUTHORS_COUNT_FOR_GROBID_EXTRACTION', 1000):
        return obj
    api_path = "api/processHeaderDocument"
    kwargs_to_grobid = {"includeRawAffiliations": "1", "consolidateHeader": "1"}
    grobid_response = post_pdf_to_grobid(obj, api_path, **kwargs_to_grobid)
    if not grobid_response:
        return
    authors_and_affiliations = GrobidAuthors(grobid_response.text)
    data = authors_and_affiliations.parse_all()
    grobid_authors = get_value(data, 'author')
    merged_authors, merge_conflicts = merge({},
                                            {'authors': obj.data.get('authors', [])},
                                            {'authors': grobid_authors},
                                            configuration=GrobidOnArxivAuthorsOperations)
    if not obj.data.get('authors', []) and len(authors_and_affiliations) > 0:
        LOGGER.info(
            "Using %s GROBID authors",
            len(authors_and_affiliations),
        )
        obj.data['authors'] = grobid_authors
        obj.extra_data['authors_with_affiliations'] = data
    elif not merge_conflicts and len(merged_authors['authors']) > 0:
        LOGGER.info(
            "Using %s merged GROBID authors",
            len(merged_authors),
        )
        obj.data['authors'] = merged_authors['authors']
        obj.extra_data['authors_with_affiliations'] = data
    else:
        metadata_authors_count = len(obj.data['authors']) if 'authors' in obj.data else 0
        grobid_authors_count = len(authors_and_affiliations) if authors_and_affiliations else 0
        LOGGER.warning(
            "Ignoring grobid authors. Expected authors count: %s. Authors exctracted from grobid %s.",
            metadata_authors_count,
            grobid_authors_count
        )
    return obj


@with_debug_logging
@backoff.on_exception(backoff.expo, (BadGatewayError, requests.exceptions.ConnectionError), base=4, max_tries=5)
def normalize_collaborations(obj, eng):
    collaborations = obj.data.get('collaborations', [])
    if not isinstance(collaborations, list):
        LOGGER.exception(
            "Metadata are malformed for record %s. Collaborations key is not a list.",
            obj.id
        )
        return obj
    if len(collaborations) < 1:
        return obj
    normalized_collaborations_response = requests.get(
        "{inspirehep_url}/curation/literature/collaborations-normalization".format(
            inspirehep_url=current_app.config["INSPIREHEP_URL"]
        ),
        headers=_get_headers_for_hep_root_table_request(),
        data=json.dumps({
            "collaborations": collaborations,
            "workflow_id": obj.id,
        }),
    )
    normalized_collaborations_response.raise_for_status()
    obj_accelerator_experiments = obj.data.get('accelerator_experiments', [])
    normalized_accelerator_experiments = normalized_collaborations_response.json()['accelerator_experiments']
    if normalized_accelerator_experiments or obj_accelerator_experiments:
        obj.data['accelerator_experiments'] = dedupe_list(
            obj_accelerator_experiments + normalized_accelerator_experiments
        )
        obj.data['collaborations'] = normalized_collaborations_response.json()['normalized_collaborations']
    return obj


@backoff.on_exception(backoff.expo, (BadGatewayError, requests.exceptions.ConnectionError), base=4, max_tries=5)
def normalize_author_affiliations(obj, eng):
    normalized_affiliation_response = requests.get(
        "{inspirehep_url}/curation/literature/affiliations-normalization".format(
            inspirehep_url=current_app.config["INSPIREHEP_URL"]
        ),
        headers=_get_headers_for_hep_root_table_request(),
        data=json.dumps({
            "authors": obj.data.get('authors', []),
            "workflow_id": obj.id,
        }),
    )
    normalized_affiliation_response.raise_for_status()
    normalized_affiliation_response_json = normalized_affiliation_response.json()
    normalized_affiliations = normalized_affiliation_response_json['normalized_affiliations']
    ambiguous_affiliations = normalized_affiliation_response_json['ambiguous_affiliations']

    for author, normalized_affiliation in zip(
        obj.data.get("authors", []), normalized_affiliations
    ):
        author_affiliations = author.get("affiliations", [])
        if author_affiliations:
            continue
        raw_affs = get_value(author, "raw_affiliations.value", [])
        if normalized_affiliation:
            author["affiliations"] = normalized_affiliation
            LOGGER.info(
                "(wf: %s) Normalized affiliations for author %s. Raw affiliations: %s. Assigned affiliations: %s",
                obj.id,
                author["full_name"],
                ",".join(raw_affs),
                normalized_affiliation,
            )
    for ambiguous_affiliation in ambiguous_affiliations:
        LOGGER.info(
            "(wf: %s) Found ambiguous affiliations for raw affiliation %s, skipping affiliation linking.",
            obj.id,
            ambiguous_affiliation,
        )
    return obj


def link_institutions_with_affiliations(obj, eng):
    if not obj.data.get('authors'):
        LOGGER.info('wf {}: No authors found, skipping institution linking'.format(obj.id))
    else:
        authors_with_linked_institutions_response = requests.get(
            "{inspirehep_url}/curation/literature/assign-institutions".format(
                inspirehep_url=current_app.config["INSPIREHEP_URL"]
            ),
            headers=_get_headers_for_hep_root_table_request(),
            data=json.dumps({
                "authors": obj.data['authors']
            }),
        )
        authors_with_linked_institutions_response.raise_for_status()
        authors_with_linked_institutions_response.raise_for_status()
        authors = authors_with_linked_institutions_response.json()['authors']
        obj.data['authors'] = authors

    return obj


def core_selection_wf_already_created(control_number):
    query_wf_with_cn = Q("match", metadata__control_number=control_number)
    query_core_selection_wf = Q("match", _workflow__workflow_name="CORE_SELECTION")
    query = query_wf_with_cn & query_core_selection_wf

    return Search(index="holdingpen-hep", using=current_search_client).query(query).source(False).execute()


def create_core_selection_wf(obj, eng):
    record_control_number = obj.data.get('control_number')
    if not record_control_number:
        raise MissingRecordControlNumber
    if is_core(obj, eng) or not _is_auto_approved(obj) or core_selection_wf_already_created(record_control_number) or check_mark(obj, 'is-update'):
        LOGGER.info("No core selection needed for %s workflow with record %s", obj.id, record_control_number)
        return obj

    extra_data_to_clean = ['_task_history', '_error_msg', 'source_data', 'restart-count']
    extra_data = dict(obj.extra_data.copy())
    for key in extra_data_to_clean:
        if key in extra_data:
            del extra_data[key]
    data = obj.data.copy()

    workflow_object = workflow_object_class.create(
        data={},
        id_user=None,
        data_type="hep"
    )

    workflow_object.data = data

    extra_data['source_data'] = {}
    workflow_object.extra_data = extra_data

    workflow_object.save()
    db.session.commit()

    start.delay("core_selection", object_id=workflow_object.id)


@backoff.on_exception(
    backoff.expo,
    GROBID_EXCEPTIONS,
    base=4, max_tries=9
)
def post_pdf_to_grobid(obj, grobid_api_path, **kwargs):
    with get_document_in_workflow(obj) as tmp_document:
        if not tmp_document:
            return
        with open(tmp_document, 'rb') as document_file:
            document = document_file.read()
        data = {'input': document}
        data.update(kwargs)
        grobid_url = current_app.config["GROBID_URL"]
        try:
            response = requests.post(
                urljoin(grobid_url, grobid_api_path),
                files=data,
                headers={'Accept': 'application/xml'}
            )
            response.raise_for_status()
        except GROBID_EXCEPTIONS:
            LOGGER.warning("(%s) Grobid request failed due to the GROBID serivce error!" % str(obj.id))
            return
    return response


def get_fulltext(obj):
    grobid_api_path = "api/processFulltextDocument"
    grobid_response = post_pdf_to_grobid(obj, grobid_api_path)
    if not grobid_response:
        return
    xml_data = grobid_response.text
    xml = Selector(text=xml_data, type="xml")
    xml.remove_namespaces()
    text = xml.getall()
    fulltext = ' '.join(text)
    return fulltext


def check_if_france_in_fulltext(obj, eng):
    fulltext = get_fulltext(obj)
    if not fulltext:
        return
    regex = re.compile(r"\bfrance\b|in2p3", re.UNICODE | re.IGNORECASE)
    return regex.search(fulltext)


def check_if_france_in_raw_affiliations(obj, eng):
    raw_affs = get_value(obj.data, 'authors.raw_affiliations.value', [])
    for aff in chain.from_iterable(raw_affs):
        if "france" in aff.lower() or "in2p3" in aff.lower():
            return True


def check_if_germany_in_fulltext(obj, eng):
    fulltext = get_fulltext(obj)
    if not fulltext:
        return
    regex = re.compile(r"\b(Germany|Deutschland)\b", re.UNICODE | re.IGNORECASE)
    return regex.search(fulltext)


def check_if_germany_in_raw_affiliations(obj, eng):
    raw_affs = get_value(obj.data, 'authors.raw_affiliations.value', [])
    for aff in chain.from_iterable(raw_affs):
        if "germany" in aff.lower() or "deutschland" in aff.lower():
            return True


def check_if_core_and_uk_in_fulltext(obj, eng):
    fulltext = get_fulltext(obj)
    if not fulltext or not is_core(obj, eng):
        return
    regex = re.compile(
        r"\b(UK|United\s+Kingdom|England|Scotland|Northern\s+Ireland)\b", re.UNICODE | re.IGNORECASE)
    return regex.search(fulltext)


def check_if_uk_in_raw_affiliations(obj, eng):
    raw_affs = get_value(obj.data, 'authors.raw_affiliations.value', [])
    regex = re.compile(
        r"\b(UK|United\s+Kingdom|England|Scotland|Northern\s+Ireland)\b", re.UNICODE | re.IGNORECASE)
    for aff in chain.from_iterable(raw_affs):
        if regex.search(aff):
            return True


def load_record_from_hep(obj, wf):
    control_number = obj.data['control_number']
    pid_type = get_pid_type_from_schema(obj.data['$schema'])
    record_data = get_record_from_hep(pid_type, control_number)
    obj.data = record_data['metadata']
    obj.extra_data['head_uuid'] = record_data['uuid']
    obj.extra_data['head_version_id'] = record_data['revision_id'] + 1
    obj.extra_data['head_revision_id'] = record_data['revision_id']

    return obj


def remove_inspire_categories_derived_from_core_arxiv_categories(obj, eng):
    if not obj.data.get("arxiv_eprints"):
        return
    inspire_categories_without_arxiv_sourced = [
        category
        for category in obj.data.get("inspire_categories", [])
        if category.get("source") != "arxiv"
    ]
    non_core_arxiv_categories = [
        arxiv_category
        for arxiv_category in get_value(obj.data, 'arxiv_eprints[0].categories', [])
        if arxiv_category in current_app.config["ARXIV_CATEGORIES"]["non-core"]
    ]
    inspire_categories_for_non_core_arxiv_categories = [
        {"term": classify_field(arxiv_category), "source": "arxiv"}
        for arxiv_category in non_core_arxiv_categories
    ]
    inspire_categories_without_arxiv_sourced.extend(
        inspire_categories_for_non_core_arxiv_categories
    )
    obj.data["inspire_categories"] = inspire_categories_without_arxiv_sourced
    return obj
