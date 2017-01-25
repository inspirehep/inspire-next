# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON model definition for HEP."""

from __future__ import absolute_import, division, print_function

from dojson import Overdo

from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value

from ..model import FilterOverdo, add_schema, clean_record
from ..utils import (
    force_single_element,
    get_record_ref,
    classify_field,
)


def add_inspire_category_from_arxiv_categories(record, blob):
    if not record.get('arxiv_eprints') or record.get('inspire_categories'):
        return record

    record.setdefault('inspire_categories', [])
    for arxiv_category in get_value(record, 'arxiv_eprints.categories', default=[]):
        inspire_category = classify_field(arxiv_category)
        if inspire_category:
            record['inspire_categories'].append({
                'term': inspire_category,
                'source': 'arxiv'
            })

    return record


def ensure_document_type(record, blob):
    if not record.get('document_type'):
        record['document_type'] = ['article']
    return record


def check_980(record, blob):
    record.setdefault('980', []).append({'a', 'HEP'})
    if blob.get('arxiv_eprints'):
        record['980'].append({'a': 'arXiv'})
    return record

hep_filters = [
    add_schema('hep.json'),
    add_inspire_category_from_arxiv_categories,
    clean_record,
    ensure_document_type,
]

hep2marc_filters = [
    check_980,
    clean_record,
]

hep = FilterOverdo(filters=hep_filters)
hep2marc = FilterOverdo(filters=hep2marc_filters)
