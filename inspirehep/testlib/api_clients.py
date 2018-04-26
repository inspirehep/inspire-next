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

import json
import requests
import re

from urlparse import urljoin
from inspirehep.testlib.api_entries import HoldingpenEntry, LiteratureEntry


class Session(requests.Session):
    def __init__(self, *args, **kwargs):
        self._base_url = kwargs.pop('base_url', 'http://inspirehep.local')
        super(Session, self).__init__(*args, **kwargs)

    def get_full_url(self, *paths):
        full_url = self._base_url
        for path in paths[:-1]:
            if not path.endswith('/'):
                path = path + '/'

            full_url = urljoin(full_url, path)

        full_url = urljoin(full_url, paths[-1])
        return full_url

    def get(self, url, *args, **kwargs):
        full_url = self.get_full_url(url)
        return requests.get(full_url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        full_url = self.get_full_url(url)
        return requests.post(full_url, *args, **kwargs)


class InspireApiClient(object):
    """Inspire Client for end-to-end testing"""
    LOCAL_LOGIN_URL = '/login/?next=%2F&local=1'

    def __init__(self, auto_login=True, base_url='http://inpirehep.local'):
        self.auto_login = auto_login
        self._session = None
        self._client = Session(base_url=base_url)

        if auto_login:
            self.login_local()

        self.holdingpen = HoldingpenApiClient(self._client)
        self.literature = LiteratureApiClient(self._client)

    def login_local(self, user='admin@inspirehep.net', password='123456'):
        """Perform a local log-in in Inspire storing the session"""
        login_data = {
            'csrf_token': '',
            'email': user,
            'password': password,
        }
        page = self._client.get(self.LOCAL_LOGIN_URL)
        csrf_token = re.search(
            '(?<=name="csrf_token" type="hidden" value=")[^"]*',
            page.text
        ).group()
        login_data['csrf_token'] = csrf_token
        response = self._client.post(
            url=self.LOCAL_LOGIN_URL,
            data=login_data,
            allow_redirects=False
        )
        return response


class HoldingpenApiClient(object):
    """Client for the Inspire Holdingpen"""
    HOLDINGPEN_API_URL = '/api/holdingpen/'

    def __init__(self, client):
        self._client = client

    def get_list_entries(self):
        resp = self._client.get(self.HOLDINGPEN_API_URL)
        return [
            HoldingpenEntry(json=e['_source'], id=e['_id'])
            for e in resp.json()['hits']['hits']
        ]

    def get_detail_entry(self, holdingpen_id):
        resp = self._client.get(
            self._client.get_full_url(self.HOLDINGPEN_API_URL, holdingpen_id),
        )
        return HoldingpenEntry(resp.json())


class LiteratureApiClient(object):
    """Client for the Inspire Literature section"""
    LITERATURE_API_URL = '/api/literature/'

    def __init__(self, client):
        self._client = client

    def get_record(self, rec_id):
        resp = self._client.get(
            self._client.get_full_url(self.LITERATURE_API_URL, rec_id),
        )
        return LiteratureEntry(resp.json())


class RobotuploadCallbackResult(dict):
    def __init__(self, recid, error_message, success, marcxml, url):
        self.update(
            {
                "recid": recid,
                "error_message": error_message,
                "success": success,
                "marcxml": marcxml,
                "url": url,
            }
        )


class CallbackClient(object):
    """Client for the Inspire callbacks"""
    CALLBACK_URL = '/callback/workflows'

    def __init__(self, client):
        self._client = client

    def robotupload(self, nonce, results):
        """
        Args:
            nonce(int): nonce parameter passed to robotupload, usually the
                workflow id.
            results(list[RobotuploadCallbackResult]): list of robotupload
                results.
        """
        data = {
            "nonce": nonce,
            "results": results,
        }

        response = self._client.post(
            self._client.get_full_url(self.CALLBACK_URL, '/robotupload'),
            data=json.dumps(data),
            headers={'Content-type': 'application/json'}
        )
        return response

    def webcoll(self, recids):
        """
        Args:
            recids(list(int)): list of recids that webcoll parsed.
        """
        data = {"recids": recids}

        response = self._client.post(
            '/webcoll',
            data=data,
            headers={'Content-type': 'application/x-www-form-urlencoded'}
        )
        return response
