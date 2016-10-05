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

"""INSPIRE Query class to wrap the Q object from elasticsearch-dsl."""

from __future__ import absolute_import, division, print_function

import json

import pypeg2
from elasticsearch_dsl import Q
from flask import current_app

from invenio_query_parser.ast import MalformedQuery

from .parser import Main
from .walkers.elasticsearch import ElasticSearchDSL
from .walkers.elasticsearch_no_keywords import ElasticSearchNoKeywordsDSL
from .walkers.elasticsearch_no_keywords import QueryHasKeywords
from .walkers.pypeg_to_ast import PypegConverter
from .walkers.spires_to_invenio import SpiresToInvenio


walkers = [PypegConverter(), SpiresToInvenio()]


def inspire_query_factory():
    """Create a parser returning Elastic Search DSL query instance."""

    def invenio_query(pattern, search):

        try:
            query = pypeg2.parse(pattern, Main, whitespace='')

            for walker in walkers:
                query = query.accept(walker)

        except SyntaxError:
            query = MalformedQuery("")

        try:
            search_walker = ElasticSearchNoKeywordsDSL()
            query.accept(search_walker)
            query = Q('multi_match',
                      query=pattern,
                      fields=search.default_fields(),
                      zero_terms_query="all")
        except QueryHasKeywords:
            query = query.accept(ElasticSearchDSL(
                current_app.config.get(
                    "SEARCH_ELASTIC_KEYWORD_MAPPING", {}
                )
            ))
        finally:
            if current_app.debug:
                current_app.logger.debug(
                    json.dumps(search.to_dict(), indent=4)
                )

            return query

    return invenio_query
