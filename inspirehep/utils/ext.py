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

"""Utils extension."""

from __future__ import absolute_import, division, print_function

from rt import AuthorizationError
from .tickets import InspireRt


class INSPIREUtils(object):

    """Utils extension."""

    def __init__(self, app=None):
        """Initialize the extension."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the application."""
        self.rt_instance = self.create_rt_instance(app)
        app.extensions["inspire-utils"] = self

    def create_rt_instance(self, app):
        """Make a RT instance and return it."""
        url = app.config.get("CFG_BIBCATALOG_SYSTEM_RT_URL", "")
        login = app.config.get("CFG_BIBCATALOG_SYSTEM_RT_DEFAULT_USER", "")
        verify_cert = app.config.get(
            "CFG_BIBCATALOG_SYSTEM_RT_VERIFY_SSL",
            True,
        )
        password = app.config.get(
            "CFG_BIBCATALOG_SYSTEM_RT_DEFAULT_PWD", "")
        if url:
            tracker = InspireRt(
                url=url,
                default_login=login,
                default_password=password,
                verify_cert=verify_cert,
            )
            loggedin = tracker.login()
            if not loggedin:
                raise AuthorizationError(
                    "RT login credentials in the app.config are invalid")
            return tracker
