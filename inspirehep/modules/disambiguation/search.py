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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Set of methods to query Elasticsearch instance."""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from dateutil.parser import parse

from elasticsearch.helpers import scan
from flask import current_app

from invenio_search import current_search_client as es


def _get_record(record_id, source):
    """Make a call to the Elasticsearch instance with known record_id.

    :param record_id:
        An identification (UUID) of the given record.

        Example:
            record_id = "a5afb151-8f75-4e91-8dc1-05e7e8e8c0b8"

    :param source:
        A list of fields to be extracted from the Elasticsearch response.

        Example:
            source = ["collaboration", "author.full_name"]
    """
    elasticsearch_index = current_app.config.get('DISAMBIGUATION_RECORD_INDEX')
    elasticsearch_type = current_app.config.get('DISAMBIGUATION_RECORD_TYPE')

    return es.get_source(
        index=elasticsearch_index,
        id=str(record_id),
        doc_type=elasticsearch_type,
        _source=source)


def _search(query):
    """Make a call to the Elasticsearch instance.

    Receives the dictionary as the parameter.
    With the given paremeter, the Elasticsearch instance is being
    queried.

    :query:
        The query for the Elasticsearch instance.

        Example:
            query = {"query": {"match_all": {}}}

    :return:
        The Elasticsearch instance response.
    """
    elasticsearch_index = current_app.config.get('DISAMBIGUATION_RECORD_INDEX')

    return es.search(
        index=elasticsearch_index,
        body=query)['hits']['hits']


def _scroll_search(query):
    """Make a call to the Elasticsearch with a big response.

    Receives the dictionary as the parameter.
    With the given paremeter, the Elasticsearch instance is being
    queried.

    :query:
        The query for the Elasticsearch instance.

        Example:
            query = {"query": {"match_all": {}}}

    :return:
        The Elasticsearch instance response.
    """
    elasticsearch_index = current_app.config.get('DISAMBIGUATION_RECORD_INDEX')
    elasticsearch_type = current_app.config.get('DISAMBIGUATION_RECORD_TYPE')

    result = []

    for response in scan(
            es, query=query,
            index=elasticsearch_index,
            doc_type=elasticsearch_type):
        result.append(response)

    return result


def create_beard_record(record_id):
    """Create a record in the Beard readable format.

    Receives a UUID of the given record as the parameter.
    In order to run Beard, a list of dictionaries, representing records,
    must be supplied. This method allows to create a dictionary
    representing one record.

    :param record_id:
        A UUID of a given record.

        Example:
            record_id = "beb847d1-c7e0-48b2-9f48-a0d5d0586199"

    :return:
        A dictionary representing one record in the Beard readable format.

        Example:
            {'authors': [u'Hohm, Olaf', u'Wang, Yi-Nan'],
             'publication_id': u'13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
             'year': u'2015'}
    """
    _source = [
        "authors.full_name",
        "earliest_date"
    ]

    response = _get_record(record_id, _source)

    # Get the year of the record publication.
    try:
        earliest_date = response.get("earliest_date")
        year = parse(earliest_date).strftime("%Y")
    except:
        year = False

    # Since the authors and publication_id are mandatory,
    # pass if the record is not complete.
    try:
        authors = [author['full_name'] for author in response['authors']]

        record = {
            "authors": authors,
            "publication_id": str(record_id),
            "year": (lambda year: int(year) and year or '')(year)
        }

        return record
    except KeyError:
        pass


def create_beard_signatures(record_id, signature_block):
    """Create a list of signatures in the Beard readable format.

    Receives a UUID of a given record as well as the phonetic block
    as the parameters. The method creates a list of dictionaries
    representing signatures for the given phonetic block within the record.

    :param record_id:
        A UUID of a given record.

        Example:
            record_id = "beb847d1-c7e0-48b2-9f48-a0d5d0586199"

    :signature_block:
        A phonetic notation of a full name using nyssis algorithm.

        Example:
            signature_block = "WANGy"

    :return:
        A list of dictionaries representing signatures with the
        given phonetic block.

        Example:
            [{'author_affiliation': u'MIT, Cambridge, CTP',
              'author_name': u'Wang, Yi-Nan',
              'publication_id': u'13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
              'signature_id': u'a4156520-560d-4248-a57f-949c361e0dd0',
              'author_recid': u'10123',
              'author_claimed: False}]
    """
    _source = [
        "authors.affiliations",
        "authors.curated_relation",
        "authors.full_name",
        "authors.recid",
        "authors.signature_block",
        "authors.uuid"
    ]

    response = _get_record(record_id, _source)

    try:
        authors = response.get("authors")
        signatures = []

        for author in authors:
            if author['signature_block'] == signature_block:
                author_affiliation = []

                if 'affiliations' in author:
                    for affiliation in author['affiliations']:
                        author_affiliation.append(affiliation['value'])

                signatures.append({
                    "publication_id": str(record_id),
                    "signature_id": author['uuid'],
                    "author_affiliation": ' '.join(author_affiliation),
                    "author_name": author['full_name'],
                    "author_recid": author.get('recid', False),
                    "author_claimed": author.get('curated_relation', False),
                })

        return signatures
    except KeyError:
        return []


def get_blocks_from_record(record_id):
    """Get all the signature blocks for the given record ID.

    Receives a UUID of the given record as the parameter.
    Querying the Elasticsearch instance, the method returns
    a list of authors written in the phonetic notation, using
    nyssis algorithm.

    :param record_id:
        A UUID of a given record.

        Example:
            record_id = "beb847d1-c7e0-48b2-9f48-a0d5d0586199"

    :return:
        A list of strings containing the phonetic notation of names of the
        authors.

        Example:
            [u'CACATRANv', u'SARANANa', u'TANASANa', u'ADANw', ...]
    """
    query = {
        "fields": [
            "authors.signature_block"
        ],
        "query": {
            "ids": {
                "values": [str(record_id)]
            }
        }
    }

    response = _search(query)

    try:
        return response[0].get("fields", {}).get("authors.signature_block", [])
    except IndexError:
        return []


def get_records_from_block(signature_block):
    """Get all the records containing a given block.

    Receives a signature block as the parameter.
    Querying the Elasticsearch instance, the method returns
    a list of records UUIDs containing the author, whose name
    is the same in phonetic notation as the given signature block.

    :signature_block:
        A phonetic notation of a full name using nyssis algorithm.

        Example:
            signature_block = "CACATRANv"

    :return:
        A list of strings representing records ids containing
        specific signature block in its record.

        Example:
            [u'545be179-5d53-4e3d-a605-82628d0dbbc9',
             u'5d56f5e7-a3fd-45cc-8818-5c0b5b7c4352', ...]
    """
    query = {
        "fields": [],
        "query": {
            "match": {
                "authors.signature_block": str(signature_block)
            }
        }
    }

    return [record["_id"] for record in _scroll_search(query)]


def get_signature(uuid):
    """Return a signature for a given UUID.

    The method receives a UUID of a signature.
    Querying the Elasticsearch instance, the method returns a
    dictionary representing the single signature.
    The method is used during a creation of a new author profile.

    :param uuid:
        A string representing UUID of the given signature.

        Example:
            uuid = 'c2f432bd-2f52-4c16-ac66-096f168c762f'

    :return:
        A dictionary representing signautre.

        Example:
            {u'affiliations': [{u'value': u'Yerevan Phys. Inst.'}],
             u'alternative_name': None,
             u'curated_relation': False,
             u'email': None,
             u'full_name': u'Chatrchyan, Serguei',
             u'inspire_id': None,
             u'orcid': None,
             u'profile': u'',
             u'recid': None,
             u'role': None,
             u'uuid': u'd63537a8-1df4-4436-b5ed-224da5b5028c'}
    """
    query = {
        "_source": [
            "authors.affiliations",
            "authors.alternative_name",
            "authors.curated_relation",
            "authors.email",
            "authors.full_name",
            "authors.inspire_id",
            "authors.orcid",
            "authors.profile",
            "authors.recid",
            "authors.contributor_roles.value",
            "authors.uuid"
        ],
        "query": {
            "match": {
                "authors.uuid": str(uuid)
            }
        }
    }

    response = _search(query)[0]
    signatures = response['_source']['authors']

    for signature in signatures:
        if signature['uuid'] == str(uuid):
            return signature
