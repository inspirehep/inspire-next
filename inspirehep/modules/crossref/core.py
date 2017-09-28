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

"""Crossref core."""

from __future__ import absolute_import, division, print_function

import requests
from flask import current_app
from six.moves.urllib.parse import urljoin


def get_response(crossref_doi):
    response = requests.get(
        urljoin(
            current_app.config['CROSSREF_API_URL'],
            '{term}'.format(term=crossref_doi),
        ),
    )
    return response


def get_json(doi):
    response = get_response(doi)
    data, query = {}, {}

    if response.status_code == 200:
        if 'message' in response.json():
            query = response.json().get('message')
        else:
            query = response.json()
        data['status'] = 'success'
    elif response.status_code == 404:
        data['status'] = 'notfound'

    data['source'] = 'crossref'
    data['query'] = query

    return data
