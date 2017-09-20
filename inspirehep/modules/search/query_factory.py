# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""INSPIRE Query class to wrap the Q object from elasticsearch-dsl."""

from __future__ import absolute_import, division, print_function

from elasticsearch_dsl import Q

import inspire_query_parser


def inspire_query_factory():
    """Create an Elastic Search DSL query instance using the generated Elastic Search query by the parser."""

    def inspire_query(query_string, search):
        return Q(inspire_query_parser.parse_query(query_string))

    return inspire_query
