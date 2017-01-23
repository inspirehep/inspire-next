# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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

"""Implement AST convertor to Elastic Search DSL."""

from __future__ import absolute_import, division, print_function

from invenio_query_parser.ast import (
    AndOp, DoubleQuotedValue, EmptyQuery,
    GreaterEqualOp, GreaterOp, Keyword,
    KeywordOp, LowerEqualOp, LowerOp,
    MalformedQuery, NotOp, OrOp, RangeOp, RegexValue,
    SingleQuotedValue, Value, ValueQuery, WildcardQuery

)
from invenio_query_parser.visitor import make_visitor


class QueryHasKeywords(Exception):
    pass


class ElasticSearchNoKeywordsDSL(object):

    """Implement visitor to create Elastic Search DSL for queries that don't include keywords."""

    visitor = make_visitor()

    @visitor(KeywordOp)
    def visit(self, node, left, right):
        raise QueryHasKeywords()

    @visitor(MalformedQuery)
    def visit(self, op):
        # FIXME: Should send signal to display a message to the user.
        return

    @visitor(AndOp)
    def visit(self, node, left, right):
        return

    @visitor(OrOp)
    def visit(self, node, left, right):
        pass

    @visitor(NotOp)
    def visit(self, node, op):
        pass

    @visitor(ValueQuery)
    def visit(self, node, op):
        return

    @visitor(Keyword)
    def visit(self, node):
        pass

    @visitor(Value)
    def visit(self, node):
        pass

    @visitor(SingleQuotedValue)
    def visit(self, node):
        pass

    @visitor(DoubleQuotedValue)
    def visit(self, node):
        pass

    @visitor(RegexValue)
    def visit(self, node):
        pass

    @visitor(RangeOp)
    def visit(self, node, left, right):
        pass

    @visitor(EmptyQuery)
    def visit(self, node):
        return

    @visitor(GreaterOp)
    def visit(self, node, value_fn):
        pass

    @visitor(WildcardQuery)
    def visit(self, node):
        pass

    @visitor(LowerOp)
    def visit(self, node, value_fn):
        pass

    @visitor(GreaterEqualOp)
    def visit(self, node, value_fn):
        pass

    @visitor(LowerEqualOp)
    def visit(self, node, value_fn):
        pass
    # pylint: enable=W0612,E0102
