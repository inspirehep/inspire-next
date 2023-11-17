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

"""Workflow tasks using refextract API."""

from __future__ import absolute_import, division, print_function

import backoff
from itertools import chain
import json
from flask import current_app
from requests.exceptions import RequestException
import requests

from invenio_workflows.errors import WorkflowsError
from inspire_schemas.utils import (
    convert_old_publication_info_to_new,
    split_page_artid,
)
from inspire_utils.helpers import maybe_int
from inspire_utils.logging import getStackTraceLogger
from inspirehep.modules.refextract.tasks import create_journal_kb_dict
from refextract import (
    extract_journal_reference,
    extract_references_from_file,
    extract_references_from_string,
)

from refextract.references.errors import UnknownDocumentTypeError

from inspirehep.modules.workflows.utils import (
    ignore_timeout_error,
    timeout_with_config,
)

from inspirehep.utils.references import (
    local_refextract_kbs_path,
    map_refextract_to_schema,
)
from ..utils import with_debug_logging

LOGGER = getStackTraceLogger(__name__)


@with_debug_logging
@backoff.on_exception(
    backoff.expo,
    RequestException,
    max_tries=5,
)
def extract_journal_info(obj, eng):
    """Extract the journal information from ``pubinfo_freetext``.

    Runs ``extract_journal_reference`` on the ``pubinfo_freetext`` key of each
    ``publication_info``, if it exists, and uses the extracted information to
    populate the other keys.

    Args:
        obj: a workflow object.
        eng: a workflow engine.

    Returns:
        None

    """
    if not obj.data.get('publication_info'):
        return

    kbs_journal_dict = create_journal_kb_dict()

    if current_app.config.get("FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE"):
        publication_infos = obj.data['publication_info']
        refextract_request_headers = {
            "content-type": "application/json",
        }
        response = requests.post(
            "{}/extract_journal_info".format(current_app.config["REFEXTRACT_SERVICE_URL"]),
            headers=refextract_request_headers,
            data=json.dumps({"publication_infos": publication_infos, "journal_kb_data": kbs_journal_dict})
        )
        try:
            response.raise_for_status()
        except RequestException:
            LOGGER.info("Couldn't extract publication info from url!")
            raise WorkflowsError(
                "Error from refextract: [{code}]: {message}".format(
                    code=response.status_code,
                    message=response.json()
                )
            )
        extracted_publication_info = response.json().get('extracted_publication_infos', [])
        for publication_info, extracted_publication_info in zip(publication_infos, extracted_publication_info):
            if extracted_publication_info.get('title'):
                publication_info['journal_title'] = extracted_publication_info['title']

            if extracted_publication_info.get('volume'):
                publication_info['journal_volume'] = extracted_publication_info['volume']

            if extracted_publication_info.get('page'):
                page_start, page_end, artid = split_page_artid(extracted_publication_info['page'])
                if page_start:
                    publication_info['page_start'] = page_start
                if page_end:
                    publication_info['page_end'] = page_end
                if artid:
                    publication_info['artid'] = artid

            if extracted_publication_info.get('year'):
                year = maybe_int(extracted_publication_info['year'])
                if year:
                    publication_info['year'] = year
    else:
        for publication_info in obj.data['publication_info']:
            try:
                with local_refextract_kbs_path() as kbs_path:
                    extracted_publication_info = extract_journal_reference(
                        publication_info['pubinfo_freetext'],
                        override_kbs_files=kbs_path,
                    )

                if not extracted_publication_info:
                    continue

                if extracted_publication_info.get('title'):
                    publication_info['journal_title'] = extracted_publication_info['title']

                if extracted_publication_info.get('volume'):
                    publication_info['journal_volume'] = extracted_publication_info['volume']

                if extracted_publication_info.get('page'):
                    page_start, page_end, artid = split_page_artid(extracted_publication_info['page'])
                    if page_start:
                        publication_info['page_start'] = page_start
                    if page_end:
                        publication_info['page_end'] = page_end
                    if artid:
                        publication_info['artid'] = artid

                if extracted_publication_info.get('year'):
                    year = maybe_int(extracted_publication_info['year'])
                    if year:
                        publication_info['year'] = year
            except KeyError:
                pass

    obj.data['publication_info'] = convert_old_publication_info_to_new(obj.data['publication_info'])


