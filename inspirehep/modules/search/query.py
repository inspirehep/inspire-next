# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""INSPIRE Query class to wrap a query object from invenio_search."""

from invenio_search.api import Query
from invenio_search.utils import query_enhancers, search_walkers

from invenio_query_parser.ast import MalformedQuery

from werkzeug.utils import cached_property

from .walkers.elasticsearch_no_keywords import ElasticSearchNoKeywordsDSL
from .walkers.elasticsearch_no_keywords import QueryHasKeywords


class InspireQuery(Query):

    """Extension of invenio_search.api.Query."""

    def __init__(self, *args, **kwargs):
        """Provide Query parameters."""
        super(InspireQuery, self).__init__(*args, **kwargs)

    @cached_property
    def query(self):
        """Catch SyntaxError upon query generation and return MalformedQuery."""
        try:
            return super(InspireQuery, self).query
        except SyntaxError:
            return MalformedQuery("")

    def build(self, **kwargs):
        """Build query body."""
        # Enhance query first
        for enhancer in query_enhancers():
            enhancer(self, **kwargs)

        query = self.query

        if self._parser is not None:
            try:
                walker = ElasticSearchNoKeywordsDSL()
                query.accept(walker)
                query = {
                    "multi_match": {
                        "query": self._query,
                        "zero_terms_query": "all",
                        "fields": [
                            "title^3",
                            "title.raw^10",
                            "abstract^2",
                            "abstract.raw^4",
                            "author^10",
                            "author.raw^15",
                            "reportnumber^10",
                            "eprint^10",
                            "doi^10"]}}
            except QueryHasKeywords:
                for walker in search_walkers():
                    query = query.accept(walker)

        self.body['query'] = query
