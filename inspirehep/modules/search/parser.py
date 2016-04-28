# -*- coding: utf-8 -*-
#
# This file is part of Invenio-Query-Parser.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# Invenio-Query-Parser is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-Query-Parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""SPIRES parser implementation."""

from invenio_query_parser.parser import *
from invenio_query_parser.parser import _

from .config import SPIRES_KEYWORDS


class SpiresKeywordRule(LeafRule):
    grammar = attr('value', re.compile(r"(%s)\b" % "|".join(
        SPIRES_KEYWORDS.keys()), re.IGNORECASE))


class SpiresSimpleValue(LeafRule):

    def __init__(self, values):
        super(SpiresSimpleValue, self).__init__()
        self.value = "".join(v.value for v in values)


class SpiresSimpleValueUnit(LeafRule):
    grammar = [
        re.compile(r"[^\s\)\(]+"),
        (re.compile(r'\('), SpiresSimpleValue, re.compile(r'\)')),
    ]

    def __init__(self, args):
        super(SpiresSimpleValueUnit, self).__init__()
        if isinstance(args, string_types):
            self.value = args
        else:
            self.value = args[0] + args[1].value + args[2]


SpiresSimpleValue.grammar = some(SpiresSimpleValueUnit)


class SpiresSmartValue(UnaryRule):

    @classmethod
    def parse(cls, parser, text, pos):  # pylint: disable=W0613
        """Match simple values excluding some Keywords like 'and' and 'or'"""
        if not text.strip():
            return text, SyntaxError("Invalid value")

        class Rule(object):
            grammar = attr('value', SpiresSimpleValue), omit(re.compile(".*"))

        try:
            tree = pypeg2.parse(text, Rule, whitespace="")
        except SyntaxError:
            return text, SyntaxError("Expected %r" % cls)
        else:
            r = tree.value

        if r.value.lower() in ('and', 'or', 'not'):
            return text, SyntaxError("Invalid value %s" % r.value)

        return text[len(r.value):], r


class SpiresValue(ast.ListOp):
    grammar = [
        (SpiresSmartValue, maybe_some(Whitespace, SpiresSmartValue)),
        Value,
    ]


class GreaterQuery(UnaryRule):
    grammar = (
        omit([
            Literal('>'),
            re.compile('after', re.I)
        ], _),
        attr('op', SpiresValue)
    )


class GreaterEqualQuery(UnaryRule):
    grammar = [
        (omit(Literal('>='), _), attr('op', SpiresValue)),
        (attr('op', Number), omit(re.compile(r'\+(?=\s|\)|$)'))),
    ]


class LowerQuery(UnaryRule):
    grammar = (
        omit([
            Literal('<'),
            re.compile('before', re.I)
        ], _),
        attr('op', SpiresValue)
    )


class LowerEqualQuery(UnaryRule):
    grammar = [
        (omit(Literal('<='), _), attr('op', SpiresValue)),
        (attr('op', Number), omit(re.compile(r'\-(?=\s|\)|$)'))),
    ]


class Find(Keyword):
    regex = re.compile(r"(find|fin|f)", re.I)


class SpiresKeywordQuery(BinaryRule):
    pass


class SpiresValueQuery(UnaryRule):
    grammar = attr('op', SpiresValue)


class SpiresSimpleQuery(UnaryRule):
    grammar = attr('op', [SpiresKeywordQuery, SpiresValueQuery])


class SpiresQuery(ListRule):
    pass


class SpiresParenthesizedQuery(UnaryRule):
    grammar = (
        omit(Literal('('), _),
        attr('op', SpiresQuery),
        omit(_, Literal(')')),
    )


class SpiresNotQuery(UnaryRule):
    grammar = (
        [
            omit(re.compile(r"and\s+not", re.I)),
            omit(re.compile(r"not", re.I)),
        ],
        [
            (omit(Whitespace), attr('op', SpiresSimpleQuery)),
            (omit(_), attr('op', SpiresParenthesizedQuery)),
            (omit(Whitespace), attr('op', SpiresValueQuery)),
        ],
    )


class SpiresAndQuery(UnaryRule):
    grammar = (
        omit(re.compile(r"and", re.I)),
        [
            (omit(Whitespace), attr('op', SpiresSimpleQuery)),
            (omit(_), attr('op', SpiresParenthesizedQuery)),
            (omit(Whitespace), attr('op', SpiresValueQuery)),
            (omit(re.compile(r".*", re.I)), attr('op', EmptyQueryRule)),
        ]
    )


class SpiresOrQuery(UnaryRule):
    grammar = (
        omit(re.compile(r"or", re.I)),
        [
            (omit(Whitespace), attr('op', SpiresSimpleQuery)),
            (omit(_), attr('op', SpiresParenthesizedQuery)),
            (omit(Whitespace), attr('op', SpiresValueQuery)),
            (omit(re.compile(r".*", re.I)), attr('op', EmptyQueryRule)),
        ]
    )


SpiresQuery.grammar = attr('children', (
    [
        SpiresParenthesizedQuery,
        SpiresSimpleQuery,
    ],
    maybe_some((
        omit(_),
        [
            SpiresNotQuery,
            SpiresAndQuery,
            SpiresOrQuery,
        ]
    )),
))


SpiresKeywordQuery.grammar = [
    (
        attr('left', NestableKeyword),
        omit(_, Literal(':'), _),
        attr('right', [
            SpiresParenthesizedQuery,
            SpiresSimpleQuery,
            ValueQuery
        ]),
    ),
    (
        attr('left', NestableKeyword),
        omit(Whitespace),
        attr('right', [
            SpiresParenthesizedQuery,
            SpiresSimpleQuery,
            SpiresValueQuery
        ]),
    ),
    (
        attr('left', KeywordRule),
        omit(_, Literal(':'), _),
        attr('right', Value)
    ),
    (
        attr('left', SpiresKeywordRule),
        omit(_, Literal(':'), _),
        attr('right', Value)
    ),
    (
        attr('left', SpiresKeywordRule),
        omit(Whitespace),
        attr('right', [
            GreaterEqualQuery,
            GreaterQuery,
            LowerEqualQuery,
            LowerQuery,
            RangeOp,
            WildcardQuery,
            SpiresValue
        ])
    ),
]


class FindQuery(UnaryRule):
    grammar = omit(Find, Whitespace), attr('op', SpiresQuery)


class Main(UnaryRule):
    initialized = False

    def __init__(self):
        """Initialize list of allowed keywords on first call."""
        if not Main.initialized:
            from invenio_query_parser.utils import build_valid_keywords_grammar
            from flask import current_app

            build_valid_keywords_grammar(
                current_app.config.get('SEARCH_ALLOWED_KEYWORDS', [])
            )
            Main.initialized = True

    grammar = [
        (omit(_), attr('op', [FindQuery, Query]), omit(_)),
        attr('op', EmptyQueryRule),
    ]
