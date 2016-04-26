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
        out = []
        references = self.record.get('references')
        if references:
            refs_to_get_from_es = [ref['recid'] for i, ref in enumerate(references)
                                   if ref.get('recid')]
            es_query = ' or '.join(['control_number:' + str(recid) for recid in refs_to_get_from_es])

            pid = PersistentIdentifier.get('literature', recid)

            refs_from_es = es.get_source(index='records-hep',
                                         id=pid.object_uuid,
                                         doc_type='hep',
                                         ignore=404)
            number = 1
            for reference in references:
                row = []
                number += 1
                if 'recid' in reference:
                    recid = reference['recid']
                    ref_record = refs_from_es.get(str(recid))
                    if ref_record:
                        row.append(render_template_to_string(
                            "inspirehep_theme/references.html",
                            number=str(number),
                            record=ref_record
                        ))
                        row.append(ref_record.get('citation_count', ''))
                        out.append(row)
                        continue

                row.append(render_template_to_string(
                    "inspirehep_theme/references.html",
                    number=str(number),
                    reference=reference))
                row.append('')
                out.append(row)

        return out