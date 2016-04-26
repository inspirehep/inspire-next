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


from refextract import extract_journal_reference, extract_references_from_file

from inspirehep.utils.helpers import get_record_from_model

# FIXME get journal mappings for refextract
# from inspirehep.utils.knowledge import get_mappings_from_kbname


def extract_journal_info(obj, eng):
    """Extract journal, volume etc. from any freetext publication info."""
    publication_info = obj.data.get("publication_info")
    if not publication_info:
        return

    new_publication_info = []
    for pubnote in publication_info:
        freetext = pubnote.get("pubinfo_freetext")
        if freetext:
            extracted_publication_info = extract_journal_reference(
                freetext,
                # override_kbs_files={'journals': get_mappings_from_kbname(cfg['REFEXTRACT_KB_NAME'])}
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
                    pubnote["year"] = extracted_publication_info.get(
                        "year"
                    )
                if "page" in extracted_publication_info:
                    pubnote["page_artid"] = extracted_publication_info.get(
                        "page"
                    )
        new_publication_info.append(pubnote)

    obj.data["publication_info"] = new_publication_info


def extract_references(filepath):
    """Extract references from PDF and return in INSPIRE format."""
    references = extract_references_from_file(
        filepath,
        reference_format="{title},{volume},{page}",
        # override_kbs_files={'journals': get_mappings_from_kbname(cfg['REFEXTRACT_KB_NAME'])}
    )
    mapped_references = []
    if references.get('references'):
        for ref in references.get('references'):
            reference = {}
            reference["journal_pubnote"] = ref.get('journal_reference')
            reference["year"] = ref.get('year')
            reference["collaboration"] = ref.get('collaboration')
            reference["title"] = ref.get('title')
            reference["misc"] = ref.get('misc')
            reference["number"] = ref.get('linemarker')
            reference["authors"] = ref.get('author')
            reference["isbn"] = ref.get('isbn')
            reference["doi"] = ref.get('doi')
            reference["report_number"] = ref.get('reportnumber')
            reference["publisher"] = ref.get('publisher')
            reference["recid"] = ref.get('recid')

            for key, value in reference.items():
                if value and isinstance(value, list):
                    reference[key] = ",".join(value)
                elif not value:
                    del reference[key]
            mapped_references.append(reference)
    return mapped_references
