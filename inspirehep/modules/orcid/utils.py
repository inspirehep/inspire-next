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

from __future__ import absolute_import, division, print_function


from flask import current_app, session

from .schema import orcid_overdo

from inspirehep.modules.authors.receivers import _query_beard_api
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.modules.search import AuthorsSearch, LiteratureSearch
from inspirehep.utils.bibtex import Bibtex

from invenio_orcid.proxies import current_orcid
from invenio_records.api import Record
from invenio_search import current_search_client


def convert_to_orcid(record):
    """ Converts a given record to a json containing the information that
    orcid needs.
    """
    orcid_json = orcid_overdo.do(record)
    orcid_json['external-ids'] = {'external-id': orcid_json['external-id']}
    orcid_json.pop('external-id')

    orcid_json['citation'] = {'citation': Bibtex(
        record).format(), 'citation-type': 'BIBTEX'}
    return orcid_json


def get_orcid_id(author):
    """Return the Orcid Id of a given author record.

    :param author: An author record.
    """
    for orcid_id in author['ids']:
        if orcid_id['type'] == 'ORCID':
            return orcid_id['value']


def match_profiles(token, response):
    author_name = response['name']
    author_token = token.token()[0]
    author_orcid = response['orcid']

    # Query ORCiD for the records that are associated with the logged in
    # author.
    orcid_records_dois, orcid_records_arxiv_ids = get_identifiers_from_orcid_records(
        author_orcid, author_token)
    # Getting the phonetic_block of the current author
    phonetic_block = _query_beard_api([author_name])[author_name]
    rec_from_phonetics = query_for_authors_references_using_phonetic_block(
        phonetic_block, orcid_records_dois, orcid_records_arxiv_ids)
    possible_profiles = extract_author_profiles_from_hep_records(
        rec_from_phonetics)
    possible_profiles = solve_references_of_authors(possible_profiles)
    assigned_profile = find_profiles(possible_profiles)

    if not assigned_profile:
        # Get all authors from records that match the fetched records.
        rec_from_identifiers = query_for_authors_from_literature_records_using_identifiers_and_full_name(
            author_name, orcid_records_arxiv_ids, orcid_records_dois)

        possible_profiles = extract_author_profiles_from_hep_records(
            rec_from_identifiers)

        assigned_profile = find_profiles(possible_profiles)

        # In case our euristics didn't match any profiles we search by name all
        # the records.
        if not assigned_profile:
            # Search all Inspire profiles by authors full_name
            author_profiles = query_for_author_profiles_using_full_name(
                author_name)

            if len(author_profiles) is 1:
                assigned_profile = assign_profile(author_profiles[0])
            else:
                possible_profiles = []
                for record in author_profiles:
                    try:
                        # If the profile already has an orcid associated with it
                        # then it's not possible that it's the logged in authors
                        # profile.
                        author_identifiers = record['_source']['ids']
                        for identifier in author_identifiers:
                            if 'orcid' in identifier:
                                continue
                            possible_profiles.append(
                                record['_source']['self']['$ref'])
                    except KeyError:
                        continue
                assigned_profile = find_profiles(possible_profiles)
    return assigned_profile


def get_inspire_records_that_match_with_list_of_dois(dois):
    """ Returns a list of dois, of records that are presented on inspire based
    on a list of dois.
    """
    records = query_for_literature_records_using_list_of_dois(dois)
    records_dois = []
    for record in records:
        records_dois.append(record['fields']['dois.value'][0])
    # only_on_orcid = []
    # for doi in dois:
    #     if doi not in records_dois:
    #         only_on_orcid.append(doi)
    return records_dois


def get_inspire_records_that_match_with_list_of_arxiv_ids(arxiv_ids):
    """ Returns a list of arxiv ids, of records that are presented on inspire based
    on a list of arxiv ids.
    """
    records = query_for_literature_records_using_list_of_arxiv_ids(arxiv_ids)
    records_arxiv_ids = []
    for record in records:
        records_arxiv_ids.append(record['fields']['arxiv_eprints.value'][0])
    # only_on_orcid = []
    # for arxiv in arxiv_ids:
    #     if arxiv not in records_arxiv_ids:
    #         only_on_orcid.append(arxiv)
    return records_arxiv_ids


def query_elasticsearch_for_literature_records_using_a_profile_reference(profile):

    search = LiteratureSearch().query(
        {'term': {
            'authors.record.$ref': profile
        }
        }
    ).params(
        size=2
    ).execute().hits.hits
    return search


def query_for_literature_records_using_list_of_dois(dois):

    search = LiteratureSearch().query(
        {'terms': {
            'dois.value': dois
        }
        }
    ).params(
        fields='dois.value',
        size=len(dois)
    ).execute().hits.hits

    return search


def query_for_literature_records_using_list_of_arxiv_ids(arxiv_ids):

    search = LiteratureSearch().query(
        {'terms': {
            'arxiv_eprints.value': arxiv_ids
        }
        }
    ).params(
        fields='arxiv_eprints.value',
        size=len(arxiv_ids)
    ).execute().hits.hits

    return search


def query_for_authors_from_literature_records_using_identifiers_and_full_name(authors_full_name, arxiv_ids, dois):
    es_filter = {
        "nested": {
            "path": "authors",
            "filter": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.name_variations": authors_full_name
                            }
                        }
                    ],
                    "should": [
                        {
                            "match": {
                                "authors.full_name": authors_full_name
                            }
                        }
                    ]
                }
            },
            "inner_hits": {}
        }
    }

    es_query = {
        "bool": {
            "should": [
                {"terms": {
                    "arxiv_eprints.value": arxiv_ids
                }},
                {"terms": {
                    "dois.value": dois
                }}
            ]
        }
    }

    search = LiteratureSearch().query(es_query).filter(
        es_filter).params(size=10000).execute().hits.hits

    return search


