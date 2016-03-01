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

from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es

from inspirehep.utils.record import get_title
from inspirehep.modules.search import IQ

from jinja2 import render_template_to_string


class Citation(object):
    """Class used to output citations format in detailed record"""

    def __init__(self, record):
        self.record = record

    def citations(self):
        """Return citation export for single record."""

        out = []
        row = []

        # Get citations
        es_query = IQ('refersto:' + self.record['control_number'])
        record_citations = es.search(
            index='records-hep',
            doc_type='hep',
            body={"query": es_query.to_dict()},
            size=10,
            _source=[
                'control_number',
                'citation_count',
                'titles',
                'earliest_date'
            ]
        )['hits']['hits']

        for citation in record_citations:

            citation_from_es = es.get_source(index='records-hep',
                                             id=citation['_id'],
                                             doc_type='hep',
                                             ignore=404)

            row.append(render_template_to_string(
                "inspirehep_theme/citations.html",
                record=citation_from_es))
            row.append(citation.get('citation_count', ''))
            out.append(row)
            row = []

        return out
