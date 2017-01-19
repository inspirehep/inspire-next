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

"""SPIRES to Invenio query converter."""

from __future__ import absolute_import, division, print_function

from invenio_query_parser.walkers import repr_printer

import pypeg2

from .parser import Main
from .walkers import pypeg_to_ast


class SpiresToInvenioSyntaxConverter(object):
    def __init__(self):
        self.converter = pypeg_to_ast.PypegConverter()
        self.printer = repr_printer.TreeRepr()

    def parse_query(self, query):
        """Parse query string using given grammar"""
        tree = pypeg2.parse(query, Main, whitespace="")
        return tree.accept(self.converter)

    def convert_query(self, query):
        return self.parse_query(query).accept(self.printer)
