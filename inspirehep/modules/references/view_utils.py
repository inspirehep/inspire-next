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

from invenio_records.api import Record

from inspirehep.utils.jinja2 import render_template_to_string
from inspirehep.modules.search import LiteratureSearch


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
            refs_to_get_from_es = [
                ref['recid'] for ref in references if ref.get('recid')
            ]
            records_from_es = LiteratureSearch().query_from_iq(
                ' OR '.join('recid:' + str(ref)
                            for ref in refs_to_get_from_es)
            ).params(
                size=9999,
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
            ).execute().to_dict()['hits']['hits']

            refs_from_es = {
                str(ref['_source']['control_number']): ref['_source'] for ref in records_from_es
            }
            for reference in references:
                row = []
                recid = reference.get('recid')
                ref_record = refs_from_es.get(str(recid)) if recid else None

                if recid and ref_record:
                    ref_record = Record(ref_record)
                    if ref_record:
                        row.append(render_template_to_string(
                            "inspirehep_theme/references.html",
                            record=ref_record,
                            reference=reference
                        ))
                        row.append(ref_record.get('citation_count', ''))
                        out.append(row)
                else:
                    # Easier to use record macros over reference records.
                    if 'publication_info' in reference:
                        reference['publication_info'] = [
                            reference['publication_info']]
                    else:
                        reference['publication_info'] = []
                    reference = Record(reference)

                    row.append(render_template_to_string(
                        "inspirehep_theme/references.html",
                        reference=reference))
                    row.append('')
                    out.append(row)

        return out
