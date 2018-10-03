# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from marshmallow import Schema, pre_dump, fields, missing
from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.helpers import force_list

from inspirehep.modules.records.serializers.fields import ListWithLimit, NestedWithoutEmptyObjects
from inspirehep.modules.records.utils import get_linked_records_in_field
from inspire_utils.record import get_value

from .author import AuthorSchemaV1
from .publication_info_item import PublicationInfoItemSchemaV1


class ReferenceItemSchemaV1(Schema):
    authors = ListWithLimit(
        NestedWithoutEmptyObjects(AuthorSchemaV1, dump_only=True, default=[]), limit=10)
    control_number = fields.Raw()
    label = fields.Raw()
    urls = fields.Raw()
    publication_info = fields.List(
        NestedWithoutEmptyObjects(PublicationInfoItemSchemaV1, dump_only=True))
    titles = fields.Method('get_titles')
    misc = fields.Method('get_misc')
    arxiv_eprint = fields.Method('get_arxiv_eprints')
    dois = fields.Method('get_dois')

    @pre_dump(pass_many=True)
    def filter_references(self, data, many):
        reference_records = self.get_resolved_references_by_control_number(data)

        if not many:
            return self.get_resolved_reference(data, reference_records)

        references = []
        for reference in data:
            resolved_reference = self.get_resolved_reference(reference, reference_records)
            references.append(resolved_reference)
        return references

    def get_resolved_reference(self, data, reference_records):
        reference_record_id = self.get_reference_record_id(data)
        reference_record = reference_records.get(reference_record_id)
        reference = self.get_reference_or_linked_reference_with_label(data, reference_record)
        return reference

    def get_reference_record_id(self, data):
        return get_recid_from_ref(data.get('record'))

    def get_resolved_references_by_control_number(self, data):
        data = force_list(data)
        resolved_records = get_linked_records_in_field(
            {'references': data}, 'references.record')
        return {
            record['control_number']: record
            for record in resolved_records
        }

    def get_reference_or_linked_reference_with_label(self, data, reference_record):
        if reference_record:
            reference_record.update({
                'label': data.get('reference', {}).get('label', missing)
            })
            return reference_record
        return data.get('reference')

    def get_titles(self, data):
        title = data.pop('title', None)
        if title:
            data['titles'] = force_list(title)
        return data.get('titles', missing)

    def get_dois(self, data):
        dois = data.get('dois', None)
        control_number = data.get('control_number')
        if dois and not control_number:
            data['dois'] = force_list({'value': get_value(data, 'dois[0]', default=missing)})
        elif dois:
            data['dois'] = force_list({'value': get_value(data, 'dois[0].value', default=missing)})
        return data.get('dois', missing)

    def get_arxiv_eprints(self, data):
        arxiv_eprint = data.pop('arxiv_eprint', None)
        arxiv_eprints = data.get('arxiv_eprints')
        if arxiv_eprint:
            data['arxiv_eprint'] = force_list({'value': arxiv_eprint})
        elif arxiv_eprints:
            data['arxiv_eprint'] = force_list({'value': get_value(data, 'arxiv_eprints[0].value', default=missing)})
        data.pop('arxiv_eprints', None)
        return data.get('arxiv_eprint', missing)

    def get_misc(self, data):
        titles = data.get('titles')
        title = data.get('title')
        misc = data.get('misc')
        if not title and not titles and misc:
            return misc[0]
        return missing
