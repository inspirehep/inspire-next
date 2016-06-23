# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Implement AST convertor to Elastic Search DSL."""

from operator import or_

from elasticsearch_dsl import Q

from invenio_query_parser.ast import (AndOp, DoubleQuotedValue, EmptyQuery,
                                      GreaterEqualOp, GreaterOp, Keyword,
                                      KeywordOp, LowerEqualOp, LowerOp, NotOp,
                                      OrOp, RangeOp, RegexValue,
                                      SingleQuotedValue, Value,
                                      ValueQuery, WildcardQuery)
from invenio_query_parser.visitor import make_visitor

from ..ast import FilterOp


class ElasticSearchDSL(object):

    """Implement visitor to create Elastic Search DSL."""

    visitor = make_visitor()

    def __init__(self, keyword_to_fields=None):
        """Provide a dictinary mapping from keywords to Elastic field(s)."""
        self.keyword_to_fields = keyword_to_fields or {None: ['_all']}

    def get_fields_for_keyword(self, keyword, mode='a'):
        """Convert keyword to fields."""
        field = self.keyword_to_fields.get(keyword, keyword)
        if isinstance(field, dict):
            return field[mode]
        elif isinstance(field, (list, tuple)):
            return field
        return [field]

    # pylint: disable=W0613,E0102

    @visitor(FilterOp)
    def visit(self, node, left, right):
        return Q({'filtered': {'query': [left], "filter": [right]}})

    @visitor(AndOp)
    def visit(self, node, left, right):
        return left & right

    @visitor(OrOp)
    def visit(self, node, left, right):
        return left | right

    @visitor(NotOp)
    def visit(self, node, op):
        return ~op

    @visitor(KeywordOp)
    def visit(self, node, left, right):
        if callable(right):
            return right(left)
        raise RuntimeError('Not supported second level operation.')

    @visitor(ValueQuery)
    def visit(self, node, op):
        return op(None)

    @visitor(Keyword)
    def visit(self, node):
        return node.value

    @visitor(WildcardQuery)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='p')
            value = str(node.value).replace('#', '*')
            if len(fields) > 1:
                res = Q('bool', should=[
                        Q('query_string',
                          query=value,
                          default_field=k,
                          analyze_wildcard=True) for k in fields])
            else:
                res = Q('query_string',
                        query=value,
                        default_field=fields[0],
                        analyze_wildcard=True)
            return res
        return query

    @visitor(Value)
    def visit(self, node):
        def query(keyword):
            # FIXME: This is a temporary hack that should be removed when
            # nested keywords search is implemented.
            if str(node.value).startswith('recid:'):
                node.value = node.value[len('recid:'):]

            fields = self.get_fields_for_keyword(keyword, mode='a')
            if fields == ['authors.full_name', 'authors.alternative_name']:
                return (
                    Q("match", authors__name_variations=str(node.value)) |
                    Q("match", authors__full_name=str(node.value)) |
                    Q("match", authors__inspire_bai=str(node.value))
                )
            return Q({
                'multi_match': {
                    'query': node.value,
                    'fields': fields
                }
            })
        return query

    @visitor(SingleQuotedValue)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='p')
            return Q('multi_match', query=node.value, fields=fields,
                     type='phrase')
        return query

    @visitor(DoubleQuotedValue)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='e')
            if fields == ['authors.full_name', 'authors.alternative_name']:
                return (
                    Q("term", authors__name_variations=str(node.value)) |
                    Q("term", authors__inspire_bai=str(node.value)) |
                    Q("match", authors__full_name=str(node.value))
                )

            if (len(fields) > 1):
                return Q({"bool":
                          {"should": [{"term": {k: str(node.value)}}
                                      for k in fields]}})
            else:
                return Q({'term': {fields[0]: node.value}})
        return query

    @visitor(RegexValue)
    def visit(self, node):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='r')
            if keyword is None or fields is None:
                raise RuntimeError('Not supported regex search for all fields')
            return reduce(or_, [
                Q('regexp', **{k: node.value}) for k in fields
            ])
        return query

    @visitor(EmptyQuery)
    def visit(self, node):
        return Q('match_all')

    def _range_operators(self, node, condition):
        def query(keyword):
            fields = self.get_fields_for_keyword(keyword, mode='r')
            return reduce(or_, [Q('range', **{k: condition}) for k in fields])
        return query

    @visitor(RangeOp)
    def visit(self, node, left, right):
        condition = {}
        if left:
            condition['gte'] = left(None).to_dict()['multi_match']['query']
        if right:
            condition['lte'] = right(None).to_dict()['multi_match']['query']

        return self._range_operators(node, condition)

    @visitor(GreaterOp)
    def visit(self, node, value_fn):
        condition = {'gt': value_fn(None).to_dict()['multi_match']['query']}
        return self._range_operators(node, condition)

    @visitor(LowerOp)
    def visit(self, node, value_fn):
        condition = {'lt': value_fn(None).to_dict()['multi_match']['query']}
        return self._range_operators(node, condition)

    @visitor(GreaterEqualOp)
    def visit(self, node, value_fn):
        condition = {'gte': value_fn(None).to_dict()['multi_match']['query']}
        return self._range_operators(node, condition)

    @visitor(LowerEqualOp)
    def visit(self, node, value_fn):
        condition = {'lte': value_fn(None).to_dict()['multi_match']['query']}
        return self._range_operators(node, condition)

    # pylint: enable=W0612,E0102
