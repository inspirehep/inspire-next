# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

import os
import requests


def make_robotupload_marcxml(url, marcxml, **kwargs):
    """Make a robotupload request and return it."""
    from invenio.utils.url import make_user_agent_string
    headers = {
        "User-agent": make_user_agent_string("inspire"),
        "Content-Type": "application/marcxml+xml",
        "Content-Length": len(marcxml),
    }
    url = os.path.join(url, "batchuploader/robotupload/insert")
    return requests.post(
        url,
        data=marcxml,
        headers=headers,
        params=kwargs,
    )
