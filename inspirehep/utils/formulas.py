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

"""
Utilities to handling LaTeX/MathML formulas.
"""


import re

import requests

from flask import current_app

from HTMLParser import HTMLParser


RE_SIMPLE_TEX_FORMULA = re.compile(r"\$(.+?)\$")
RE_SIMPLE_MATHML_FORMULA = re.compile(r"(\<math\b.+?\<\/math\>)", re.M + re.S)


class HTMLStripper(HTMLParser):

    def __init__(self):
        """Set initial values."""
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []
        self.inannotation = False

    def handle_data(self, d):
        """Return representation of pure text data."""
        if not self.inannotation:
            self.fed.append(d.strip())

    def handle_entityref(self, name):
        """Return representation of entities."""
        if not self.inannotation:
            self.fed.append('&%s;' % name)

    def handle_charref(self, name):
        """Return representation of numeric entities."""
        if not self.inannotation:
            self.fed.append('&#%s;' % name)

    def handle_starttag(self, tag, attrs):
        if tag == 'msqrt':
            self.fed.append(u'&radic;(')
        elif tag == 'annotation':
            self.inannotation = True

    def handle_endtag(self, tag):
        if tag == 'msqrt':
            self.fed.append(u')')
        elif tag == 'annotation':
            self.inannotation = False

    def get_data(self):
        """Return all the stripped data."""
        return self.unescape(''.join(self.fed))


def splitter(formula):
    """Split a formula.

    Given a unicode-based formulas, returns the set of its component, namely
    * the formula itself,
    * split after and before the equal sign,
    * split after and before any arrow,
    * consider inner content of parenthesis.
    """
    if not valid_component(formula):
        return []
    if u'=' in formula:
        return [formula] + [splitter(component) for component in formula.split(u'=')]
    if u'→' in formula:
        return [formula] + [splitter(component) for component in formula.split(u'→')]
    if u'/' in formula:
        return [formula] + [splitter(component) for component in formula.split(u'/')]
    return [formula]


def parenthesizer(formula):
    """Parenthesised components of a formula.

    Returns the parenthesized components of a formula.
    E.g.
        >>> parenthesizer("((a+b)*(c+d))/a")
        ["((a+b)*(c+d))/a", "a+b", "c+d", "(a+b)*(c+d)"]
    """
    ret = [formula]
    try:
        components = []
        for i, c in enumerate(formula):
            if c == u'(':
                components.append(i)
            elif c == u')':
                start = components.pop()
                ret.append(formula[start + 1:i])
    except IndexError:
        # Unbalanced parenthesis
        pass
    return ret


def flatten(elements):
    """Transforms a list of list into a flat list, recursively."""
    ret = []
    for element in elements:
        if isinstance(element, list):
            ret += flatten(element)
        else:
            ret.append(element)
    return ret


def formula2components(formula):
    """Return the set of components of a unicode formula."""
    return set(flatten(splitter(component) for component in parenthesizer(formula)))


def valid_component(component):
    """Check if a component has valid parentheses."""
    count = 0
    for c in component:
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0


def tex2mml(formula):
    """Converts a LaTeX formula to MathML."""
    mathjax_node_server = current_app.config['MATHOID_SERVER']
    return requests.post(mathjax_node_server + "/mml", {'q': formula.encode('utf8'), 'type': 'inline-tex'}).text


def mml2formula(text):
    """Transforms a MathML formula into a unicode one."""
    parser = HTMLStripper()
    parser.feed(text)
    return parser.get_data()


def get_tex_formulas_from_text(text):
    """Extract LaTeX formulas from text."""
    return RE_SIMPLE_TEX_FORMULA.findall(text)


def get_mathml_formulas_from_text(text):
    """Extract MathML formulas from text."""
    return RE_SIMPLE_MATHML_FORMULA.findall(text)


def get_all_unicode_formula_tokens_from_text(text, only_decays=True):
    """Returns all the unicode formula tokens suitable to be indexed."""
    formulas = []
    for latex_formula in get_tex_formulas_from_text(text):
        formulas.append(tex2mml(latex_formula))
    formulas += get_mathml_formulas_from_text(text)
    ret = set()
    for formula in formulas:
        formula = mml2formula(formula)
        if only_decays and u'→' not in formula:
            continue
        ret |= formula2components(formula)
    return ret
