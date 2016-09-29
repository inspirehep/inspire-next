# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

from inspirehep.modules.relations import current_db_session
from inspirehep.modules.relations.model.model_commands_producers import (
    match_record,
    render_query
)


class LiteratureRelationsSearch(object):


    @classmethod
    def get_impact_graph_summary(cls, recid, limit=None):
        limit_command = ''
        if limit:
            limit_command = ' LIMIT {}'.format(limit)

        query_elements = [
            match_record(recid, 'record'),
            'MATCH (record) <- [:REFERS_TO] - (citation)',
            'MATCH (record) - [:REFERS_TO] -> (reference)',
            'OPTIONAL MATCH (citation) <- [ref_citation:REFERS_TO] - ()',
            'OPTIONAL MATCH (reference) <- [ref_reference:REFERS_TO] - ()',
            ('WITH {control_number: citation.recid,'
             'date: citation.earliest_date, title: citation.title, '
             'citation_count: count(ref_citation)} as citations,'
             '{control_number: reference.recid, date: reference.earliest_date, '
             'title:  reference.title, '
             'citation_count: count(ref_reference)} as references '
            ),
            ('RETURN collect(citations) as citations, '
            'collect(references) as references'
            ),
            limit_command
        ]

        query = render_query(query_elements)

        def _process_paper(paper):
            return {
                "inspire_id": paper['control_number'],
                "citation_count": paper['citation_count'],
                "title": paper['title'],
                "year": paper['date'].split('-')[0]
            }

        response = [record for record in current_db_session.run(query)]

        return {
            'citations': map(_process_paper, response[0]['citations']),
            'references': map(_process_paper, response[0]['references'])
        }
