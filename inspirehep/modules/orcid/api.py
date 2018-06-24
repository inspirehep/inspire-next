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

from itertools import chain
from flask import current_app as app
from orcid import MemberAPI

from inspire_utils.logging import getStackTraceLogger
from inspire_utils.record import get_value
from inspirehep.utils.lock import distributed_lock
from inspirehep.modules.orcid import OrcidConverter
from inspirehep.modules.orcid.utils import (
    _split_lists,
    WORKS_BULK_QUERY_LIMIT,
    RECID_FROM_INSPIRE_URL,
    log_time_context,
)
from inspirehep.modules.records.serializers import bibtex_v1
from inspirehep.utils.record_getter import get_db_record

from .cache import OrcidCache, OrcidHasher
from .exceptions import (
    DuplicatedExternalIdentifiersError,
    EmptyPutcodeError,
    PutcodeNotFoundInCacheException,
)
from .utils import log_time


LOGGER = getStackTraceLogger(__name__)


def push_record_with_orcid(recid, orcid, oauth_token, putcode=None, old_hash=None):
    """Push record to ORCID with a specific ORCID ID.

    Args:
        recid (string): HEP record to push
        orcid (string): ORCID identifier to push onto
        oauth_token (string): ORCID user OAUTH token
        putcode (Union[string, NoneType]): put-code to push record onto,
            if None will push as a new record
        old_hash (Optional[string]): previous hash of the record

    Returns:
        Tuple[string, string]: a tuple with two elements:
            - the put-code of the inserted item,
            - and the new hash of the ORCID record
    """
    record = get_db_record('lit', recid)

    orcid_cache = OrcidCache(orcid)

    if not putcode or not old_hash:
        cached_putcode, cached_old_hash = orcid_cache.read_record_data(recid)
        putcode = putcode or cached_putcode
        old_hash = old_hash or cached_old_hash

    new_hash = OrcidHasher().compute_hash(record)
    if new_hash == old_hash:
        LOGGER.info(
            'Hash unchanged: not pushing #%s as not a meaningful update', recid
        )
        return putcode, new_hash

    try:
        bibtex = bibtex_v1.serialize(recid, record)
    except Exception:
        bibtex = None
        LOGGER.error(
            'Pushing record #%s without BibTex, as fetching it failed!', recid
        )

    orcid_api = _get_api()

    orcid_xml = OrcidConverter(
        record, app.config['LEGACY_RECORD_URL_PATTERN'], put_code=putcode, bibtex_citation=bibtex
    ).get_xml()

    lock_name = 'orcid:{}'.format(orcid)

    # It's an update: PUT.
    if putcode:
        LOGGER.info(
            "Pushing record #%s with put-code %s onto %s.", recid, putcode, orcid,
        )
        with log_time_context('Pushing updated record', LOGGER), \
                distributed_lock(lock_name, blocking=True):
            orcid_api.update_record(
                orcid_id=orcid,
                token=oauth_token,
                request_type='work',
                data=orcid_xml,
                put_code=putcode,
                content_type='application/orcid+xml',
            )

    # It's a new record: POST.
    else:
        LOGGER.info(
            "No put-code found, pushing new record #%s to ORCID %s.", recid, orcid,
        )

        try:
            with log_time_context('Pushing new record', LOGGER), \
                    distributed_lock(lock_name, blocking=True):
                putcode = orcid_api.add_record(
                    orcid_id=orcid,
                    token=oauth_token,
                    request_type='work',
                    data=orcid_xml,
                    content_type='application/orcid+xml',
                )
        except Exception as exc:
            if DuplicatedExternalIdentifiersError.match(exc):
                recache_author_putcodes(orcid, oauth_token)
                putcode, previous_hash = orcid_cache.read_record_data(recid)
                if not putcode:
                    raise PutcodeNotFoundInCacheException(
                        'Putcode not found in cache for recid {} after having'
                        ' recached all putcodes for the orcid {}'.format(recid, orcid))
                return push_record_with_orcid(recid, orcid, oauth_token, putcode, previous_hash)
            else:
                raise exc
        if not putcode:
            raise EmptyPutcodeError

    LOGGER.info("Push of %s onto %s completed with put-code %s.", recid, orcid, putcode)

    orcid_cache.write_record_data(recid, putcode, new_hash)
    return putcode, new_hash


@log_time(LOGGER)
def recache_author_putcodes(orcid, oauth_token):
    """Fetch all putcodes from ORCID and cache them.

    Args:
        orcid(string): an orcid identifier.
        oauth_token(string): orcid token.
    """
    record_putcodes = get_author_putcodes(orcid, oauth_token)
    cache = OrcidCache(orcid)
    for fetched_recid, fetched_putcode in record_putcodes:
        cache.write_record_data(fetched_recid, fetched_putcode, None)


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
    return MemberAPI(client_key, client_secret, sandbox, timeout=30)
