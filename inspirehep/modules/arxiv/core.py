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

"""ArXiv Core."""

from __future__ import absolute_import, division, print_function

import requests
from flask import current_app
from lxml.etree import fromstring

from .utils import etree_to_dict


def get_response(arxiv_id):
    response = requests.get(
        current_app.config['ARXIV_API_URL'],
        params=dict(
            verb='GetRecord',
            metadataPrefix='arXiv',
            identifier='oai:arXiv.org:{term}'.format(
                term=arxiv_id.strip()),
        ),
    )
    return response


def get_json(arxiv_id):
    response = get_response(arxiv_id)
    data = etree_to_dict(fromstring(response.content))
    query = {}

    for d in data['OAI-PMH']:
        query.update(dict(d.items()))
    del data['OAI-PMH']

    if 'error' in query:
        if query['error'].startswith('Malformed'):
            query = {}
            data['status'] = 'malformed'
        elif 'versions' in query['error']:
            query = {}
            data['status'] = 'unsupported_versioning'
        else:
            query = {}
            data['status'] = 'notfound'
    else:
        for d in query['GetRecord'][0][
                'record'][1]['metadata'][0]['arXiv']:
            query.update(dict(d.items()))
        del query['GetRecord']
        data['status'] = 'success'

    data['source'] = 'arxiv'
    data['query'] = query

    return data
