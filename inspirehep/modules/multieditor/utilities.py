# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function, division


from invenio_records.api import Record
from jsonschema import ValidationError
from inspire_schemas.api import validate

from inspirehep.utils.record import get_inspire_patch
from inspirehep.modules.migrator.tasks import chunker


def filter_records(uuids, filters):
    '''
    :param uuids: uuids of the records
    :param filters: filters to be applied(format: {keypath: , value:})
    :return:
    '''
    total_matches = 0
    is_match = False
    for i, chunk in enumerate(chunker(uuids, 200)):
        records = Record.get_records(chunk)
        for record in records:
            for single_filter in filters:
                temp_record = record
                is_match = recursive_filter(temp_record, single_filter['keys'], single_filter['value'], 0)
                if not is_match:
                    break
            if is_match:
                total_matches = total_matches + 1
    return total_matches


def recursive_filter(record, keys, value, position):
    if position == len(keys):
        return record == value
    if not record.get(keys[position]):
        return False
    record = record[keys[position]]
    if isinstance(record, list):
        for index, array_record in enumerate(record):
            if recursive_filter(record[index], keys, value, position+1):
                return True
        return False
    else:
        return recursive_filter(record, keys, value, position + 1)


def compare_records(old_records, new_records, schema):
    """
    Compares and validates the records after the actions have been applied
    :param old_records: records before actions
    :param new_records: records after actions
    :param schema: corresponding schema of the records
    :return:json patches[object] and errors[string]
    """
    json_patches = []
    errors = []
    for index, new_record in enumerate(new_records):
        json_patches.append(get_inspire_patch(old_records[index], new_record))
        try:
            validate(new_record, schema)
        except ValidationError as e:
            errors.append(e.message)
        else:
            errors.append(None)
    return json_patches, errors