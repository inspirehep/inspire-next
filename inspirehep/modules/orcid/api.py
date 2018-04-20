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

from inspire_utils.logging import getStackTraceLogger
from inspire_utils.record import get_value
from inspirehep.modules.orcid import OrcidConverter
from inspirehep.modules.orcid.utils import (
    _get_api_url_for_recid,
    _split_lists,
    WORKS_BULK_QUERY_LIMIT,
    RECID_FROM_INSPIRE_URL,
    hash_xml_element,
    log_time_context,
)
from inspirehep.utils.record_getter import get_db_record

LOGGER = getStackTraceLogger(__name__)


def push_record_with_orcid(recid, orcid, oauth_token, put_code=None, old_hash=None):
    """Push record to ORCID with a specific ORCID ID.

    Args:
        recid (string): HEP record to push
        orcid (string): ORCID identifier to push onto
        oauth_token (string): ORCID user OAUTH token
        put_code (Union[string, NoneType]): put-code to push record onto,
            if None will push as a new record
        old_hash (Optional[string]): previous hash of the record

    Returns:
        Tuple[string, string]: a tuple with two elements:
            - the put-code of the inserted item,
            - and the new hash of the ORCID record
    """
    record = get_db_record('lit', recid)

    new_hash = calculate_hash_for_record(record)
    if new_hash == old_hash:
        LOGGER.info(
            'Hash unchanged: not pushing #%s as not a meaningful update', recid
        )
        return put_code, new_hash

    try:
        bibtex = _get_bibtex_record(app.config, recid)
    except requests.RequestException:
        bibtex = None
        LOGGER.error(
            'Pushing record #%s without BibTex, as fetching it failed!', recid
        )

    orcid_api = _get_api()

    orcid_xml = OrcidConverter(
        record, app.config['LEGACY_RECORD_URL_PATTERN'], put_code=put_code, bibtex_citation=bibtex
    ).get_xml()

    if put_code:
        LOGGER.info(
            "Pushing record #%s with put-code %s onto %s.", recid, put_code, orcid,
        )
        with log_time_context('Pushing updated record', LOGGER):
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
            "No put-code found, pushing new record #%s to ORCID %s.", recid, orcid,
        )
        with log_time_context('Pushing new record', LOGGER):
            put_code = orcid_api.add_record(
                orcid_id=orcid,
                token=oauth_token,
                request_type='work',
                data=orcid_xml,
                content_type='application/orcid+xml',
            )

    LOGGER.info("Push of %s onto %s completed with put-code %s.", recid, orcid, put_code)

    return put_code, new_hash


def calculate_hash_for_record(record):
    """Generate hash for an ORCID-serialised HEP record

    Args:
        record (dict): HEP record

    Returns:
        string: hash of the record
    """
    orcid_rec = OrcidConverter(record, app.config['LEGACY_RECORD_URL_PATTERN'])
    return hash_xml_element(orcid_rec.get_xml())


def _get_bibtex_record(config, recid):
    """
    Call Inspire API to get the bibtex for a given record id.

    Args:
        config (inspire_utils.config.Config): configuration
        recid (string): HEP record ID

    Returns:
        string: BibTeX serialized record
    """
    mime_type = 'application/x-bibtex'
    server_name = config['SERVER_NAME']

    record_api_endpoint = _get_api_url_for_recid(
        server_name, config['SEARCH_UI_SEARCH_API'], recid
    )

    with log_time_context(
        'Getting %s #%s record from inspire' % (mime_type, recid),
        LOGGER,
    ):
        response = requests.get(
            record_api_endpoint,
            headers={'Accept': mime_type, },
            timeout=30)
        response.raise_for_status()
        return response.text


def get_author_putcodes(orcid, oauth_token):
    """Get put-codes for author works pushed by INSPIRE.

    Args:
        orcid (string): author's ORCID
        oauth_token (string): author's OAUTH token

    Returns:
        List[Tuple[string, string]]: list of tuples of the form
            (recid, put_code) with results.
    """
    def timed_read_record_member(orcid, request_type, oauth_token, accept_type, put_code=None):
        with log_time_context(
            'Request for %s for %s' % (request_type, orcid),
            LOGGER
        ):
            return api.read_record_member(
                orcid,
                'works',
                oauth_token,
                accept_type=accept_type,
                put_code=put_code,
            )

    api = _get_api()
    # This reads the record _summary_ (no URLs attached):
    user_works = timed_read_record_member(
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
        batch = timed_read_record_member(
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
            'Failed to match putcodes %s from %s to HEP records.',
            ', '.join(errors), orcid
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
