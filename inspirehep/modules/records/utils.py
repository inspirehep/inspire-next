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

from inspire_utils.record import get_value
from inspire_utils.helpers import force_list
from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_schema
)
from inspirehep.utils.record_getter import get_db_records


def get_endpoint_from_record(record):
    """Return the endpoint corresponding to a record."""
    pid_type = get_pid_type_from_schema(record['$schema'])
    endpoint = get_endpoint_from_pid_type(pid_type)

    return endpoint


def get_pid_from_record_uri(record_uri):
    """Transform a URI to a record into a (pid_type, pid_value) pair."""
    parts = [part for part in record_uri.split('/') if part]
    pid_type = parts[-2][:3]
    pid_value = parts[-1]

    return pid_type, pid_value


def get_linked_records_in_field(record, field_path):
    """Get all linked records in a given field.

    Args:
        record (dict): the record containing the links
        field_path (string): a dotted field path specification understandable
            by ``get_value``, containing a json reference to another record.

    Returns:
        Iterator[dict]: an iterator on the linked record.

    Warning:
        Currently, the order in which the linked records are yielded is
        different from the order in which they appear in the record.

    Example:
        >>> record = {'references': [
        ...     {'record': {'$ref': 'https://labs.inspirehep.net/api/literature/1234'}},
        ...     {'record': {'$ref': 'https://labs.inspirehep.net/api/data/421'}},
        ... ]}
        >>> get_linked_record_in_field(record, 'references.record')
        [...]
    """
    full_path = '.'.join([field_path, '$ref'])
    pids = force_list([get_pid_from_record_uri(rec) for rec in get_value(record, full_path, [])])
    return get_db_records(pids)
