# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

"""Records checkers."""

from __future__ import absolute_import, division, print_function

from collections import defaultdict

from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import JSONB

from invenio_records.models import RecordMetadata
from inspire_utils.record import get_value


def increase_cited_count(result, identifier, core):
    """Increases the number of times a reference with the same identifier has appeared"""
    if core:
        result[identifier] = (result[identifier][0] + 1, result[identifier][1])
    else:
        result[identifier] = (result[identifier][0], result[identifier][1] + 1)


def calculate_score_of_reference(counted_reference):
    """Given a tuple of the number of times cited by a core record and a non core record,
    calculate a score associated with a reference.

    The score is calculated giving five times more importance to core records"""
    _, (core_count, non_core_count) = counted_reference
    return core_count * 5 + non_core_count


def order_dictionary_into_list(result_dict):
    """Return ``result_dict`` as an ordered list of tuples"""
    sorted_list = sorted(result_dict.items(), key=calculate_score_of_reference, reverse=True)

    return sorted_list


def get_all_unlinked_references():
    """Return a list of dict, in which each dictionary corresponds to one reference object
    and the status of core or non core"""
    query = (
        RecordMetadata.query
        .filter(
            type_coerce(RecordMetadata.json, JSONB)['_collections']
            .contains(['Literature'])
        )
        .with_entities(RecordMetadata.json)
    )

    for record in query.yield_per(1000):
        core = record.json.get('core')
        for reference in record.json.get('references', []):
            if 'record' not in reference:
                yield {'core': core, 'reference': reference}


def check_unlinked_references():
    """Return two lists with the unlinked references that have a doi or an arxiv id.

    If the reference read has a doi or an arxiv id, it is stored in the data structure.
    Once all the data is read, it is ordered by most relevant to less relevant."""

    result_doi, result_arxiv = defaultdict(lambda: (0, 0)), defaultdict(lambda: (0, 0))

    data = get_all_unlinked_references()

    for reference in data:
        dois = get_value(reference, 'reference.reference.dois', [])
        for doi in dois:
            increase_cited_count(result_doi, doi, reference["core"])
        arxiv_id = get_value(reference, 'reference.reference.arxiv_eprint', '')
        if arxiv_id:
            increase_cited_count(result_arxiv, arxiv_id, reference["core"])

    result_doi = order_dictionary_into_list(result_doi)
    result_arxiv = order_dictionary_into_list(result_arxiv)

    return result_doi, result_arxiv
