#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from invenio_search import current_search_client
from invenio_search.api import Query
from jinja2 import render_template_to_string


class Citation(object):
    """Class used to output citations format in detailed record"""

    def __init__(self, record):
        self.record = record

    def citations(self):
        """Return citation export for single record."""

        out = []
        row = []

        es_query = Query('refersto:' + self.record['control_number'])
        es_query.body.update(
            {
                'sort': [{'citation_count': {'order': 'desc'}}]
            }
        )

        record_citations = current_search_client.search(
            index='records-hep',
            doc_type='hep',
            body=es_query.body
        )['hits']['hits']

        for citation in record_citations:
            citation = citation['_source']

            row.append(render_template_to_string(
                "inspirehep_theme/citations.html",
                record=citation))
            out.append(row)
            row.append('')

            row = []

        return out
