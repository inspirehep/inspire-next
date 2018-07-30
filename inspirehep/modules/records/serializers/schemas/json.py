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

"""Marshmallow JSON schema."""

from __future__ import absolute_import, division, print_function

from inspire_dojson.utils import get_recid_from_ref, strip_empty_values
from inspire_utils.helpers import force_list
from marshmallow import Schema, fields, missing, pre_dump, post_dump

from inspirehep.modules.records.utils import get_linked_records_in_field

from .common import IsbnSchemaV1, ThesisInfoSchemaV1, ConferenceInfoItemSchemaV1


class RecordMetadataSchemaV1(Schema):
    _collections = fields.Raw()
    abstracts = fields.Raw()
    accelerator_experiments = fields.Raw()
    acquisition_source = fields.Raw()
    arxiv_eprints = fields.Raw()
    book_series = fields.Raw()
    # citeable = fields.Raw()
    collaborations = fields.Raw()
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
    date = fields.Raw()
    # deleted = fields.Raw()
    # deleted_records = fields.Raw()
    document_type = fields.Raw()
    # documents = fields.Raw()
    dois = fields.Raw()
    # editions = fields.Raw()
    # energy_ranges = fields.Raw()
    external_system_identifiers = fields.Raw()
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
    number_of_authors = fields.Raw()
    number_of_pages = fields.Raw()
    number_of_references = fields.Raw()
    persistent_identifiers = fields.Raw()
    preprint_date = fields.Raw()
    # public_notes = fields.Raw()
    publication_info = fields.Raw()
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

    @post_dump
    def strip_empty(self, data):
        return strip_empty_values(data)


class RecordSchemaJSONUIV1(Schema):
    """Schema for record UI."""

    id = fields.Integer(attribute='pid.pid_value')
    metadata = fields.Nested(RecordMetadataSchemaV1, dump_only=True)
    display = fields.Raw()
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()


class MetadataAuthorsSchemaV1(Schema):

    authors = fields.Raw(dump_only=True)
    collaborations = fields.Raw(dump_only=True)


class AuthorsSchemaJSONUIV1(RecordSchemaJSONUIV1):
    """Schema for literature authors."""

    metadata = fields.Nested(MetadataAuthorsSchemaV1, dump_only=True)


class MetadataReferencesSchemaItemV1(Schema):
    arxiv_eprints = fields.List(fields.Dict())
    authors = fields.Method('get_authors')
    collaborations = fields.List(fields.Dict())
    control_number = fields.Int()
    dois = fields.List(fields.Dict())
    external_system_identifiers = fields.List(fields.Dict())
    label = fields.String()
    publication_info = fields.List(fields.Dict())
    titles = fields.List(fields.Dict())
    urls = fields.List(fields.Dict())

    def get_authors(self, data):
        authors = data.get('authors', [])
        return authors[:10] or missing


class MetadataReferencesSchemaUIV1(Schema):
    references = fields.Nested(
        MetadataReferencesSchemaItemV1, many=True, dump_only=True)


class ReferencesSchemaJSONUIV1(RecordSchemaJSONUIV1):
    """Schema for references."""
    metadata = fields.Nested(MetadataReferencesSchemaUIV1, dump_only=True)

    @pre_dump
    def processed_refs(self, data):
        resolved = []
        references = data['metadata'].get('references')
        if not references:
            data['metadata']['references'] = []
            return data

        reference_records = self.resolve_records(data)
        for reference in references:
            if 'record' in reference:
                reference_record_id = get_recid_from_ref(
                    reference.get('record'))
                reference_record = reference_records.get(
                    reference_record_id)
                reference = self.resolve_record(reference, reference_record)
            else:
                reference = self.format_reference(reference)

            if reference:
                resolved.append(reference)

        data['metadata']['references'] = resolved
        return data

    def format_reference(self, reference):
        reference.update(reference.get('reference', {}))
        reference.pop('reference', None)
        reference.update({
            'publication_info': self.prepare_publication_info(
                reference.get('publication_info', {})),
            'arxiv_eprints': self.prepare_arxiv_eprint(
                reference.get('arxiv_eprint')),
            'collaborations': self.prepare_collaborations(
                reference.get('collaborations', [])),
            'dois': self.prepare_dois(reference.get('dois', [])),
            'titles': self.prepare_titles(reference.get('title', [])),
        })
        reference = strip_empty_values(reference)
        return self.only_meaningful_data(reference)

    def resolve_record(self, reference, reference_record):
        if reference_record:
            return reference_record
        return self.format_reference(reference)

    @staticmethod
    def resolve_records(data):
        resolved_records = get_linked_records_in_field(
            data, 'metadata.references.record')
        return {
            record['control_number']: record
            for record in resolved_records
        }

    @staticmethod
    def only_meaningful_data(reference):
        if any(key in reference for
               key in ['titles', 'authors', 'publication_info']):
            return reference

    @staticmethod
    def prepare_publication_info(publication_info):
        return force_list(
            publication_info
            if {'journal_title', 'pubinfo_freetext'}.issubset(publication_info.keys())
            else None
        )

    @staticmethod
    def prepare_arxiv_eprint(arxiv_eprint):
        if not arxiv_eprint:
            return
        return [{'value': arxiv_eprint}]

    @staticmethod
    def prepare_titles(titles):
        return force_list(titles)

    @staticmethod
    def prepare_dois(dois):
        return [{'value': doi} for doi in dois]

    @staticmethod
    def prepare_collaborations(collaborations):
        return [
            {'value': collaboration} for collaboration in collaborations]
