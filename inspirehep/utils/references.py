#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

from invenio.ext.template import render_template_to_string

from invenio_records.api import get_record


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
        row = []
        number = 0
        references = self.record['references']
        for reference in references:
            number += 1
            row.append(number)
            for reference_field in reference:
                if 'recid' in reference_field:
                    recid = reference['recid']
                    record = get_record(recid)
                    if record:
                        row.append(render_template_to_string(
                            "references.html",
                            number=str(number),
                            record=record))
            if 'recid' not in reference:
                row.append(render_template_to_string(
                    "references.html",
                    number=str(number),
                    reference=reference))
            # FIXME add the number of citations
            row.append("")
            out.append(row)
            row = []
        return out
