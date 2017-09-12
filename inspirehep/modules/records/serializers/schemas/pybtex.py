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

"""Marshmallow JSON schema for a literature entry."""

from __future__ import absolute_import, division, print_function

from marshmallow import Schema, post_load
from marshmallow.fields import Str, List, Nested, Int
from pybtex.database import Entry, Person

from inspirehep.modules.records.serializers.fields_export import bibtex_type_and_fields, extractor, get_authors_with_role
from .helper_fields import First, FromRecordID, PartialDate


class AuthorSchema(Schema):
    """Schema for authors in Bibtex references."""
    full_name = Str()
    inspire_roles = List(Str())


class TitleSchema(Schema):
    """Schema for titles in Bibtex references."""
    title = Str()

    @post_load
    def make_title(self, data):
        return data['title']


class ConferenceAddressSchema(Schema):
    postal_address = First(Str())

    @post_load
    def make_address(self, data):
        return data['postal_address']


class ConferenceSchema(Schema):
    cnum = Str()
    address = First(Nested(ConferenceAddressSchema))
    title = First(Nested(TitleSchema), load_from='titles')


class PublicationInfoSchema(Schema):
    """Schema to represent publication_info."""
    journal = Str(load_from='journal_title')
    volume = Str(load_from='journal_volume')
    year = Int()
    number = Str(load_from='journal_issue')
    page_start = Str()
    page_end = Str()
    conference = FromRecordID(ConferenceSchema, 'con', load_from='conference_recid')


class InstitutionSchema(Schema):
    """Schema for representing institutions."""
    name = Str()

    @post_load
    def make_institution(self, data):
        return data['name']


class ThesisSchema(Schema):
    """Schema for theses in Bibtex references."""
    degree_type = Str()
    institutions = List(Nested(InstitutionSchema))
    date = PartialDate()


class ValueListSchema(Schema):
    """Schema to represent extract value from an object of the form {value : data}."""
    value = Str()

    @post_load
    def make_value_list(self, obj):
        return obj['value']


class ArXivEprintSchema(Schema):
    """Schema to represent archiv entry objects."""
    categories = List(Str())
    value = Str()


class ImprintsSchema(Schema):
    """Schema to represent imprints object."""
    date = PartialDate()
    place = Str()
    publisher = Str()


class PybtexSchema(Schema):
    """Schema for Bibtex references."""
    key = Int(load_from='self_recid')
    texkey = First(Str(), load_from='texkeys')
    author = List(Nested(AuthorSchema), load_from='authors')
    title = First(Nested(TitleSchema), load_from='titles')
    document_type = List(Str())
    publication_info = First(Nested(PublicationInfoSchema))  # TODO: find the best entry
    doi = First(Nested(ValueListSchema), load_from='dois')
    arxiv_eprints = First(Nested(ArXivEprintSchema))
    reportNumber = List(Nested(ValueListSchema), load_from='report_numbers')
    preprint_date = PartialDate()
    earliest_date = PartialDate()
    corporate_author = List(Str(), load_from='corporate_authors')
    collaboration = First(Nested(ValueListSchema), load_from='collaborations')
    url = First(Nested(ValueListSchema), load_from='urls')
    thesis_info = Nested(ThesisSchema)

    @post_load
    def make_bibtex(self, data):
        """
        Serializes the record to an Entity object provided by Pybtex.
        :param data: Data excteracted by using the schema.
        :return: Pybtex Entity representing the record.
        """
        doc_type, fields = bibtex_type_and_fields(data)
        texkey = str(data.get('texkey', ''))

        template_data = [
            ('key', str(data.get('key')))
        ]

        for field in fields:
            if field in extractor.store:
                field_value = extractor.store[field](data, doc_type)
                if field_value:
                    template_data.append(
                        (field, unicode(field_value))
                    )
            elif data.get(field):
                template_data.append(
                    (field, unicode(data[field]))
                )

        # Note: human-authors are put in `persons' dict, corporate author will be passed as a field in template data.
        return texkey, Entry(doc_type, template_data, persons={
            'author': [Person(x) for x in get_authors_with_role(data.get('author', []), 'author')],
            'editor': [Person(x) for x in get_authors_with_role(data.get('author', []), 'editor')]
        })
