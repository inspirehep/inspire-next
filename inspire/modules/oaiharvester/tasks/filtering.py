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

import os
import traceback


def get_content_from_file(obj, eng):
    """Replace object data with content from filepath in object data."""
    from invenio.modules.workflows.errors import WorkflowError

    filepath = obj.data
    try:
        assert filepath
        is_found = os.path.exists(filepath)
        assert is_found
    except (AssertionError, TypeError):
        err_msg = "Not a valid file found in {0}:\n{1}".format(
            filepath,
            traceback.format_exc()[:-1]
        )
        obj.log.error(err_msg)
        payload = {"filepath": filepath}
        raise WorkflowError(err_msg, eng.uuid, obj.id, payload)

    obj.log.info("Found file at {0}".format(filepath))
    content = ""
    with open(filepath) as fd:
        content = fd.read()

    if not content:
        err_msg = "No content found in {0}".format(filepath)
        obj.log.error(err_msg)
        payload = {"filepath": filepath}
        raise WorkflowError(err_msg, eng.uuid, obj.id, payload)

    obj.data = content
    obj.log.info("Read {0} characters from {1}".format(len(content), filepath))
