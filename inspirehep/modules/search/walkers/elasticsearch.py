# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Wrap Elastic Search AST convertor."""

from flask import current_app

from invenio_query_parser.ast import (
    Value,
    DoubleQuotedValue
)
from invenio_query_parser.visitor import make_visitor
from invenio_query_parser.contrib.elasticsearch.walkers import dsl

from ..ast import FilterOp


class ElasticSearchDSL(dsl.ElasticSearchDSL):
    """Override constructor with default configuration option."""

    visitor = make_visitor(dsl.ElasticSearchDSL.visitor)

    def __init__(self):
        """Provide default keyword mapping."""
        super(ElasticSearchDSL, self).__init__(
            keyword_to_fields=current_app.config.get(
                'SEARCH_ELASTIC_KEYWORD_MAPPING'
            )
        )

    @visitor(Value)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='a')
            if keyword == 'author':
                return {"bool":
                        {"should": [
                            {"match": {
                                "authors.name_variations": str(node.value)}},
                            {"match": {"authors.full_name": str(node.value)}}]
                         }}
            return {
                'multi_match': {
                    'query': node.value,
                    'fields': fields,
                }
            }
        return query

    @visitor(DoubleQuotedValue)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='p')
            if keyword == 'author':
                return {"bool":
                        {"must": [
                            {"match": {"authors.name_variations": str(node.value)}}],
                            "should": [
                            {"match": {"authors.full_name": str(node.value)}}]
                         }}
            return {
                'multi_match': {
                    'query': node.value,
                    'type': 'phrase',
                    'fields': fields,
                }
            }
        return query

    @visitor(FilterOp)
    def visit(self, node, left, right):
        return {'filtered': {'query': [left], "filter": [right]}}
