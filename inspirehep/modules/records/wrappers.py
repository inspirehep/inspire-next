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


class JournalsRecord(Record):
    """Record class specialized for journal records."""

    @property
    def title(self):
        """."""
        titles = self.get('titles', [])
        if titles:
            return titles[0].get('title', '')

    @property
    def short_title(self):
        """."""
        short_titles = self.get('short_titles', [])
        if short_titles:
            return short_titles[0].get('title', '')

    @property
    def publisher(self):
        """."""
        publisher = self.get('publisher', [])
        if publisher:
            return publisher[0]

    @property
    def urls(self):
        """."""
        urls = self.get('urls', [])
        if urls:
            return [url.get('value', '') for url in urls]

    @property
    def name_variants(self):
        """."""
        name_variants = self.get('title_variants', [])
        if name_variants:
            return [name.get('title', '') for name in name_variants]
