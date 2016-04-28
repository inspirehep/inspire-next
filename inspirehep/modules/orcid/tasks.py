# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import os

import sys

from celery import shared_task

from flask import current_app

from invenio_db import db

from invenio_oauthclient.models import RemoteAccount, UserIdentity

from invenio_search import current_search_client
from invenio_search.utils import schema_to_index

from requests import RequestException

from .models import InspireOrcidRecords
from .utils import convert_to_orcid


@shared_task(ignore_result=True)
def send_to_orcid(sender, *args, **kwargs):
    """Sends records to orcid."""
    index, doc_type = schema_to_index(sender['$schema'])
    if doc_type == 'hep':
        try:
            api = current_app.extensions['inspire-orcid'].orcid_api
            orcid_json = convert_to_orcid(sender)
            try:
                authors = get_orcid_valid_authors(sender)
                for author in authors:
                    token, author_orcid = get_authors_credentials(author)
                    if not InspireOrcidRecords.query.filter_by(orcid=author_orcid, record_id=int(sender.get('control_number'))).all():
                        put_code = api.add_record(
                            author_orcid, token, 'work', orcid_json)
                        x = InspireOrcidRecords(
                            orcid=author_orcid,
                            record_id=sender.get('control_number'),
                            put_code=put_code)
                        with db.session.begin_nested():
                            db.session.add(x)
                    else:
                        put_code = InspireOrcidRecords.query.filter_by(
                            orcid=author_orcid, record_id=int(
                                sender.get('control_number'))).first().put_code
                        api.update_record(author_orcid, token,
                                          'work', orcid_json, str(put_code))
            except RequestException as e:
                print(e.response.text)
                print sender['control_number']
        except (KeyError, AttributeError) as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


def get_authors_credentials(author):
    """Returns the orcid-id and the orcid-token for a specific author (if available)."""
    author_orcid = ''
    author = author['_source']
    for orcid_id in author['ids']:
        if orcid_id['type'] == 'ORCID':
            author_orcid = orcid_id['value']
    raw_user = UserIdentity.query.filter_by(
        id=author_orcid, method='orcid').first()
    user = RemoteAccount.query.get(raw_user.id_user)
    token = user.tokens[0].access_token
    return (token, author_orcid)


def get_orcid_valid_authors(sender):
    """ Returns all the valid author-records from a hep-record.
    A valid author-rerord is one that has 'curated_relation' = True
    and contains an orcid id.
    """
    valid_authors = []
    authors = sender['authors']
    for author in authors:
        if author['curated_relation']:
            valid_authors.append(author['record']['$ref'])
    es_query = {
        "filter": {
            "bool": {
                "must": [
                    {"terms": {
                        "self.$ref": valid_authors
                    }}, {"match": {
                        "ids.type": "ORCID"
                    }}
                ]
            }
        }
    }
    authors = current_search_client.search(
        index='records-authors',
        doc_type='authors',
        body=es_query
    )['hits']['hits']
    if authors:
        return authors
    else:
        return []
