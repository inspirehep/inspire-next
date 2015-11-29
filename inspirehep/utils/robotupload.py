# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Function for sending robotuploads to other Invenio instances."""

import os
import requests


def make_robotupload_marcxml(url, marcxml, mode, **kwargs):
    """Make a robotupload request."""
    from invenio_utils.url import make_user_agent_string
    from inspirehep.utils.text import clean_xml

    from invenio_base.globals import cfg
    headers = {
        "User-agent": make_user_agent_string("inspire"),
        "Content-Type": "application/marcxml+xml",
    }
    if url is None:
        base_url = cfg.get("CFG_ROBOTUPLOAD_SUBMISSION_BASEURL")
    else:
        base_url = url

    url = os.path.join(base_url, "batchuploader/robotupload", mode)
    return requests.post(
        url=url,
        data=str(clean_xml(marcxml)),
        headers=headers,
        params=kwargs,
    )
