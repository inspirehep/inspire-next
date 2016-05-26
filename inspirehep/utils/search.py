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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Functions for searching ES and returning the results."""

from invenio_search.api import RecordsSearch
from inspirehep.modules.search import IQ


def perform_es_search(q, index, start=0, size=10, sort=None, fields=None):
    """Helper to use elasticsearch_dsl with Spires/Invenio syntax."""
    query = IQ(q)

    search = RecordsSearch(index=index).query(query)
    if sort:
        search = search.sort(sort)
    if fields and isinstance(fields, list):
        search = search.extra(_source={'include': fields})
    return search[start:start + size].execute()
