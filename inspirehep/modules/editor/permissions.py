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

from __future__ import absolute_import, division, print_function

from functools import wraps

from flask import abort, session
from flask_login import current_user

from invenio_access.permissions import (
    ParameterizedActionNeed,
    Permission,
)

from inspirehep.modules.pidstore.utils import get_pid_type_from_endpoint
from inspirehep.modules.records.permissions import has_update_permission
from inspirehep.utils.record_getter import get_db_record


action_editor_use_api = ParameterizedActionNeed(
    'editor-use-api', argument=None
)

editor_use_api_permission = Permission(
    action_editor_use_api
)


def editor_permission(fn):

    @wraps(fn)
    def decorator(endpoint, pid_value, **kwargs):
        cache_key = 'editor-permission-{0}-{1}'.format(
            endpoint,
            pid_value
        )
        is_allowed = session.get(cache_key)
        if is_allowed is not None:
            if is_allowed:
                return fn(endpoint, pid_value, **kwargs)
            else:
                abort(403)

        pid_type = get_pid_type_from_endpoint(endpoint)
        record = get_db_record(pid_type, pid_value)

        is_allowed = has_update_permission(current_user, record)
        session[cache_key] = is_allowed
        if is_allowed:
            return fn(endpoint, pid_value, **kwargs)
        else:
            abort(403)

    return decorator
