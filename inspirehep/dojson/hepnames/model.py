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

"""DoJSON model definition for HEPNames."""

from __future__ import absolute_import, division, print_function

from ..model import FilterOverdo, add_schema, add_collection, clean_record


def ensure_hepnames(record, blob):
    record.setdefault('980', []).append({'a': 'HEPNAMES'})

    return record


hepnames_filters = [
    add_schema('authors.json'),
    add_collection('Authors'),
    clean_record,
]

hepnames2marc_filters = [
    ensure_hepnames,
    clean_record,
]

hepnames = FilterOverdo(filters=hepnames_filters)
hepnames2marc = FilterOverdo(filters=hepnames2marc_filters)
