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

"""PIDStore utils."""

from __future__ import absolute_import, division, print_function

from flask import current_app
from six import iteritems
from six.moves.urllib.parse import urlsplit


def _get_pid_type_endpoint_map():
    pid_type_endpoint_map = {}
    for key, value in iteritems(current_app.config['RECORDS_REST_ENDPOINTS']):
        if value.get('default_endpoint_prefix'):
            pid_type_endpoint_map[value['pid_type']] = key

    return pid_type_endpoint_map


def get_endpoint_from_pid_type(pid_type):
    """Return the endpoint corresponding to a ``pid_type``."""
    PID_TYPE_TO_ENDPOINT = _get_pid_type_endpoint_map()

    return PID_TYPE_TO_ENDPOINT[pid_type]


def get_pid_type_from_endpoint(endpoint):
    """Return the ``pid_type`` corresponding to an endpoint."""
    ENDPOINT_TO_PID_TYPE = {
        v: k for k, v in iteritems(_get_pid_type_endpoint_map())}

    return ENDPOINT_TO_PID_TYPE[endpoint]


def get_pid_type_from_schema(schema):
    """Return the ``pid_type`` corresponding to a schema URL.

    The schema name corresponds to the ``endpoint`` in all cases except for
    Literature records. This implementation exploits this by falling back to
    ``get_pid_type_from_endpoint``.
    """
    def _get_schema_name_from_schema(schema):
        return urlsplit(schema).path.split('/')[-1].split('.')[0]

    schema_name = _get_schema_name_from_schema(schema)
    if schema_name == 'hep':  # FIXME: remove when hep.json -> literature.json
        return 'lit'

    return get_pid_type_from_endpoint(schema_name)
