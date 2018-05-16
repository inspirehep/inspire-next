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

"""Main API client for Inspire"""

from __future__ import absolute_import, division, print_function

import requests
import re

from posixpath import join as urljoin
from inspirehep.testlib.api.literature import LiteratureApiClient
from inspirehep.testlib.api.callback import CallbackClient
from inspirehep.testlib.api.holdingpen import HoldingpenApiClient


class Session(requests.Session):
    def __init__(self, *args, **kwargs):
        self._base_url = kwargs.pop('base_url', 'http://inspirehep.local')
        super(Session, self).__init__(*args, **kwargs)

    def get_full_url(self, *paths):
        full_path = urljoin(*paths)
        if not full_path.startswith('/'):
            full_path = '/' + full_path
        return self._base_url + full_path

    def bare_get(self, *args, **kwargs):
        return super(Session, self).get(*args, **kwargs)

    def bare_post(self, *args, **kwargs):
        return super(Session, self).post(*args, **kwargs)

    def get(self, *args, **kwargs):
        full_url = self.get_full_url(*args)
        return super(Session, self).get(full_url, **kwargs)

    def post(self, *args, **kwargs):
        full_url = self.get_full_url(*args)
        return super(Session, self).post(full_url, **kwargs)

    @staticmethod
    def response_to_string(res):
        """
        :param res: :class:`requests.Response` object
        Parse the given request and generate an informative string from it
        """
        if 'Authorization' in res.request.headers:
            res.request.headers['Authorization'] = "*****"
        return """
    ####################################
    url = %s
    headers = %s
    -------- data sent -----------------
    %s
    ------------------------------------
    @@@@@ response @@@@@@@@@@@@@@@@
    headers = %s
    code = %d
    reason = %s
    --------- data received ------------
    %s
    ------------------------------------
    ####################################
    """ % (res.url,
           str(res.request.headers),
           res.request.body,
           res.headers,
           res.status_code,
           res.reason,
           res.text)


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
        self.callback = CallbackClient(self._client)

    def login_local(self, user='admin@inspirehep.net', password='123456'):
        """Perform a local log-in in Inspire storing the session"""
        login_data = {
            'csrf_token': '',
            'email': user,
            'password': password,
        }
        page = self._client.get(self.LOCAL_LOGIN_URL)
        try:
            page.raise_for_status()
            csrf_token = re.search(
                '(?<=name="csrf_token" type="hidden" value=")[^"]*',
                page.text
            ).group()
        except Exception as e:
            raise Exception(
                "Exception: %s\n %s" % (
                    e, self._client.response_to_string(page)
                )
            )
        login_data['csrf_token'] = csrf_token
        response = self._client.post(
            self.LOCAL_LOGIN_URL,
            data=login_data,
            allow_redirects=False
        )
        return response

    def __repr__(self):
        return "{}(auto_login={}, base_url='{}')".format(
            self.__class__.__name__,
            self.auto_login,
            self._client._base_url
        )

    def __str__(self):
        return repr(self)
