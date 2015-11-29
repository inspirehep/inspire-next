# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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


# from invenio.legacy.refextract.api import extract_journal_reference

from inspirehep.utils.helpers import get_record_from_model


def extract_journal_info(obj, eng):
    """Extract journal, volume etc. from any freetext publication info."""
    model = eng.workflow_definition.model(obj)
    record = get_record_from_model(model)

    publication_info = record.get("publication_info")
    if not publication_info:
        return

    new_publication_info = []
    for pubnote in publication_info:
        freetext = pubnote.get("pubinfo_freetext")
        if freetext:
            extracted_publication_info = extract_journal_reference(freetext)
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

    record["publication_info"] = new_publication_info
    model.update()
