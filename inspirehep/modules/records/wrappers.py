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

from __future__ import absolute_import, division, print_function

from invenio_records.api import Record

from inspirehep.modules.search import JobsSearch


class JobsRecord(Record):

    """Record class specialized for job records."""

    @property
    def similar(self):
        def _build_query(id_):
            result = JobsSearch()
            return result.query({
                'more_like_this': {
                    'docs': [
                        {
                            '_id': id_,
                        },
                    ],
                    'min_term_freq': 0,
                    'min_doc_freq': 0,
                }
            })[0:2]

        query = _build_query(self.id)
        result = query.execute()

        return result
