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

import logging
import re

from flask import current_app
from invenio_oauthclient.models import (
    RemoteAccount,
    RemoteToken,
    User,
    UserIdentity,
)
from itertools import chain
from orcid import MemberAPI
from sqlalchemy.orm.exc import NoResultFound

from .converter import OrcidConverter
from .models import InspireOrcidPutCodes
from inspire_utils.record import get_value
from inspirehep.modules.records.json_ref_loader import replace_refs


LOGGER = logging.getLogger(__name__)


RECID_FROM_INSPIRE_URL = re.compile(
    r"https?://(?:labs\.)?inspirehep\.net/(?:record|literature)/(\d+)",
    re.IGNORECASE
)


def push_record_to_all(record):
    """Push record to all authorized associated ORCIDS.

    Args:
        record (dict): HEP record to be pushed
    """
    associated_orcids = _get_author_orcids_for_record(record)
    for orcid in associated_orcids:
        try:
            push_record_with_orcid(record, orcid)
        except NoResultFound:
            LOGGER.info(
                'No OAUTH token for {}, can\'t push #{}.'.format(
                    orcid, record['control_number']
                )
            )


def push_record_with_orcid(record, orcid):
    """Push record to ORCID with a specific ORCID ID.

    Args:
        record (dict): HEP record to push
        orcid (string): ORCID identifier to push onto
    """
    recid = record['control_number']
    client_key = current_app.config['ORCID_APP_CREDENTIALS']['consumer_key']
    client_secret = current_app.config['ORCID_APP_CREDENTIALS']['consumer_secret']
    oauth_token = _oauth_token_for_orcid(orcid)

    orcid_api = MemberAPI(client_key, client_secret)

    put_code = _find_put_code_for_record_in_orcid(record, orcid, oauth_token, orcid_api)
    orcid_xml = OrcidConverter(record, put_code).get_xml()

    if put_code:
        LOGGER.info("Pushing record #{} with put-code {}.".format(
            recid,
            put_code
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
        LOGGER.info("No put-code found, pushing new record #{}.".format(recid))
        inserted_put_code = orcid_api.add_record(
            orcid_id=orcid,
            token=oauth_token,
            request_type='work',
            data=orcid_xml,
            content_type='application/orcid+xml',
        )

        InspireOrcidPutCodes.set_put_code(recid=recid, put_code=inserted_put_code)

        LOGGER.info("Record added with put-code {}.".format(inserted_put_code))


def _get_put_code(work):
    """Return a put-code for ORCID work entry.

    Args:
        work (lxml.etree._Element): work entry

    Returns:
        string: the put code
    """
    return _ns_xpath(work, './work:work-summary/@put-code')[0]


def _find_put_code_for_record_in_orcid(record, orcid, oauth_token, api):
    """Determines the put code (if possible) for the HEP record and ORCID.

    Args:
        record (dict): HEP record we want the put code for
        orcid (string): ORCID identifier to search in
        oauth_token (string): OAUTH token associated with `orcid`
        api (MemberAPI): API to be used for search

    Returns:
        Union[string, NoneType]: put code or None if not found
    """
    stored_code = InspireOrcidPutCodes.get_put_code(record['control_number'])
    if stored_code:
        return stored_code

    user_works = api.read_record_member(
        orcid, 'works', oauth_token, accept_type='application/orcid+xml'
    )
    for work in _ns_xpath(user_works, '/activities:works/activities:group'):
        if _hep_orcid_records_matching(record, work, orcid, oauth_token, api)\
                and _was_record_pushed_by_inspire(work):
            return _get_put_code(work)


def _oauth_token_for_orcid(orcid):
    """Given an ORCID will try to find corresponding OAUTH token.

    Args:
        orcid (string): ORCID identifier

    Returns:
        Union[string, NoneType]: OAUTH token connected to the `orcid` account
    """
    token_accounts = RemoteToken.query.join(RemoteAccount)
    token_identities = token_accounts.join(User).join(UserIdentity)
    token_row = token_identities.filter(UserIdentity.id == orcid).one()
    return token_row.access_token


def _hep_orcid_records_matching(hep, work, orcid, oauth_token, api):
    """Match an HEP record against ORCID work record.

    The matching steps:
    1) are any UIDs shared?
    2) is there a matching reference to INSPIRE (inspirehep.net url)
    3) is there a match of (title, journal, date)

    Args:
        hep (dict): record in INSPIRE
        work (lxml.etree._Element): activities:group node, record in ORCID
        orcid (string): ORCID identifier to search in
        oauth_token (string): OAUTH token associated with `orcid`
        api (MemberAPI): API to be used for search

    Returns:
        bool: are the records representing the same piece of work?
    """
    hep_ids = set(
        get_value(hep, 'dois.value', [])
        + get_value(hep, 'arxiv_eprints.value', [])
    )
    orcid_ids = set(_ns_xpath(
        work,
        './common:external-ids/common:external-id'
        '[common:external-id-type="doi" or common:external-id-type="arxiv"]'
        '[common:external-id-relationship="self"]'
        '/common:external-id-value/text()',
    ))

    if orcid_ids & hep_ids != set():
        # If external identifiers overlap, then we can assume records are
        # referring to the same piece of work:
        return True

    # If no common identifiers were found we need to look at other identifiers
    # to a record in INSPIRE, for that we fetch the full work record from ORCID
    work_entry = api.read_record_member(
        orcid_id=orcid,
        request_type='work',
        token=oauth_token,
        put_code=_get_put_code(work),
        accept_type='application/orcid+xml'
    )
    url_on_orcid = _ns_xpath(work_entry, '/work:work/work:url/text()', 0)

    if url_on_orcid and _recid_from_url(url_on_orcid) == hep['control_number']:
        return True

    # If above fails compare title, journal and date
    if _orcid_hep_publication_info_matching(work_entry, hep):
        return True

    # No identifiers are shared, give up
    return False


def _was_record_pushed_by_inspire(work):
    """Determine if a record was pushed by INSPIRE before.

    Args:
        work (lxml.etree._Element): activities:group node (work)

    Returns:
        bool: True if record was pushed by INSPIRE, False otherwise
    """
    client_id = current_app.config['ORCID_APP_CREDENTIALS']['consumer_key']
    return client_id in _ns_xpath(
        work,
        './work:work-summary/common:source/common:source-client-id/'
        'common:path/text()',
    )


def _recid_from_url(url):
    """Determines if a url point to an INSPIRE record and returns its recid.

    Args:
        url (string): a url

    Returns:
        Union[int, NoneType]: recid extracted from the url, or None
    """
    match = RECID_FROM_INSPIRE_URL.match(url)
    if match:
        return int(match.group(1))


def _ns_xpath(node, xpath, index=None):
    """Run an XPath expression on a node, and automatically add namespaces.

    Args:
        node (lxml.etree._Element): a node
        xpath (string): an XPath expression
        index (int): get a particular item from list, or None otherwise

    Returns:
        any: result of running `xpath` on `node`
    """
    results = node.xpath(xpath, namespaces=node.nsmap)
    if index is None:
        return results
    else:
        return results[index] if index < len(results) else None


def _orcid_hep_publication_info_matching(work_entry, hep):
    """Check if HEP and ORCID records have matching publication info.

    Args:
        work_entry (lxml.etree._Element): a work:work node
        hep (dict): a HEP record

    Returns:
        bool: if publication information are matching
    """
    title_on_orcid = _ns_xpath(
        work_entry, '/work:work/work:title/common:title/text()', 0
    )
    journal_on_orcid = _ns_xpath(
        work_entry, '/work:work/work:journal-title/text()', 0
    )
    year_on_orcid = _ns_xpath(
        work_entry, '/work:work/common:publication-date/common:year/text()', 0
    )

    if title_on_orcid not in get_value(hep, 'titles.title', []):
        return False

    for pub_info in hep.get('publication_info', []):
        title = pub_info.get('journal_title')
        year = pub_info.get('year')
        if title == journal_on_orcid and year == int(year_on_orcid):
            return True

    return False


def _get_author_orcids_for_record(record):
    """List all of the known author ORCIDs of a record.

    Args:
        record (dict): HEP record

    Returns:
        Iterable[string]: ORCIDs of authors
    """
    authors_with_refs = {'authors': replace_refs(record.get('authors'))}
    return (
        uid['value'] for uid
        in chain(*get_value(authors_with_refs, 'authors.record.ids', []))
        if uid['schema'] == 'ORCID'
    )
