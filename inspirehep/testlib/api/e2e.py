# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""/holdingpen endopint api client and resources."""

from __future__ import absolute_import, division, print_function


class E2EClient(object):
    """Client for the Inspire E2E api."""
    INIT_DB_URL = '/e2e/init_db'
    INIT_ES_URL = '/e2e/init_es'
    INIT_FIXTURES_URL = '/e2e/init_fixtures'
    SCHEDULE_CRAWL_URL = '/e2e/schedule_crawl'

    def __init__(self, client):
        self._client = client

    def init_db(self):
        resp = self._client.get(self.INIT_DB_URL)
        resp.raise_for_status()
        return resp.json()

    def init_es(self):
        resp = self._client.get(self.INIT_ES_URL)
        resp.raise_for_status()
        return resp.json()

    def init_fixtures(self):
        resp = self._client.get(self.INIT_FIXTURES_URL)
        resp.raise_for_status()
        return resp.json()

    def schedule_crawl(self, **params):
        resp = self._client.post(
            self.SCHEDULE_CRAWL_URL,
            json=params,
        )
        resp.raise_for_status()
        return resp.json()
