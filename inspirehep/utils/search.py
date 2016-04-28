# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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


def perform_es_search(q, index, start=0, size=10, sort=None):
    """."""
    from invenio_search.api import RecordsSearch
    from inspirehep.modules.search import IQ
    query = IQ(q)

    if sort:
        return RecordsSearch(index=index).query(query). \
            sort(sort)[start:start + size].execute()
    else:
        return RecordsSearch(index=index).query(query)[start:start + size] \
            .execute()
