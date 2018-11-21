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

"""Migrator utils."""

from __future__ import absolute_import, division, print_function

from dojson.contrib.marc21.utils import create_record

from inspire_utils.helpers import force_list


REAL_COLLECTIONS = (
    'INSTITUTION',
    'EXPERIMENT',
    'JOURNALS',
    'JOURNALSNEW',
    'HEPNAMES',
    'HEP',
    'JOB',
    'JOBHIDDEN',
    'CONFERENCES',
    'DATA',
)


def get_collection(marc_record):
    collections = set()
    for field in force_list(marc_record.get('980__')):
        for v in field.values():
            for e in force_list(v):
                collections.add(e.upper().strip())
    if 'DELETED' in collections:
        return 'DELETED'
    for collection in collections:
        if collection in REAL_COLLECTIONS:
            return collection
    return 'HEP'


def get_collection_from_marcxml(marcxml):
    marc_record = create_record(marcxml, keep_singletons=False)
    return get_collection(marc_record)
