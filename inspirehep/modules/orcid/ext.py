# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import (
    absolute_import,
    division,
    print_function)

import orcid


class INSPIREOrcid(object):
    """INSPIRE orcid extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self.app = app
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """Initialize application object."""
        app.extensions['inspire-orcid'] = self

        orcid_base_url = app.config['OAUTHCLIENT_REMOTE_APPS'][
            'orcid']['params']['base_url']
        orcid_consumer_secret = app.config[
            'OAUTHCLIENT_ORCID_CREDENTIALS']['consumer_secret']
        orcid_consumer_key = app.config[
            'OAUTHCLIENT_ORCID_CREDENTIALS']['consumer_key']

        self.sandbox = (orcid_base_url == 'https://pub.sandbox.orcid.org/')

        self.orcid_api = orcid.MemberAPI(
            orcid_consumer_secret, orcid_consumer_key, sandbox=self.sandbox)
