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

""" Record related utils."""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.migrator.tasks import chunker
from invenio_records.api import Record
from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_schema
)


def get_endpoint_from_record(record):
    """Return the endpoint corresponding to a record."""
    pid_type = get_pid_type_from_schema(record['$schema'])
    endpoint = get_endpoint_from_pid_type(pid_type)

    return endpoint


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
                total_matches = total_matches +1
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
