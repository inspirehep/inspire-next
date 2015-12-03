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

from invenio_ext.template import render_template_to_string

# MAX_REFERENCES_NUMBER = 200


class Reference(object):
    """Class used to output reference format in detailed record"""

    def __init__(self, record):
        self.record = record

    def references(self):
        """Reference export for single record in datatables format.

        :returns: list
            List of lists where every item represents a datatables row.
            A row consists of [reference_number, reference, num_citations]
        """
        from invenio_search.api import Query

        out = []
        row = []
        references = self.record.get('references')
        if references:
            refs_to_get_from_es = [ref['recid'] for i, ref in enumerate(references)
                                   if ref.get('recid') and i <= MAX_REFERENCES_NUMBER]
            es_query = ' or '.join(['control_number:' + str(recid) for recid in refs_to_get_from_es])
            refs_from_es = {record['control_number']: record for record in Query(es_query).search().records()}

            number = 0
            for reference in references:
                row.append(number + 1)
                if 'recid' in reference:
                    recid = reference['recid']
                    ref_record = refs_from_es.get(str(recid))
                    if ref_record:
                        number += 1
                        row.append(render_template_to_string(
                            "references.html",
                            number=str(number),
                            record=ref_record
                        ))

                else:
                    number += 1
                    row.append(render_template_to_string(
                        "references.html",
                        number=str(number),
                        reference=reference))
                row.append(self.record.get('citation_count'), '')
                out.append(row)
                row = []

                # if number >= MAX_REFERENCES_NUMBER:
                #     break

        return out

#     def display_count(self):
#         references_count = len(self.record['references']) if self.record.get('references') else 0
#         show_count = references_count if references_count < MAX_REFERENCES_NUMBER else MAX_REFERENCES_NUMBER

#         return "Showing {0} of {1}".format(show_count, references_count)
# >>>>>>> 3fefb9d... templates: add display of citations
