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

from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.jinja2 import render_template_to_string
from inspirehep.utils.record_getter import get_es_records


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
            reference_recids = [
                str(ref['recid']) for ref in references if ref.get('recid')
            ]

            resolved_references = get_es_records(
                'literature',
                reference_recids,
                _source=[
                    'control_number',
                    'citation_count',
                    'titles',
                    'earliest_date',
                    'authors',
                    'collaboration',
                    'corporate_author',
                    'publication_info'
                ]
            )

            # Create mapping to keep reference order
            recid_to_reference = {
                str(ref['control_number']): ref for ref in resolved_references
            }
            for reference in references:
                row = []
                ref_record = recid_to_reference.get(
                    str(reference.get('recid')), {}
                )
                if 'publication_info' in reference:
                    reference['publication_info'] = force_force_list(
                        reference['publication_info']
                    )
                row.append(render_template_to_string(
                    "inspirehep_theme/references.html",
                    record=ref_record,
                    reference=reference
                ))
                row.append(ref_record.get('citation_count', ''))
                out.append(row)

        return out