@ignore_timeout_error(return_value=[])
@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=5,
)
def extract_references_from_pdf_url(url, custom_kbs_file, source=None):
    refextract_request_headers = {
        "content-type": "application/json",
    }
    response = requests.post(
        "{}/extract_references_from_url".format(current_app.config["REFEXTRACT_SERVICE_URL"]),
        headers=refextract_request_headers,
        data=json.dumps({"url": url, "journal_kb_data": custom_kbs_file})
    )
    if response.status_code != 200:
        LOGGER.info("Couldn't extract references from url!")
        raise WorkflowsError(
            "Error from refextract: [{code}]: {message}".format(
                code=response.status_code,
                message=response.json()
            )
        )
    extracted_references = response.json().get('extracted_references', [])
    return map_refextract_to_schema(extracted_references, source=source)


@ignore_timeout_error(return_value=[])
@timeout_with_config('WORKFLOWS_REFEXTRACT_TIMEOUT')
def extract_references_from_pdf(filepath, source=None, custom_kbs_file=None):
    """Extract references from PDF and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        try:
            extracted_references = extract_references_from_file(
                filepath,
                override_kbs_files=kbs_path,
                reference_format=u'{title},{volume},{page}',
            )
        except UnknownDocumentTypeError as e:
            if 'xml' in e.message:
                LOGGER.info('Skipping extracting references for xml file')
                return []
            raise

    return map_refextract_to_schema(extracted_references, source=source)


@ignore_timeout_error(return_value=[])
@timeout_with_config('WORKFLOWS_REFEXTRACT_TIMEOUT')
def extract_references_from_text(text, source=None, custom_kbs_file=None):
    """Extract references from text and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        extracted_references = extract_references_from_string(
            text,
            override_kbs_files=kbs_path,
            reference_format=u'{title},{volume},{page}',
        )

    return map_refextract_to_schema(extracted_references, source=source)


@ignore_timeout_error(return_value=[])
@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=5,
)
def extract_references_from_text_data(text, custom_kbs_file, source=None):
    """Extract references from text and return in INSPIRE format."""
    refextract_request_headers = {
        "content-type": "application/json",
    }
    response = requests.post(
        "{}/extract_references_from_text".format(current_app.config["REFEXTRACT_SERVICE_URL"]),
        headers=refextract_request_headers,
        data=json.dumps({"text": text, "journal_kb_data": custom_kbs_file})
    )
    extracted_text_references = response.json().get('extracted_references', [])
    return map_refextract_to_schema(extracted_text_references, source=source)


@ignore_timeout_error(return_value=[])
@timeout_with_config('WORKFLOWS_REFEXTRACT_TIMEOUT')
def extract_references_from_raw_refs(references, custom_kbs_file=None):
    """Extract references from raw references in reference list.

    Args:
        references(List[dict]): a schema-compliant ``references`` field. If an element
            already contains a structured reference (that is, a ``reference`` key),
            it is not modified.  Otherwise, the contents of the
            ``raw_refs`` is extracted by ``refextract``.
        custom_kbs_file(dict): configuration for refextract knowledge bases.

    Returns:
        List[dict]: a schema-compliant ``references`` field, with all
        previously unextracted references extracted.
    """
    return list(chain.from_iterable(
        extract_references_from_raw_ref(ref, custom_kbs_file=custom_kbs_file) for ref in references
    ))


def extract_references_from_raw_ref(reference, custom_kbs_file=None):
    """Extract references from raw references in reference element.

    Args:
        reference(dict): a schema-compliant element of the ``references``
            field. If it already contains a structured reference (that is, a
            ``reference`` key), no further processing is done.  Otherwise, the
            contents of the ``raw_refs`` is extracted by ``refextract``.
        custom_kbs_file(dict): configuration for refextract knowledge bases.

    Returns:
        List[dict]: a list of schema-compliant elements of the ``references`` field, with all
        previously unextracted references extracted.

    Note:
        This function returns a list of references because one raw reference
        might correspond to several references.
    """
    if 'reference' in reference or 'raw_refs' not in reference:
        return [reference]

    text_raw_refs = [ref for ref in reference['raw_refs'] if ref['schema'] == 'text']
    nontext_schemas = [ref['schema'] for ref in reference['raw_refs'] if ref['schema'] != 'text']

    if nontext_schemas:
        LOGGER.error('Impossible to extract references from non-text raw_refs with schemas %s', nontext_schemas)
        return [reference]

    if len(text_raw_refs) > 1:
        LOGGER.error(
            'More than one text raw reference in %s, taking first one, the others will be lost',
            text_raw_refs
        )

    raw_ref = text_raw_refs[0]
    return extract_references_from_text(
        raw_ref['value'], source=raw_ref.get('source'), custom_kbs_file=custom_kbs_file
    )
