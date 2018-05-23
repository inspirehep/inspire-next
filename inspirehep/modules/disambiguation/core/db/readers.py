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

"""Disambiguation core DB readers."""

from __future__ import absolute_import, division, print_function

from elasticsearch_dsl import Q

from invenio_records.models import RecordMetadata

from inspirehep.modules.search.api import LiteratureSearch

SIGNATURE_FIELDS = [
    'authors.affiliations',
    'authors.curated_relation',
    'authors.full_name',
    'authors.record',
    'authors.signature_block',
    'authors.uuid',
]


def get_all_curated_signatures():
    """Get all curated signatures from the DB.

    Walks through all Literature records and collects all signatures
    that were marked as curated in order to build the training set
    for ``BEARD``.

    Yields:
        dict: a curated signature.

    """
    query = RecordMetadata.query.with_entities(RecordMetadata.json)

    for record in query.yield_per(1000):
        for signature in record.json.get('authors', []):
            if signature.get('curated_relation'):
                yield signature


def get_signatures_matching_a_phonetic_encoding(phonetic_encoding):
    """Get all signatures matching a phonetic encoding from ES.

    Args:
        phonetic_encodings(str): a phonetic encoding.

    Yields:
        dict: a signature matching the phonetic encoding.

    """
    query = Q('term', authors__signature_block__raw=phonetic_encoding)
    search_by_phonetic_encoding = LiteratureSearch().query('nested', path='authors', query=query)\
                                                    .params(_source=SIGNATURE_FIELDS, size=9999)

    for record in search_by_phonetic_encoding:
        for signature in record.authors:
            if signature.signature_block == phonetic_encoding:
                yield signature.to_dict()
