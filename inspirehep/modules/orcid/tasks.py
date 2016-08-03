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

from celery import shared_task
from celery.utils.log import get_task_logger

from flask import current_app

from invenio_db import db

from invenio_oauthclient.models import RemoteAccount, RemoteToken, UserIdentity

from invenio_pidstore.resolver import Resolver

from invenio_search import current_search_client
from invenio_search.utils import schema_to_index

from requests import RequestException

from .models import InspireOrcidRecords
from .utils import convert_to_orcid, get_authors_credentials

logger = get_task_logger(__name__)


def prepare_authors_data_for_pushing_to_orcid(json):
    """ Extracts the authors with valid orcid credentials from the list of authors
    of a given record in json format.
    """
    resolver = Resolver(pid_type='literature',
                        object_type='rec', getter=lambda x: x)
    record_id = resolver.resolve(json.get('control_number'))[
        0].object_uuid
    authors = get_orcid_valid_authors(json)
    token = None
    author_orcid = ''
    authors_with_orcid_credentials = []
    for author in authors:
        try:
            token, author_orcid = get_authors_credentials(author['_source'])
        except AttributeError:
            continue
        try:
            authors_with_orcid_credentials.append((InspireOrcidRecords.query.filter_by(
                orcid=author_orcid, record_id=record_id).first().put_code, token, author_orcid, record_id))
        except AttributeError:
            authors_with_orcid_credentials.append(
                ([], token, author_orcid, record_id))
            continue
    return authors_with_orcid_credentials


@shared_task(ignore_result=True)
def delete_from_orcid(sender, api=None):
    """ Deletes a record from orcid.
    """
    if not api:
        api = current_app.extensions['inspire-orcid'].orcid_api

    resolver = Resolver(pid_type='literature',
                        object_type='rec', getter=lambda x: x)
    record_id = resolver.resolve(sender.get('control_number'))[
        0].object_uuid
    records = InspireOrcidRecords.query.filter_by(record_id=record_id).all()
    for record in records:
        raw_user = UserIdentity.query.filter_by(
            id=record.orcid, method='orcid').first()
        remote_user = RemoteAccount.query.filter_by(user_id=raw_user.id_user).first()
        token = RemoteToken.query.filter_by(
            id_remote_account=remote_user.id).first().access_token
        api.remove_record(record.orcid, token, 'work', record.put_code)
        with db.session.begin_nested():
            db.session.delete(record)
        db.session.commit()


def doc_type_should_be_sent_to_orcid(record):
    index, doc_type = schema_to_index(record['$schema'])
    return doc_type == 'hep'


@shared_task(ignore_result=True)
def send_to_orcid(sender, api=None):
    """Sends records to orcid."""
    if doc_type_should_be_sent_to_orcid(sender):
        logger.info("Sending to orcid: ", sender.get('control_number'))
        try:
            if not api:
                api = current_app.extensions['inspire-orcid'].orcid_api
            orcid_json = convert_to_orcid(sender)
            authors = prepare_authors_data_for_pushing_to_orcid(sender)
            for put_code, token, author_orcid, record_id in authors:
                try:
                    if not put_code:
                        put_code = api.add_record(  # try-continue
                            author_orcid, token, 'work', orcid_json)
                        orcid_log_record = InspireOrcidRecords(
                            orcid=author_orcid,
                            record_id=record_id,
                            put_code=put_code)
                        with db.session.begin_nested():
                            db.session.add(orcid_log_record)
                        db.session.commit()
                    else:
                        api.update_record(author_orcid, token,
                                          'work', orcid_json, str(put_code))
                    logger.info("Successfully sent to orcid: ",
                                sender.get('control_number'))
                except RequestException as e:
                    print(e.response.text, sender['control_number'])
                    logger.error("Failed to push to orcid: ",
                                 sender.get('control_number'))
                    continue
        except (KeyError, AttributeError, TypeError) as e:
            logger.warning("Failed to convert: ", sender.get('control_number'))


def get_author_collection_records_from_valid_authors(authors_refs):
    """ Queries elasticsearch for the author-records of the given authors references.
    """
    es_query = {
        "filter": {
            "bool": {
                "must": [
                    {"terms": {
                        "self.$ref": authors_refs
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
    return authors


def get_orcid_valid_authors(record):
    """ Returns all the valid author-records from a hep-record.
    A valid author-rerord is one that contains an orcid id.
    """
    authors_refs = []
    for author in record['authors']:
        try:
            authors_refs.append(author['record']['$ref'])
        except KeyError:
            continue

    return get_author_collection_records_from_valid_authors(authors_refs)
