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

import hashlib
import re

from itertools import chain
from elasticsearch_dsl import Q
from flask import current_app
from six.moves.urllib.parse import urljoin
from StringIO import StringIO
from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import JSONB

from invenio_db import db
from invenio_oauthclient.models import (
    UserIdentity,
    RemoteAccount,
    RemoteToken,
)
from invenio_oauthclient.utils import oauth_link_external_id
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadata

from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.logging import getStackTraceLogger
from inspire_utils.record import get_values_for_schema
from inspire_utils.urls import ensure_scheme
from inspirehep.modules.search.api import LiteratureSearch
from inspirehep.utils.record_getter import get_db_records

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
    if not api_endpoint.endswith('/'):
        api_endpoint = api_endpoint + '/'

    api_url = urljoin(ensure_scheme(server_name), api_endpoint)
    return urljoin(api_url, recid)


def get_orcid_recid_key(orcid, rec_id):
    """Return the string 'orcidcache:``orcid_value``:``rec_id``'"""
    return 'orcidcache:{}:{}'.format(orcid, rec_id)


def _get_account_and_token(orcid):
    account_token_join = db.session.query(RemoteAccount, RemoteToken).join("remote_tokens")
    account_token_user_join = account_token_join.join(UserIdentity, UserIdentity.id_user == RemoteAccount.user_id)
    account, remote_token = account_token_user_join.filter(UserIdentity.id == orcid).one()

    return account, remote_token


def get_push_access_tokens(orcids):
    remote_accounts = db.session.query(RemoteAccount)\
        .filter(RemoteAccount.user_id == UserIdentity.id_user)\
        .filter(UserIdentity.id.in_(orcids)).all()

    remote_tokens = []
    for remote_account in remote_accounts:
        if remote_account.extra_data.get('allow_push', False):
            remote_tokens.extend(remote_account.remote_tokens)

    return remote_tokens


def account_setup(remote, token, resp):
    """Perform additional setup after user have been logged in.

    This is a modified version of
    :ref:`invenio_oauthclient.contrib.orcid.account_setup` that stores
    additional metadata.

    :param remote: The remote application.
    :param token: The token value.
    :param resp: The response.
    """
    with db.session.begin_nested():
        # Retrieve ORCID from response.
        orcid = resp.get('orcid')
        full_name = resp.get('name')

        # Set ORCID in extra_data.
        token.remote_account.extra_data = {
            'orcid': orcid,
            'full_name': full_name,
            'allow_push': current_app.config.get('ORCID_ALLOW_PUSH_DEFAULT', False)
        }

        user = token.remote_account.user

        # Create user <-> external id link.
        oauth_link_external_id(user, {'id': orcid, 'method': 'orcid'})


def get_orcids_for_push(record):
    """Obtain the ORCIDs associated to the list of authors in the Literature record.

    The ORCIDs are looked up both in the ``ids`` of the ``authors`` and in the
    Author records that have claimed the paper.

    Args:
        record(dict): metadata from a Literature record

    Returns:
        Iterator[str]: all ORCIDs associated to these authors
    """
    orcids_on_record = []
    author_recids_with_claims = []

    for author in record.get('authors', []):
        orcids_in_author = get_values_for_schema(author.get('ids', []), 'ORCID')
        if orcids_in_author:
            orcids_on_record.extend(orcids_in_author)
        elif author.get('curated_relation') is True and 'record' in author:
            author_recids_with_claims.append(get_recid_from_ref(author['record']))

    author_records = get_db_records('aut', author_recids_with_claims)
    all_ids = (author.get('ids', []) for author in author_records)
    orcids_in_authors = chain.from_iterable(get_values_for_schema(ids, 'ORCID') for ids in all_ids)

    return chain(orcids_on_record, orcids_in_authors)


def hash_xml_element(element):
    """Compute a hash for XML element comparison.

    Args:
        element (lxml.etree._Element): the XML node

    Return:
        string: hash
    """
    canonical_string = canonicalize_xml_element(element)
    hash = hashlib.sha1(canonical_string)
    return 'sha1:' + hash.hexdigest()


def canonicalize_xml_element(element):
    """Return a string with a canonical representation of the element.

    Args:
        element (lxml.etree._Element): the XML node

    Return:
        string: canonical representation
    """
    element_tree = element.getroottree()
    output_stream = StringIO()
    element_tree.write_c14n(
        output_stream,
        with_comments=False,
        exclusive=True,
    )
    return output_stream.getvalue()


def get_literature_recids_for_orcid(orcid):
    """Return the Literature recids that were claimed by an ORCiD.

    We record the fact that the Author record X has claimed the Literature
    record Y by storing in Y an author object with a ``$ref`` pointing to X
    and the key ``curated_relation`` set to ``True``. Therefore this method
    first searches the DB for the Author records for the one containing the
    given ORCiD, and then uses its recid to search in ES for the Literature
    records that satisfy the above property.

    Args:
        orcid (str): the ORCiD.

    Return:
        list(int): the recids of the Literature records that were claimed
        by that ORCiD.

    """
    orcid_object = '[{"schema": "ORCID", "value": "%s"}]' % orcid
    # this first query is written in a way that can use the index on (json -> ids)
    author_rec_uuid = db.session.query(RecordMetadata.id)\
        .filter(type_coerce(RecordMetadata.json, JSONB)['ids'].contains(orcid_object)).one().id
    author_recid = db.session.query(PersistentIdentifier.pid_value).filter(
        PersistentIdentifier.object_type == 'rec',
        PersistentIdentifier.object_uuid == author_rec_uuid,
        PersistentIdentifier.pid_type == 'aut',
    ).one().pid_value

    query = Q('match', authors__curated_relation=True) & Q('match', authors__recid=author_recid)
    search_by_curated_author = LiteratureSearch().query('nested', path='authors', query=query)\
                                                 .params(_source=['control_number'], size=9999)

    return [el['control_number'] for el in search_by_curated_author]
