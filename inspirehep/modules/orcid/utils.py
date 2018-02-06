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

from orcid import MemberAPI

from inspire_utils.record import get_value
from inspire_utils.config import load_config


RECID_FROM_INSPIRE_URL = re.compile(
    r"https?://(?:labs\.)?inspirehep\.net/(?:record|literature)/(\d+)",
    re.IGNORECASE
)

WORKS_BULK_QUERY_LIMIT = 50

CONFIG = load_config()


def get_author_putcodes(orcid, oauth_token):
    """Get put-codes for author works pushed by INSPIRE.

    Args:
        orcid (string): author's ORCID
        oauth_token (string): author's OAUTH token

    Returns:
        Tuple[
            List[Tuple[string, string]],
            List[string]
        ]: list of tuples of the form (recid, put_code) with results,
            and another list of put-codes for which we failed to obtain
            the recids (should never happen)
    """
    api = _get_api()
    # This reads the record _summary_ (no URLs attached):
    user_works = api.read_record_member(
        orcid,
        'works',
        oauth_token,
        accept_type='application/orcid+json',
    )

    put_codes = [
        str(item[0]) for item
        in get_value(user_works, 'group.work-summary.put-code')
    ]

    # We can batch requests for _detailed_ records for maximum
    # `WORKS_BULK_QUERY_LIMIT` put-codes at once:
    detailed_works = {'bulk': []}

    for put_code_batch in _split_lists(put_codes, WORKS_BULK_QUERY_LIMIT):
        batch = api.read_record_member(
            orcid,
            'works',
            oauth_token,
            accept_type='application/orcid+json',
            put_code=put_code_batch,
        )

        detailed_works['bulk'].extend(batch['bulk'])

    # Now that we have all of the detailed records, we extract recids.
    # If it's not possible (and it should always be), we put the put-code in
    # `errors`
    author_putcodes = []
    errors = []

    for item in detailed_works['bulk']:
        put_code = get_value(item, 'work.put-code')
        if not put_code:
            continue

        try:
            url = get_value(item, 'work.url.value')
            match = RECID_FROM_INSPIRE_URL.match(url)
            recid = match.group(1)
        except (TypeError, AttributeError):
            errors.append(put_code)
            continue

        if put_code:
            author_putcodes.append(
                (recid, put_code)
            )

    return author_putcodes, errors


def _get_api():
    """Get ORCID API.

    Returns:
        MemberAPI: ORCID API
    """
    client_key = CONFIG['ORCID_APP_CREDENTIALS']['consumer_key']
    client_secret = CONFIG['ORCID_APP_CREDENTIALS']['consumer_secret']
    return MemberAPI(client_key, client_secret)


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
