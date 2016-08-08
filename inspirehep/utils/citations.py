# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.jinja2 import render_template_to_string


class Citation(object):
    """Class used to output citations format in detailed record"""

    def __init__(self, record):
        self.record = record

    def citations(self):
        """Return citation export for single record."""

        out = []
        row = []

        # Get citations
        record_citations = LiteratureSearch().query_from_iq(
            'refersto:' + self.record['control_number']
        ).params(
            _source=[
                'control_number',
                'citation_count',
                'titles',
                'earliest_date'
            ]
        ).execute().hits

        for citation in record_citations:

            citation_from_es = LiteratureSearch().get_source(citation.meta.id)

            row.append(render_template_to_string(
                "inspirehep_theme/citations.html",
                record=citation_from_es))
            try:
                citation_count = citation.citation_count
            except AttributeError:
                citation_count = 0
            row.append(citation_count)
            out.append(row)
            row = []

        return out
