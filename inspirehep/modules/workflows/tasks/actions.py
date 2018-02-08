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

import os
import re
from functools import wraps

from flask import current_app
from sqlalchemy import (
    JSON,
    String,
    cast,
    type_coerce,
)
from timeout_decorator import TimeoutError
from werkzeug import secure_filename

from invenio_db import db
from invenio_workflows.errors import WorkflowsError
from invenio_records.models import RecordMetadata

from inspire_schemas.builders import LiteratureBuilder
from inspire_schemas.utils import validate
from inspire_utils.record import get_value
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.modules.workflows.tasks.refextract import (
    extract_references_from_pdf,
    extract_references_from_text,
)
from inspirehep.modules.workflows.utils import (
    download_file_to_workflow,
    get_pdf_in_workflow,
    log_workflows_action,
    with_debug_logging,
)
from inspirehep.utils.normalizers import normalize_journal_title
from inspirehep.utils.record import get_arxiv_id
from inspirehep.utils.url import is_pdf_link
from jsonschema.exceptions import ValidationError


RE_ALPHANUMERIC = re.compile('\W+', re.UNICODE)


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
        obj.extra_data[key] = value

    _mark.__doc__ = 'Mark the workflow object with %s:%s.' % (key, value)
    return _mark


def is_marked(key):
    """Check if the workflow object has a specific mark."""
    @with_debug_logging
    @wraps(mark)
    def _mark(obj, eng):
        return key in obj.extra_data and obj.extra_data[key]

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


@with_debug_logging
def is_record_relevant(obj, eng):
    """Shall we halt this workflow for potential acceptance or just reject?"""

    # We do not auto-reject any user submissions
    if is_submission(obj, eng):
        return True

    if _is_auto_rejected(workflow_obj=obj):
        return False

    return True


@with_debug_logging
def is_experimental_paper(obj, eng):
    """Check if the record is an experimental paper."""
    categories = list(
        get_value(obj.data, "arxiv_eprints.categories", [[]])[0]
    ) + list(get_value(obj.data, "inspire_categories.term", []))

    categories_to_check = [
        "hep-ex", "nucl-ex", "astro-ph", "astro-ph.IM", "astro-ph.CO",
        "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.SR",
        "physics.ins-det", "Experiment-HEP", "Experiment-Nucl",
        "Astrophysics", "Instrumentation"
    ]
    for experimental_category in categories_to_check:
        if experimental_category in categories:
            return True

    return False


@with_debug_logging
def is_arxiv_paper(obj, *args, **kwargs):
    """Check if the record is from arXiv."""
    arxiv_id = get_arxiv_id(obj.data)
    categories = get_value(obj.data, 'arxiv_eprints.categories')

    if arxiv_id or categories:
        return True
    return False


@with_debug_logging
def is_submission(obj, eng):
    """Is this a submission?"""
    source = obj.data.get('acquisition_source')
    if source:
        return source.get('method') == 'submitter'
    return False


@with_debug_logging
def stop_in_error_if_record_not_valid(obj, eng):
    """Check if the record is schema compliant and stop the workflow in ERROR state it it is not."""
    try:
        validate(obj.data, 'hep')
    except ValidationError as err:
        message = 'The record contained in the workflow is not schema compliant: \n' + err.message
        obj.log.error(message)
        raise WorkflowsError(message)


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


@with_debug_logging
def download_documents(obj, eng):
    documents = obj.data.get('documents')
    if documents:
        for document in documents:
            filename = document['key']
            url = document['url']
            downloaded = download_file_to_workflow(
                workflow=obj,
                name=filename,
                url=url,
            )
            if downloaded:
                document['url'] = '/api/files/{bucket}/{key}'.format(
                    bucket=obj.files[filename].bucket_id, key=filename)
                obj.log.info('Document downloaded from %s', url)
            else:
                obj.log.error(
                    'Cannot download document from %s', url)


@with_debug_logging
def refextract(obj, eng):
    """Extract references from various sources and add them to the workflow.

    Runs ``refextract`` on both the PDF attached to the workflow and the
    references provided by the submitter, if any, then chooses the one
    that generated the most and attaches them to the workflow object.

    Note:
        We might want to compare the number of *matched* references instead.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None
    """
    pdf_references, text_references = [], []
    source = get_value(obj.data, 'acquisition_source.source')

    tmp_pdf = get_pdf_in_workflow(obj)
    if tmp_pdf:
        try:
            pdf_references = extract_references_from_pdf(tmp_pdf, source)
        except TimeoutError:
            obj.log.error('Timeout when extracting references from PDF.')
        finally:
            if os.path.exists(tmp_pdf):
                os.unlink(tmp_pdf)

    text = get_value(obj.extra_data, 'formdata.references')
    if text:
        try:
            text_references = extract_references_from_text(text, source)
        except TimeoutError:
            obj.log.error('Timeout when extracting references from text.')

    if len(pdf_references) == len(text_references) == 0:
        obj.log.info('No references extracted.')
    elif len(pdf_references) >= len(text_references):
        obj.log.info('Extracted %d references from PDF.', len(pdf_references))
        obj.data['references'] = pdf_references
    elif len(text_references) > len(pdf_references):
        obj.log.info('Extracted %d references from text.', len(text_references))
        obj.data['references'] = text_references


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
        raise WorkflowsError(message)

    _error_workflow.__doc__ = (
        'Force an error in the workflow object with the message "%s".'
        % message
    )
    return _error_workflow


@with_debug_logging
def normalize_journal_titles(obj, eng):
    """Normalize the journal titles

    Normalize the journal titles stored in the `journal_title` field of each object
    contained in `publication_info`.

    Note:
        The DB is queried in order to get the `$ref` of each journal and add it in
        `journal_record`.

    TODO:
        Refactor: it must be checked that `normalize_journal_title` is appropriate.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
       None
    """
    publications = obj.data.get('publication_info')

    if not publications:
        return None

    for index, publication in enumerate(publications):
        if 'journal_title' in publication:
            normalized_title = normalize_journal_title(publication['journal_title'])
            obj.data['publication_info'][index]['journal_title'] = normalized_title
            ref_query = RecordMetadata.query.filter(
                RecordMetadata.json['_collections'].op('?')('Journals')).filter(
                cast(RecordMetadata.json['short_title'], String) == type_coerce(normalized_title, JSON))
            result = db.session.execute(ref_query).fetchone()

            if result:
                obj.data['publication_info'][index]['journal_record'] = result.records_metadata_json['self']


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
