# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""Schema for parsing literature records."""

from __future__ import absolute_import, division, print_function

from pybtex.database import Entry, Person
from ..fields_export import get_authors_with_role, extractor, bibtex_type_and_fields
from inspire_utils.record import get_value
from inspirehep.modules.records.json_ref_loader import replace_refs


class PybtexSchema(object):
    def load(self, json):
        """
        Args:
            json: literature record from API

        Returns:
            Pybtex Entity representing the record
        """
        json = replace_refs(json, 'es')
        doc_type, fields = bibtex_type_and_fields(json)
        texkey = unicode(get_value(json, 'texkeys[0]'))

        template_data = []

        for field in fields:
            if field in extractor.store:
                field_value = extractor.store[field](json, doc_type)
                if field_value:
                    template_data.append(
                        (field, unicode(field_value))
                    )
            elif json.get(field):
                template_data.append(
                    (field, unicode(json[field]))
                )

        # Note: human-authors are put in `persons' dict, corporate author will be passed as a field in template data.
        data = (texkey, Entry(doc_type, template_data, persons={
            'author': [Person(x) for x in get_authors_with_role(json.get('authors', []), 'author')],
            'editor': [Person(x) for x in get_authors_with_role(json.get('authors', []), 'editor')]
        }))
        return data
