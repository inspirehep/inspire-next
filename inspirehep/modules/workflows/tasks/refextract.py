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

from itertools import chain

from inspire_schemas.utils import (
    convert_old_publication_info_to_new,
    split_page_artid,
)
from inspire_utils.helpers import maybe_int
from inspire_utils.logging import getStackTraceLogger
from inspirehep.utils.references import (
    local_refextract_kbs_path,
    map_refextract_to_schema,
)
from refextract import (
    extract_journal_reference,
    extract_references_from_file,
    extract_references_from_string,
)

from ..utils import with_debug_logging


LOGGER = getStackTraceLogger(__name__)


@with_debug_logging
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


def extract_references_from_pdf(filepath, source=None, custom_kbs_file=None):
    """Extract references from PDF and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        extracted_references = extract_references_from_file(
            filepath,
            override_kbs_files=kbs_path,
            reference_format=u'{title},{volume},{page}',
        )

    return map_refextract_to_schema(extracted_references, source=source)


def extract_references_from_text(text, source=None, custom_kbs_file=None):
    """Extract references from text and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        extracted_references = extract_references_from_string(
            text,
            override_kbs_files=kbs_path,
            reference_format=u'{title},{volume},{page}',
        )

    return map_refextract_to_schema(extracted_references, source=source)


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
        raw_ref['value'], source=raw_ref['source'], custom_kbs_file=custom_kbs_file
    )


def match_reference(reference):
    pass
