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

"""API clients for Inspire"""

from __future__ import absolute_import, division, print_function

import requests
import re

from inspirehep.testlib.api_entries import HoldingpenEntry, LiteratureEntry

WEB_URL = 'http://test-web-e2e:5000'
LOCAL_LOGIN_URL = '/login/?next=%2F&local=1'
HOLDINGPEN_API_URL = '/api/holdingpen/'
LITERATURE_API_URL = '/api/literature/'


def _get_url(url):
    if not url.startswith('/'):
        url = '/{}'.format(url)
    return '{}{}'.format(WEB_URL, url)


class InspireApiClient(object):
    """Inspire Client for end-to-end testing"""

    def __init__(self, auto_login=True):
        self.auto_login = auto_login
        self._session = None

        if auto_login:
            self.login_local()

        self.holdingpen = HoldingpenApiClient(self._session)
        self.literature = LiteratureApiClient(self._session)

    def login_local(self):
        """Perform a local log-in in Inspire storing the session"""
        login_data = {
            'csrf_token': '',
            'email': 'admin@inspirehep.net',
            'password': '123456'
        }
        login_url = _get_url(LOCAL_LOGIN_URL)
        page = requests.get(login_url)
        csrf_token = re.search(
            '(?<=name="csrf_token" type="hidden" value=")[^"]*',
            page.text
        ).group()
        cookie = re.search('session=[^; ]*', page.headers['Set-Cookie']).group()
        login_data['csrf_token'] = csrf_token
        response = requests.post(
            url=login_url,
            data=login_data,
            headers={'Cookie': cookie},
            allow_redirects=False
        )
        self._session = {'Cookie': response.headers['Set-Cookie']}
        return response


class HoldingpenApiClient(object):
    """Client for the Inspire Holdingpen"""

    def __init__(self, login_headers):
        if not login_headers:
            raise ValueError('Can not query holdingpen without being logged-in')
        self._login_headers = login_headers

    def get_list_entries(self):
        resp = requests.get(
            _get_url(HOLDINGPEN_API_URL),
            headers=self._login_headers
        )
        return [
            HoldingpenEntry(json=e['_source'], id=e['_id'])
            for e in resp.json()['hits']['hits']
        ]

    def get_detail_entry(self, holdingpen_id):
        resp = requests.get(
            "{}{}".format(_get_url(HOLDINGPEN_API_URL), holdingpen_id),
            headers=self._login_headers
        )
        return HoldingpenEntry(resp.json())


class LiteratureApiClient(object):
    """Client for the Inspire Literature section"""

    def __init__(self, login_headers):
        self._login_headers = login_headers

    def get_record(self, rec_id):
        resp = requests.get(
            "{}{}".format(_get_url(LITERATURE_API_URL), rec_id),
            headers=self._login_headers
        )
        return LiteratureEntry(resp.json())
