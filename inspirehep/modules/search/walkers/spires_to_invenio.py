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
# or submit itself to any jurisdiction.

"""Implement query printer."""

from __future__ import absolute_import, division, print_function

from invenio_query_parser import ast
from invenio_query_parser.visitor import make_visitor

from ..ast import SpiresOp
from ..config import SPIRES_KEYWORDS


class SpiresToInvenio(object):
    visitor = make_visitor()

    # pylint: disable=W0613,E0102

    @visitor(ast.AndOp)
    def visit(self, node, left, right):
        return type(node)(left, right)

    @visitor(ast.OrOp)
    def visit(self, node, left, right):
        return type(node)(left, right)

    @visitor(ast.KeywordOp)
    def visit(self, node, left, right):
        return type(node)(left, right)

    @visitor(ast.RangeOp)
    def visit(self, node, left, right):
        return type(node)(left, right)

    @visitor(ast.NotOp)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.GreaterOp)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.LowerOp)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.GreaterEqualOp)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.LowerEqualOp)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.Keyword)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.Value)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.WildcardQuery)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.ValueQuery)
    def visit(self, node, op):
        return type(node)(op)

    @visitor(ast.SingleQuotedValue)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.DoubleQuotedValue)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.RegexValue)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(ast.EmptyQuery)
    def visit(self, node):
        return type(node)(node.value)

    @visitor(SpiresOp)
    def visit(self, node, left, right):
        left.value = SPIRES_KEYWORDS[left.value.lower()]
        if (left.value is 'author') and (type(right) is not ast.WildcardQuery):
            return ast.KeywordOp(left, ast.DoubleQuotedValue(right.value))
        return ast.KeywordOp(left, right)

    # pylint: enable=W0612,E0102
