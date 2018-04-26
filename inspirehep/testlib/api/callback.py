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

"""/callback endpoint api client and resources."""

from __future__ import absolute_import, division, print_function

import json


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
    """Client for the Inspire callback"""
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
            self.CALLBACK_URL,
            'robotupload',
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
            self.CALLBACK_URL,
            'webcoll',
            data=data,
            headers={'Content-type': 'application/x-www-form-urlencoded'}
        )
        return response
