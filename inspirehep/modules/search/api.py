# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

from __future__ import absolute_import, division, print_function

import logging

from flask import request
from flask_security import current_user

from elasticsearch import RequestError
from elasticsearch_dsl.query import Q

from invenio_search.api import DefaultFilter, RecordsSearch
from invenio_search import current_search_client as es

from inspirehep.modules.records.permissions import (
    all_restricted_collections,
    user_collections
)

from .query_factory import inspire_query_factory


logger = logging.getLogger(__name__)
IQ = inspire_query_factory()


class SearchMixin(object):
    """Mixin that adds helper functions to ElasticSearch DSL classes."""

    def query_from_iq(self, query_string):
        """Initialize ES DSL object using INSPIRE query parser.

        :param query_string: Query string as a user would input in INSPIRE's search box.
        :type query_string: string
        :returns: Elasticsearch DSL search class
        """
        return self.query(IQ(query_string, self))

    def get_source(self, uuid, **kwargs):
        """Get source from a given uuid.

        This function mimics the behaviour from the low level ES library
        get_source function.

        :param uuid: uuid of document to be retrieved.
        :type uuid: UUID
        :returns: dict
        """
        return es.get_source(
            index=self.Meta.index,
            doc_type=self.Meta.doc_types,
            id=uuid,
            **kwargs
        )

    def mget(self, uuids, **kwargs):
        """Get source from a list of uuids.

        :param uuids: uuids of documents to be retrieved.
        :type uuids: list of strings representing uuids
        :returns: list of JSON documents
        """
        results = []

        try:
            documents = es.mget(
                index=self.Meta.index,
                doc_type=self.Meta.doc_types,
                body={'ids': uuids},
                **kwargs
            )
            results = [document['_source'] for document in documents['docs']]
        except RequestError as e:
            logger.exception(e)

        return results


def inspire_filter():
    """Filter applied to all queries."""
    if request:
        collection = request.values.get('cc', 'Literature')

        user_roles = [r.name for r in current_user.roles]
        if 'superuser' in user_roles:
            user_coll = all_restricted_collections
        else:
            user_coll = user_collections

        query = Q('match', _collections=collection)

        for collection in list(all_restricted_collections - user_coll):
            query = query & ~Q('match', _collections=collection)

        return query


class LiteratureSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Literature database."""

    class Meta:
        index = 'records-hep'
        doc_types = 'hep'
        default_filter = DefaultFilter(inspire_filter)

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class AuthorsSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Authors database."""

    class Meta:
        index = 'records-authors'
        doc_types = 'authors'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class DataSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Data database."""

    class Meta:
        index = 'records-data'
        doc_types = 'data'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class ConferencesSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Conferences database."""

    class Meta:
        index = 'records-conferences'
        doc_types = 'conferences'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class JobsSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Jobs database."""

    class Meta:
        index = 'records-jobs'
        doc_types = 'jobs'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class InstitutionsSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Institutions database."""

    class Meta:
        index = 'records-institutions'
        doc_types = 'institutions'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class ExperimentsSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Experiments database."""

    class Meta:
        index = 'records-experiments'
        doc_types = 'experiments'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']


class JournalsSearch(RecordsSearch, SearchMixin):
    """Elasticsearch-dsl specialized class to search in Journals database."""

    class Meta:
        index = 'records-journals'
        doc_types = 'journals'

    def default_fields(self):
        """What fields to use when no keyword is specified."""
        return ['_all']
