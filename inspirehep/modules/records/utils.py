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

import requests
import sys
import traceback
from flask import current_app
from six.moves.urllib.parse import urlparse

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_schema
)


class FailedToOpenUrlPath(Exception):

    def __init__(self, path, exception=None, msg=None):
        self.exception = exception
        exc_info = sys.exc_info()
        first_line_msg = "Failed to open %s\n" % path
        msg = msg or ''.join(traceback.format_exception(*exc_info))
        super(FailedToOpenUrlPath, self).__init__(first_line_msg + msg)


def get_endpoint_from_record(record):
    """Return the endpoint corresponding to a record."""
    pid_type = get_pid_type_from_schema(record['$schema'])
    endpoint = get_endpoint_from_pid_type(pid_type)

    return endpoint


def get_detailed_template_from_record(record):
    """Return the detailed template corresponding to the given record."""
    endpoint = get_endpoint_from_record(record)
    return current_app.config['RECORDS_UI_ENDPOINTS'][endpoint]['template']


def open_url_or_path(file_path):
    known_schemes = ['http', 'https']
    try:
        if urlparse(file_path).scheme in known_schemes:
            resp = requests.get(url=file_path, stream=True)
            if resp.status_code == 200:
                resp.raw.decode_content = True
                return resp.raw
            else:
                msg = 'Got response {}:{}'.format(resp.status_code, resp.text)
                raise FailedToOpenUrlPath(path=file_path, msg=msg)
        else:
            file_descriptor = open(file_path, mode='r')
            return file_descriptor
    except FailedToOpenUrlPath:
        raise
    except Exception as error:
        raise FailedToOpenUrlPath(path=file_path, exception=error)
