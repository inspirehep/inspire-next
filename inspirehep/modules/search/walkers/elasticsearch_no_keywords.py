# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

    @visitor(KeywordOp)  # noqa: F811
    def visit(self, node, left, right):
        raise QueryHasKeywords()

    @visitor(MalformedQuery)  # noqa: F811
    def visit(self, op):
        # FIXME: Should send signal to display a message to the user.
        return

    @visitor(AndOp)  # noqa: F811
    def visit(self, node, left, right):
        return

    @visitor(OrOp)  # noqa: F811
    def visit(self, node, left, right):
        pass

    @visitor(NotOp)  # noqa: F811
    def visit(self, node, op):
        pass

    @visitor(ValueQuery)  # noqa: F811
    def visit(self, node, op):
        return

    @visitor(Keyword)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(Value)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(SingleQuotedValue)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(DoubleQuotedValue)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(RegexValue)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(RangeOp)  # noqa: F811
    def visit(self, node, left, right):
        pass

    @visitor(EmptyQuery)  # noqa: F811
    def visit(self, node):
        return

    @visitor(GreaterOp)  # noqa: F811
    def visit(self, node, value_fn):
        pass

    @visitor(WildcardQuery)  # noqa: F811
    def visit(self, node):
        pass

    @visitor(LowerOp)  # noqa: F811
    def visit(self, node, value_fn):
        pass

    @visitor(GreaterEqualOp)  # noqa: F811
    def visit(self, node, value_fn):
        pass

    @visitor(LowerEqualOp)  # noqa: F811
    def visit(self, node, value_fn):
        pass
    # pylint: enable=W0612,E0102
