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

from refextract import extract_journal_reference, extract_references_from_file

from inspire_schemas.api import ReferenceBuilder
from inspire_schemas.utils import split_page_artid
from inspire_utils.record import get_value
from inspirehep.utils.helpers import force_list, maybe_int


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
                    year = maybe_int(extracted_publication_info.get('year'))
                    if year is not None:
                        pubnote['year'] = year
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


@timeout(5 * 60)
def extract_references(filepath, source=None, custom_kbs_file=None):
    """Extract references from PDF and return in INSPIRE format."""
    references = extract_references_from_file(
        filepath,
        override_kbs_files=custom_kbs_file,
        reference_format=u'{title},{volume},{page}'
    )

    result = []

    for reference in references:
        rb = ReferenceBuilder()
        mapping = [
            ('author', rb.add_refextract_authors_str),
            ('collaboration', rb.add_collaboration),
            ('doi', rb.add_uid),
            ('hdl', rb.add_uid),
            ('isbn', rb.add_uid),
            ('journal_reference', rb.set_pubnote),
            ('linemarker', rb.set_label),
            ('misc', rb.add_misc),
            ('publisher', rb.set_publisher),
            ('raw_ref', lambda raw_ref: rb.add_raw_reference(raw_ref, source)),
            ('reportnumber', rb.add_report_number),
            ('texkey', rb.set_texkey),
            ('title', rb.add_title),
            ('url', rb.add_url),
            ('year', rb.set_year),
        ]

        for field, method in mapping:
            for el in force_list(reference.get(field)):
                if el:
                    method(el)

        result.append(rb.obj)

    return result
