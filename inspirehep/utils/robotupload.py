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

"""Utils for sending robotuploads to other Invenio instances."""

from __future__ import absolute_import, division, print_function

import os

import requests
from six import text_type
from flask import current_app

from .url import make_user_agent_string


def make_robotupload_marcxml(url, marcxml, mode, **kwargs):
    """Make a robotupload request."""
    headers = {
        "User-agent": make_user_agent_string("inspire"),
        "Content-Type": "application/marcxml+xml",
    }
    if url is None:
        base_url = current_app.config.get("LEGACY_ROBOTUPLOAD_URL")
    else:
        base_url = url

    if isinstance(marcxml, text_type):
        marcxml = marcxml.encode('utf8')

    if base_url:
        url = os.path.join(base_url, "batchuploader/robotupload", mode)
        return requests.post(
            url=url,
            data=marcxml,
            headers=headers,
            params=kwargs,
        )
    else:
        raise ValueError(
            "Base URL missing for robotupload. "
            "Please check `LEGACY_ROBOTUPLOAD_URL` config."
        )
