# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_records.signals import before_record_index


@before_record_index.connect
def populate_inspire_subjects(recid, json):
    """
    Populate a json record before indexing it to elastic.
    Adds a field for faceting INSPIRE subjects
    """
    inspire_subjects = [
        s['term'] for s in json.get('subject_terms', [])
        if s.get('scheme', '') == 'INSPIRE' and s.get('term')
    ]
    json['facet_inspire_subjects'] = inspire_subjects


@before_record_index.connect
def populate_inspire_document_type(recid, json):
    """ Populates a json record before indexing it to elastic.
        Adds a field for faceting INSPIRE document type
    """
    inspire_doc_type = []
    if 'collections' in json:
        for element in json.get('collections', []):
            if 'primary' in element and element.get('primary', ''):
                if element['primary'].lower() == 'thesis':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'published':
                    inspire_doc_type.append('peer reviewed')
                    break
                elif element['primary'].lower() == 'bookchapter':
                    inspire_doc_type.append('book chapter')
                    break
                elif element['primary'].lower() == 'book':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'proceedings':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'conferencepaper':
                    inspire_doc_type.append('conference paper')
                    break
                elif element['primary'].lower() == 'note':
                    inspire_doc_type.append('note')
                    break
                elif json.get('publication_info', []):
                    for field in json.get('publication_info', []):
                        if 'page_artid' not in field:
                            inspire_doc_type.append('preprint')
                            break

        inspire_doc_type.extend([s['primary'].lower() for s in
                                 json.get('collections', []) if 'primary'
                                 in s and s['primary'] is not None and
                                 s['primary'].lower() in
                                 ('review', 'lectures')])
    json['facet_inspire_doc_type'] = inspire_doc_type
