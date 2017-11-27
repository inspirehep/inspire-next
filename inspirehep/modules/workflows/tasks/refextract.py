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

from timeout_decorator import timeout

from inspire_schemas.utils import (
    convert_old_publication_info_to_new,
    split_page_artid,
)
from inspire_utils.helpers import maybe_int
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


@timeout(5 * 60)
def extract_references_from_pdf(filepath, source=None, custom_kbs_file=None):
    """Extract references from PDF and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        extracted_references = extract_references_from_file(
            filepath,
            override_kbs_files=kbs_path,
            reference_format=u'{title},{volume},{page}',
        )

    return map_refextract_to_schema(extracted_references, source=source)


@timeout(5 * 60)
def extract_references_from_text(text, source=None, custom_kbs_file=None):
    """Extract references from text and return in INSPIRE format."""
    with local_refextract_kbs_path() as kbs_path:
        extracted_references = extract_references_from_string(
            text,
            override_kbs_files=kbs_path,
            reference_format=u'{title},{volume},{page}',
        )

    return map_refextract_to_schema(extracted_references, source=source)
