#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es
from jinja2 import render_template_to_string

from invenio_search.api import Query


class Conference(object):
    """Class used to output reference format in detailed record"""
                                                    
    def __init__(self, series_name):
        self.series_name = series_name

    def conferences(self):
        """Reference export for single record in datatables format.
        :returns: list
            List of lists where every item represents a datatables row.
            A row consists of [reference_number, reference, num_citations]
        """
        out = []
        # series = self.record.get('series')[0]
        # series_name = 'Rencontres de Moriond'
        # return self.record
        # out = series
        # return out

        # out = ''

        es_query = Query()
        es_query.body.update(
            {
                "query": {
                    "bool": {
                        "must": [
                            { "match": { "series":   self.series_name }}
                        ]
                    }
                }#, "size": 2
            }
        )

        conferences_in_series = es.search(
            index='records-conferences',
            doc_type='conferences',
            body=es_query.body,
            _source=[
                    'control_number',
                    'title',
                    'place',
                    'opening_date',
                    'closing_date'
                ]
        )['hits']['hits']

        number = 1
        for conference in conferences_in_series:
            row = []
            conference = conference['_source']
            # TO-DO: Exclude current conference in the series
            row.append((render_template_to_string(
                        "inspirehep_theme/conferences_in_series.html",
                        record=conference)))
            row.append(conference.get('place', ''))
            row.append('')
            row.append((render_template_to_string(
                        "inspirehep_theme/conferences_in_series_date.html",
                        record=conference)))
            out.append(row)

        return out

        # if series:
        #     refs_to_get_from_es = [ref['recid'] for i, ref in enumerate(series)
        #                            if ref.get('recid')]
        #     es_query = ' or '.join(['control_number:' + str(recid) for recid in refs_to_get_from_es])

        #     pid = PersistentIdentifier.get('literature', recid)

        #     refs_from_es = es.get_source(index='records-hep',
        #                                  id=pid.object_uuid,
        #                                  doc_type='hep',
        #                                  ignore=404)
        #     number = 1
        #     for reference in series:
        #         row = []
        #         number += 1
        #         if 'recid' in reference:
        #             recid = reference['recid']
        #             ref_record = refs_from_es.get(str(recid))
        #             if ref_record:
        #                 row.append(render_template_to_string(
        #                     "inspirehep_theme/references.html",
        #                     number=str(number),
        #                     record=ref_record
        #                 ))
        #                 row.append(ref_record.get('citation_count', ''))
        #                 out.append(row)
        #                 continue

        #         row.append(render_template_to_string(
        #             "inspirehep_theme/references.html",
        #             number=str(number),
        #             reference=reference))
        #         row.append('')
        #         out.append(row)

        # return out