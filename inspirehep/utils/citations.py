# -*- coding: utf-8 -*-
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

from invenio_ext.template import render_template_to_string

MAX_CITATIONS_NUMBER = 200


class Citation(object):
    """Class used to output citations format in detailed record"""

    def __init__(self, record):
        self.record = record

    def citations(self):
        """Return citation export for single record."""
        from invenio_search.api import Query

        out = ''
        recid = self.record['recid']
        es_query = Query('refersto:' + str(recid)).search()
        es_query.body.update({
            'size': MAX_CITATIONS_NUMBER,
            'sort': [{'citation_count': {'order': 'desc'}}]
        })
        citations = es_query.records()

        for index, citation in enumerate(citations):
            out += render_template_to_string("citations.html",
                                             number=str(index + 1),
                                             record=citation)
        if out:
            return out
        else:
            return 'There are no citations available for this record'

    def cit_count(self):
        all_citations_count = self.record.get('citation_count', 0)
        show_count = all_citations_count \
            if all_citations_count < MAX_CITATIONS_NUMBER\
            else MAX_CITATIONS_NUMBER

        return "Showing {0} of {1}".format(show_count, all_citations_count)
