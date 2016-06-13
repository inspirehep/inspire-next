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

"""Functions related to the main INSPIRE-HEP ticketing system."""

from __future__ import absolute_import, division, print_function

from flask import current_app
from rt import Rt, ConnectionError


def get_instance():
    """Make a RT instance and return it."""
    url = current_app.config.get("CFG_BIBCATALOG_SYSTEM_RT_URL", "")
    login = current_app.config.get("CFG_BIBCATALOG_SYSTEM_RT_DEFAULT_USER", "")
    password = current_app.config.get("CFG_BIBCATALOG_SYSTEM_RT_DEFAULT_PWD", "")

    if url:
        tracker = Rt(
            url=url,
            default_login=login,
            default_password=password,
        )
        tracker.login()
        return tracker


def retry_if_connection_problems(exception):
    """Return True if exception is an ConnectionError in Rt."""
    return isinstance(exception, ConnectionError)
