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

"""APIs for ORCID."""

from __future__ import absolute_import, division, print_function

import requests

from itertools import chain
from flask import current_app as app
from orcid import MemberAPI

from inspire_utils.record import get_value
from inspirehep.modules.orcid import OrcidConverter
from inspirehep.modules.orcid.utils import (
    LOGGER,
    _get_api_url_for_recid,
    _split_lists,
    WORKS_BULK_QUERY_LIMIT,
    RECID_FROM_INSPIRE_URL,
)


def push_record_with_orcid(recid, orcid, oauth_token, put_code=None):
    """Push record to ORCID with a specific ORCID ID.

    Args:
        recid (string): HEP record to push
        orcid (string): ORCID identifier to push onto
        oauth_token (string): ORCID user OAUTH token
        put_code (Union[string, NoneType]): put-code to push record onto,
            if None will push as a new record

    Returns:
        string: the put-code of the inserted item
    """
    record = _get_hep_record(app.config, recid)

    try:
        bibtex = _get_bibtex_record(app.config, recid)
    except requests.RequestException:
        bibtex = None
        LOGGER.error('Pushing record #{} without BibTex, as fetching'
                     'it failed!'.format(recid))

    orcid_api = _get_api()

    orcid_xml = OrcidConverter(
        record, app.config['LEGACY_RECORD_URL_PATTERN'], put_code=put_code, bibtex_citation=bibtex
    ).get_xml()

    if put_code:
        LOGGER.info("Pushing record #{} with put-code {} to ORCID {}.".format(
            recid,
            put_code,
            orcid
        ))
        orcid_api.update_record(
            orcid_id=orcid,
            token=oauth_token,
            request_type='work',
            data=orcid_xml,
            put_code=put_code,
            content_type='application/orcid+xml',
        )
    else:
        LOGGER.info(
            "No put-code found, pushing new record #{} to ORCID {}.".format(
                recid,
                orcid,
            )
        )
        put_code = orcid_api.add_record(
            orcid_id=orcid,
            token=oauth_token,
            request_type='work',
            data=orcid_xml,
            content_type='application/orcid+xml',
        )

        LOGGER.info("Record added with put-code {}.".format(put_code))

    return put_code


def _get_record_by_mime(config, recid, mime_type):
    """

    Args:
        config (inspire_utils.config.Config): configuration
        recid (string): HEP record ID
        mime_type (string): accept type

    Returns:
        requests.Response: response form API
    """
    server_name = config['SERVER_NAME']

    record_api_endpoint = _get_api_url_for_recid(
        server_name, config['SEARCH_UI_SEARCH_API'], recid
    )

    response = requests.get(record_api_endpoint, headers={
        'Accept': mime_type
    })
    response.raise_for_status()
    return response


def _get_hep_record(config, recid):
    """

    Args:
        config (inspire_utils.config.Config): configuration
        recid (string): HEP record ID

    Returns:
        dict: HEP record
    """
    hep_response = _get_record_by_mime(config, recid, 'application/json')
    return hep_response.json()['metadata']


def _get_bibtex_record(config, recid):
    """

    Args:
        config (inspire_utils.config.Config): configuration
        recid (string): HEP record ID

    Returns:
        string: BibTeX serialized record
    """
    bibtex_response = _get_record_by_mime(config, recid, 'application/x-bibtex')
    return bibtex_response.text


def get_author_putcodes(orcid, oauth_token):
    """Get put-codes for author works pushed by INSPIRE.

    Args:
        orcid (string): author's ORCID
        oauth_token (string): author's OAUTH token

    Returns:
        List[Tuple[string, string]]: list of tuples of the form
            (recid, put_code) with results.
    """
    api = _get_api()
    # This reads the record _summary_ (no URLs attached):
    user_works = api.read_record_member(
        orcid,
        'works',
        oauth_token,
        accept_type='application/orcid+json',
    )

    put_codes = []
    for summary in chain(*get_value(user_works, 'group.work-summary', [])):
        source_client_id_dict = get_value(summary, 'source.source-client-id')
        put_code = summary.get('put-code')

        # Filter out records that are not ours and those with no put-code (unlikely)
        if source_client_id_dict and put_code:
            if source_client_id_dict.get('path') == app.config['ORCID_APP_CREDENTIALS']['consumer_key']:
                put_codes.append(str(put_code))

    # We can batch requests for _detailed_ records for maximum
    # `WORKS_BULK_QUERY_LIMIT` put-codes at once:
    detailed_works = []

    for put_code_batch in _split_lists(put_codes, WORKS_BULK_QUERY_LIMIT):
        batch = api.read_record_member(
            orcid,
            'works',
            oauth_token,
            accept_type='application/orcid+json',
            put_code=put_code_batch,
        )

        detailed_works.extend(batch['bulk'])

    # Now that we have all of the detailed records, we extract recids.
    # If it's not possible (and it should always be), we put the put-code in
    # `errors`
    author_putcodes = []
    errors = []

    for item in detailed_works:
        put_code = get_value(item, 'work.put-code')
        if not put_code:
            continue

        try:
            url = get_value(item, 'work.url.value')
            match = RECID_FROM_INSPIRE_URL.match(url)
            recid = match.group(1)
        except (TypeError, AttributeError):
            errors.append(str(put_code))
            continue

        author_putcodes.append(
            (recid, str(put_code))
        )

    if errors:
        LOGGER.error(
            'Failed to match putcodes {} from {} to HEP records.'.format(
                ', '.join(errors), orcid
            )
        )

    return author_putcodes


def _get_api():
    """Get ORCID API.

    Returns:
        MemberAPI: ORCID API
    """
    client_key = app.config['ORCID_APP_CREDENTIALS']['consumer_key']
    client_secret = app.config['ORCID_APP_CREDENTIALS']['consumer_secret']
    sandbox = app.config['ORCID_SANDBOX']
    return MemberAPI(client_key, client_secret, sandbox)
