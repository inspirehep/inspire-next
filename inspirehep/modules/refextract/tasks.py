# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Workflow tasks using refextract API."""

from __future__ import absolute_import, division, print_function

import json

from refextract import extract_journal_reference, extract_references_from_file

from inspirehep.utils.record import get_value
from inspirehep.utils.pubnote import split_page_artid

# FIXME get journal mappings for refextract
# from inspirehep.utils.knowledge import get_mappings_from_kbname


def extract_journal_info(obj, eng):
    """Extract journal, volume etc. from any freetext publication info."""
    publication_info = get_value(obj.data, "publication_info")
    if not publication_info:
        return

    new_publication_info = []
    for pubnote in publication_info:
        if not pubnote:
            continue
        freetext = pubnote.get("pubinfo_freetext")
        if freetext:
            if isinstance(freetext, (list, tuple)):
                freetext = ". ".join(freetext)
            extracted_publication_info = extract_journal_reference(
                freetext,
                # override_kbs_files={
                #    'journals': get_mappings_from_kbname(['REFEXTRACT_KB_NAME'])
                # }
            )
            if extracted_publication_info:
                if "volume" in extracted_publication_info:
                    pubnote["journal_volume"] = extracted_publication_info.get(
                        "volume"
                    )
                if "title" in extracted_publication_info:
                    pubnote["journal_title"] = extracted_publication_info.get(
                        "title"
                    )
                if "year" in extracted_publication_info:
                    pubnote["year"] = int(extracted_publication_info.get(
                        "year"
                    ))
                if "page" in extracted_publication_info:
                    page_start, page_end, artid = split_page_artid(
                        extracted_publication_info.get("page"))
                    if page_start:
                        pubnote["page_start"] = page_start
                    if page_end:
                        pubnote["page_end"] = page_end
                    if artid:
                        pubnote["artid"] = artid
        if any(value for value in pubnote.values()):
            new_publication_info.append(pubnote)

    obj.data["publication_info"] = new_publication_info


def extract_references(filepath):
    """Extract references from PDF and return in INSPIRE format."""
    references = extract_references_from_file(
        filepath,
        reference_format="{title},{volume},{page}",
    )
    mapped_references = []
    if references.get('references'):
        for ref in references.get('references'):
            reference = {
                'curated_relation': False,
                'raw_refs': [
                    {
                        'position': '',
                        'schema': '',
                        'source': '',
                        'value': json.dumps(ref),
                    }
                ],
                'record': {
                    '$ref': ''
                },
                'reference': {
                    'authors': ref.get('author'),
                    'book_series': ref.get('book_series'),
                    'collaboration': ref.get('collaboration'),
                    'dois': ref.get('dois'),
                    'imprint': ref.get('imprint'),
                    'misc': ref.get('misc'),
                    'number': ref.get('linemarker'),
                    'persistent_identifiers': ref.get(
                        'persistent_identifiers'
                    ),
                    'publication_info': {
                        'year': ref.get('year'),
                        'journal_title': ref.get('journal_title'),
                        'journal_volume': ref.get('journal_volume'),
                        'page_start': ref.get('journal_page'),
                        'artid': ref.get('journal_reference'),
                    },
                    'texkey': ref.get('texkey'),
                    'titles': ref.get('titles'),
                    'urls': ref.get('urls'),
                },
            }
            mapped_references.append(reference)

    return mapped_references
