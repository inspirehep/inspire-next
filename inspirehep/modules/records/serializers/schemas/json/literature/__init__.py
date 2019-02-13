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

from inspire_dojson.utils import strip_empty_values
from inspire_utils.date import format_date

from marshmallow import Schema, fields, missing, post_dump

from inspirehep.modules.records.serializers.fields import ListWithLimit, NestedWithoutEmptyObjects
from inspirehep.modules.records.serializers.schemas.base import JSONSchemaUIV1

from .common import (  # noqa: F401
    AuthorSchemaV1,
    ConferenceInfoItemSchemaV1,
    DOISchemaV1,
    ExternalSystemIdentifierSchemaV1,
    IsbnSchemaV1,
    PublicationInfoItemSchemaV1,
    ReferenceItemSchemaV1,
    ThesisInfoSchemaV1,
    CitationItemSchemaV1,
    CollaborationWithSuffixSchemaV1,
    CollaborationSchemaV1,
    AcceleratorExperimentSchemaV1
)


class RecordMetadataSchemaV1(Schema):

    _collections = fields.Raw()
    abstracts = fields.Raw()
    accelerator_experiments = fields.Nested(AcceleratorExperimentSchemaV1, dump_only=True, many=True)
    acquisition_source = fields.Raw()
    arxiv_eprints = fields.Raw()
    authors = ListWithLimit(fields.Nested(
        AuthorSchemaV1, dump_only=True), limit=10)
    book_series = fields.Raw()
    # citeable = fields.Raw()
    citation_count = fields.Raw()
    collaborations = fields.List(fields.Nested(CollaborationSchemaV1, dump_only=True), attribute="collaborations")
    collaborations_with_suffix = fields.List(fields.Nested(CollaborationWithSuffixSchemaV1, dump_only=True), attribute="collaborations")
    conference_info = fields.Nested(
        ConferenceInfoItemSchemaV1,
        dump_only=True,
        attribute='publication_info',
        many=True)
    control_number = fields.Raw()
    # copyright = fields.Raw()
    # core = fields.Raw()
    corporate_author = fields.Raw()
    # curated = fields.Raw()
    date = fields.Method('get_formatted_date')
    # deleted = fields.Raw()
    # deleted_records = fields.Raw()
    document_type = fields.Raw()
    # documents = fields.Raw()
    dois = fields.Nested(DOISchemaV1, dump_only=True, many=True)
    # editions = fields.Raw()
    # energy_ranges = fields.Raw()
    external_system_identifiers = fields.Nested(
        ExternalSystemIdentifierSchemaV1, dump_only=True, many=True)
    # figures = fields.Raw()
    # funding_info = fields.Raw()
    imprints = fields.Raw()
    inspire_categories = fields.Raw()
    isbns = fields.List(fields.Nested(IsbnSchemaV1, dump_only=True))
    keywords = fields.Raw()
    languages = fields.Raw()
    # legacy_creation_date = fields.Raw()
    # license = fields.Raw()
    # new_record = fields.Raw()
    number_of_authors = fields.Method('get_number_of_authors')
    number_of_pages = fields.Raw()
    number_of_references = fields.Method('get_number_of_references')
    persistent_identifiers = fields.Raw()
    preprint_date = fields.Raw()
    # public_notes = fields.Raw()
    publication_info = fields.Nested(
        PublicationInfoItemSchemaV1, dump_only=True, many=True)
    # publication_type = fields.Raw()
    # record_affiliations = fields.Raw()
    # refereed = fields.Raw()
    # related_records = fields.Raw()
    report_numbers = fields.Raw()
    # self = fields.Raw()
    texkeys = fields.Raw()
    thesis_info = fields.Nested(ThesisInfoSchemaV1, dump_only=True)
    # title_translations = fields.Raw()
    titles = fields.Raw()
    # urls = fields.Raw()
    # withdrawn = fields.Raw()

    def get_formatted_date(self, data):
        earliest_date = data.get('earliest_date')
        if earliest_date is None:
            return missing
        return format_date(earliest_date)

    def get_number_of_authors(self, data):
        authors = data.get('authors')
        return self.get_len_or_missing(authors)

    def get_number_of_references(self, data):
        number_of_references = data.get('number_of_references')
        if number_of_references is not None:
            return number_of_references

        references = data.get('references')
        return self.get_len_or_missing(references)

    @staticmethod
    def get_len_or_missing(maybe_none_list):
        if maybe_none_list is None:
            return missing
        return len(maybe_none_list)

    @post_dump
    def strip_empty(self, data):
        return strip_empty_values(data)


class LiteratureRecordSchemaJSONUIV1(JSONSchemaUIV1):
    """Schema for record UI."""

    metadata = fields.Nested(RecordMetadataSchemaV1, dump_only=True)


class MetadataAuthorsSchemaV1(Schema):
    authors = NestedWithoutEmptyObjects(
        AuthorSchemaV1, default=[],
        dump_only=True, many=True
    )
    collaborations = fields.Raw(default=[], dump_only=True)


class LiteratureAuthorsSchemaJSONUIV1(JSONSchemaUIV1):
    """Schema for literature authors."""

    metadata = fields.Nested(MetadataAuthorsSchemaV1, dump_only=True)


class MetadataReferencesSchemaUIV1(Schema):
    references = NestedWithoutEmptyObjects(
        ReferenceItemSchemaV1, default=[], many=True, dump_only=True)


class LiteratureReferencesSchemaJSONUIV1(JSONSchemaUIV1):
    """Schema for references."""

    metadata = fields.Nested(MetadataReferencesSchemaUIV1, dump_only=True)
