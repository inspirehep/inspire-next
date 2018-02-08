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

"""ORCID utils."""

from __future__ import absolute_import, division, print_function

import re
from urlparse import urljoin

from inspire_utils.logging import getStackTraceLogger

from inspirehep.modules.cache.utils import redis_locking_context, RedisLockError

LOGGER = getStackTraceLogger(__name__)


RECID_FROM_INSPIRE_URL = re.compile(
    r"https?://(?:labs\.)?inspirehep\.net/(?:record|literature)/(\d+)",
    re.IGNORECASE
)

WORKS_BULK_QUERY_LIMIT = 50


def _split_lists(sequence, chunk_size):
    """Get a list created by splitting the original list every n-th element

    Args:
        sequence (List[Any]): a list to be split
        chunk_size (int): how bit one chunk should be (n)

    Returns:
        List[List[Any]]: the split list
    """
    return [
        sequence[i:i + chunk_size] for i in range(0, len(sequence), chunk_size)
    ]


def _get_api_url_for_recid(server_name, api_endpoint, recid):
    """Return API url for record

    Args:
        server_name (string): server authority
        api_endpoint (string): api path
        recid (string): record ID

    Returns:
        string: API URL for the record
    """
    if not re.match('^https?://', server_name):
        server_name = 'http://{}'.format(server_name)

    if not api_endpoint.endswith('/'):
        api_endpoint = api_endpoint + '/'

    api_url = urljoin(server_name, api_endpoint)
    return urljoin(api_url, recid)


def get_orcid_recid_key(orcid, rec_id):
    """Return the string 'orcid:``orcid_value``:``rec_id``'"""
    return 'orcidputcodes:{}:{}'.format(orcid, rec_id)


def store_record_in_redis(orcid, rec_id, put_code):
    """Store the entry <orcid:recid, value> in Redis.

    Args:
        orcid(string): the author's orcid.
        rec_id(int): inspire record's id pushed to ORCID.
        put_code(string): the put_code used to push the record to ORCID.

    Returns:
        bool: True if the entry is set in Redis, False otherwise.
    """
    try:
        with redis_locking_context('orcid_push') as r:
            orcid_recid_key = get_orcid_recid_key(orcid, rec_id)
            r.set(orcid_recid_key, put_code)
            return True

    except RedisLockError:
        LOGGER.info("Push to ORCID failed for record {}".format(rec_id))
        return False


def get_putcode_from_redis(orcid, rec_id):
    """Retrieve from Redis the put_code for the given ORCID - record id"""
    try:
        with redis_locking_context('orcid_push') as r:
            orcid_recid_key = get_orcid_recid_key(orcid, rec_id)
            return r.get(orcid_recid_key)

    except RedisLockError:
        LOGGER.info("Push to ORCID failed for record {}".format(rec_id))
