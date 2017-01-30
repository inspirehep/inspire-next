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
    classify_field,
    force_single_element,
    get_record_ref,
    classify_field,
    validate,
)


def add_book_info(record, blob):
    """Add link to the appropriate book record."""
    collections = []
    if 'collections' in record:
        for c in record.get('collections', ''):
            if c.get('primary', ''):
                collections.append(c.get('primary').lower())
        if 'bookchapter' in collections:
            pubinfos = force_force_list(blob.get("773__", []))
            for pubinfo in pubinfos:
                recid = force_single_element(pubinfo.get('0'))
                try:
                    recid = int(recid)
                    record['book'] = {'record':
                                      get_record_ref(recid, 'literature')}
                except (ValueError, TypeError):
                    pass

    return record


def add_inspire_category(record, blob):
    if not record.get('arxiv_eprints') or record.get('inspire_categories'):
        return record

    record.setdefault('inspire_categories', [])
    for arxiv_category in get_value(record, 'arxiv_eprints.categories', default=[]):
        inspire_category = classify_field(arxiv_category)
        if inspire_category:
            record['inspire_categories'].append({
                'term': inspire_category,
                'source': 'arxiv',
            })

    return record


hep_filters = [
    add_schema('hep.json'),
    validate,
    add_book_info,
    add_inspire_category,
    clean_record,
]

hep2marc_filters = [
    clean_record,
]

hep = FilterOverdo(filters=hep_filters)
hep2marc = FilterOverdo(filters=hep2marc_filters)