def query_for_authors_references_using_phonetic_block(phonetic_block, dois, arxiv_ids):
    es_query = {"bool": {
        "should": [
            {"terms": {
                "arxiv_eprints.value": arxiv_ids
            }},
            {"terms": {
                "dois.value": dois
            }}
        ]
    }}

    es_filter = {"nested": {
        "path": "authors",
        "filter": {
            "term": {
                "authors.signature_block": {
                    "value": phonetic_block
                }
            }
        },
        "inner_hits": {}
    }}

    search = LiteratureSearch().query(es_query).filter(
        es_filter).params(size=10000).execute().hits.hits

    return search


def query_for_author_profiles_using_ref(reference):

    search = AuthorsSearch().query(
        {'term': {'self.$ref': reference}}
    ).params(
        size=1
    ).execute().hits.hits

    return search


def query_for_author_profiles_using_full_name(authors_full_name):
    es_query = {
        "bool": {
            "must": [{
                "match": {
                    "name.name_variations": authors_full_name
                }
            }
            ],
            "should": [{
                "match": {
                    "name.preferred_name": authors_full_name
                }},
                {
                "match": {
                    "name.value": authors_full_name
                }
            }
            ]
        }
    }

    search = AuthorsSearch.query(es_query).params(
        size=10000).execute().hits.hits

    return search


def get_identifiers_from_orcid_records(orcid, token):
    """ Queries orcid for records of a specific author (given his orcid-id)
    and returns two lists of the correspondins dois and arxiv-ids.

    :param orcid: an orcid-id of an author
    :param token: the access token of the author
    """

    api = current_orcid.member
    # Fetches all the records from orcid for the specified author.
    orcid_records = api.read_record_public(
        orcid, 'activities', token)
    orcid_records_dois = []
    orcid_records_arxiv_ids = []

    # Extract dois and arxiv-ids from those records.
    for record in orcid_records['works']['group']:
        if record['external-ids']['external-id'][0]['external-id-type'] == 'doi':
            orcid_records_dois.append(
                record['external-ids']['external-id'][0]['external-id-value'])
        if record['external-ids']['external-id'][0]['external-id-type'] == 'arxiv':
            orcid_records_arxiv_ids.append(
                record['external-ids']['external-id'][0]['external-id-value'])

    return orcid_records_dois, orcid_records_arxiv_ids


def extract_author_profiles_from_hep_records(records):
    """ Extract references to authors records.

    :param records: list of hep records
    """
    possible_profiles = set()
    for record in records:
        try:
            for author in record['inner_hits']['authors']['hits']['hits']:
                possible_profiles.add(author['_source']['record']['$ref'])
        except KeyError:
            continue
    return possible_profiles


def solve_references_of_authors(refs):
    """ Returns a list of author-records.

    :param refs: list of references to author records
    """
    possible_profiles = []
    for ref in refs:
        author_profile = replace_refs({'$ref': ref}, source='es')
        try:
            # If the profile has an orcid it's already claimed by somebody.
            for identifier in author_profile['ids']:
                if 'orcid' in identifier:
                    continue
            possible_profiles.append(ref)
        except (KeyError, TypeError):
            continue
    return possible_profiles


def pick_records_from_author_profiles(profiles):
    """ Returns a fixed number of records corresponding to a number of author profiles
    in order to present them to the user, and ask him to pick the ones that he authored.

    In case of two possible profiles we return 2 records from each profile.
    In case of two to ten possible profiles we return 1 record from each profile.
    In case of more than ten possible profiles we return 1 records from each
    of the first 10 profiles.

    :param profiles: A list of author-records references
    """
    number_of_records_per_profile = 1
    picked_records = {}
    picked_recids = set()
    if len(profiles) is 2:
        number_of_records_per_profile = 2

    for profile in profiles[:10]:
        picked_records[profile] = []
        records = query_elasticsearch_for_literature_records_using_a_profile_reference(
            profile)
        for record in records[:number_of_records_per_profile]:
            if record['_source']['control_number'] not in picked_recids:
                record['_source']['_profile'] = profile
                picked_records[profile].append(record)
                picked_recids.add(record['_source']['control_number'])

    # In case that after eliminating doublicates there is only one possible profile
    # we assign that to the user.
    if len(picked_recids) is 1:
        picked_records = assign_profile(profile)
    return picked_records


def find_profiles(possible_profiles):
    """
    Returns a dictionary which has author-profile references as keys
    and lists of hep-records as values.

    This dictionary is then used to present to the user records from the
    corresponding possible-profile.

    :param possible_profiles: A list of author records.
    """
    if len(possible_profiles) is 1:
        profile = possible_profiles.pop()
        return assign_profile(profile)
    if len(possible_profiles) is 0:
        return {}
    chosen_records = pick_records_from_author_profiles(possible_profiles)
    return chosen_records


def assign_profile(profile, orcid=None):
    """ Assigns a profile to the user by adding his orcid-id to the existant profile.

    :param profile: The reference of the profile to be assigned.
    :param orcid: The orcid-id of the user. Normaly this is retrieved from the session.
    """
    if not orcid:
        orcid = session['users_orcid']
    author = query_for_author_profiles_using_ref(profile)[0]['_source']
    author['ids'].append({
        "type": u"ORCID",
        "value": orcid
    })
    current_search_client.index(
        index='records-authors', doc_type='authors', body=author)
    db_record = Record.create(author)
    db_record.commit()
    current_app.logger.info("Matched %s to logged in user.", profile)
    return {profile: []}
