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

"""
Handle conversion from INSPIRE records to ORCID.
"""

from __future__ import absolute_import, division, print_function
from inspire_utils.record import get_value
from inspire_utils.date import PartialDate
from .builder import OrcidBuilder
from flask import current_app
import re
from inspirehep.modules.hal.utils import (
    get_journal_title,
    get_publication_date,
    get_conference_title,
    get_conference_record,
    get_conference_country,
    get_doi,
)


class OrcidConverter(object):
    """Coverter for the Orcid format."""

    # Maps INSPIRE author roles to ORCID contributor roles
    # for full list see: https://git.io/vdKXv#L235-L245
    INSPIRE_TO_ORCID_ROLES_MAP = {
        'author': 'author',
        'editor': 'editor',
        'supervisor': None
    }

    # Maps INSPIRE document type to ORCID work types
    # for full list see: https://git.io/vdKXv#L118-L155
    INSPIRE_DOCTYPE_TO_ORCID_TYPE = {
        'article': 'journal-article',
        'book': 'book',
        'book chapter': 'book-chapter',
        'conference paper': 'conference-paper',
        'note': 'other',
        'proceedings': 'edited-book',
        'report': 'report',
        'thesis': 'dissertation',
    }

    def __init__(self, record, put_code=None, visibility=None):
        """Constructor.

        Args:
            record (dict): a record.
        """
        self.record = record
        self.put_code = put_code
        self.visibility = visibility

    def get_xml(self):
        """Create an ORCID XML representation of the record.

        Returns:
            lxml.etree._Element: ORCID XML work record
        """
        builder = OrcidBuilder()

        # Set attributes
        if self.visibility:
            builder.set_visibility(self.visibility)

        if self.put_code:
            builder.set_put_code(self.put_code)

        # Add a title
        if self.title:
            builder.add_title(self.title, self.subtitle, self.title_translation)

        # Add a journal title
        containing_publication_title = self.journal_title or self.conference_title or self.book_series_title
        if containing_publication_title:
            builder.add_journal_title(containing_publication_title)

        # TODO: Add a citation

        # Add a type
        builder.add_type(self.orcid_work_type)

        # Add a publication date
        if self.publication_date:
            builder.add_publication_date(self.publication_date)

        # Add external IDs
        if self.doi:
            builder.add_doi(self.doi, 'self')

        if self.arxiv_eprint:
            builder.add_arxiv(self.arxiv_eprint, 'self')

        for isbn in get_value(self.record, 'isbns.value', []):
            builder.add_external_id('isbn', isbn)

        # Add URL pointing to INSPIRE to ORCID
        server_name = current_app.config.get('SERVER_NAME')
        if not re.match('^https?://', server_name):
            server_name = 'http://{}'.format(server_name)
        builder.add_url('{}/record/{}'.format(server_name, self.recid))

        # Add authors/editors/etc. to the ORCID record
        for author in self.record.get('authors', []):
            orcid_role = self.orcid_role_for_inspire_author(author)
            if not orcid_role:
                continue
            person_orcid = self.orcid_for_inspire_author(author)
            email = get_value(author, 'emails[0]')
            builder.add_contributor(author['full_name'], orcid_role, person_orcid, email)

        # Add a country (only available for conferences)
        if self.conference_country:
            builder.add_country(self.conference_country)

        return builder.get_xml()

    def orcid_role_for_inspire_author(self, author):
        """ORCID role for an INSPIRE author field.

        Args:
            author (dict): an author field from INSPIRE literature record

        Returns:
            string: ORCID role of a person
        """
        inspire_roles = sorted(get_value(author, 'inspire_roles', ['author']))
        if inspire_roles:
            return self.INSPIRE_TO_ORCID_ROLES_MAP[inspire_roles[0]]

    def orcid_for_inspire_author(self, author):
        """ORCID identifier for an INSPIRE author field.

        Args:
            author (dict): an author field from INSPIRE literature record

        Returns:
            string: ORCID identifier of an author, if available
        """
        ids = author.get('ids', [])
        for id in ids:
            if id['schema'] == 'ORCID':
                return id['value']

    @property
    def orcid_work_type(self):
        """Get record's ORCID work type."""
        inspire_doc_type = get_value(self.record, 'document_type[0]')
        return self.INSPIRE_DOCTYPE_TO_ORCID_TYPE[inspire_doc_type]

    @property
    def title(self):
        """Get record title."""
        return get_value(self.record, 'titles[0].title')

    @property
    def subtitle(self):
        """Get record subtitle."""
        return get_value(self.record, 'titles[0].subtitle')

    @property
    def journal_title(self):
        """Get record's journal title."""
        return get_journal_title(self.record)

    @property
    def conference_title(self):
        """Get record's conference title."""
        try:
            conference_record = get_conference_record(self.record)
            return get_conference_title(conference_record)
        except TypeError:  # TODO: Fixed in the bibtex PR
            pass

    @property
    def book_series_title(self):
        """Get record's book series title."""
        return get_value(self.record, 'book_series[0].title')

    @property
    def conference_country(self):
        """Get conference record country."""
        return get_conference_country(self.record)

    @property
    def doi(self):
        """Get DOI of a record."""
        return get_doi(self.record)

    @property
    def arxiv_eprint(self):
        """Get arXiv ID of a record."""
        return get_value(self.record, 'arxiv_eprints.value[0]')

    @property
    def recid(self):
        """Get INSPIRE record ID."""
        return self.record['self_recid']

    @property
    def title_translation(self):
        """Translated title.

        Returns:
            Tuple[string, string]: translated title and the language code of the translation, if available
        """
        title = get_value(self.record, 'title_translations[0].title')
        language_code = get_value(self.record, 'title_translations[0].language')
        if title and language_code:
            return title, language_code

    @property
    def publication_date(self):
        """(Partial) date of publication.

        Returns:
            partial_date (inspire_utils.date.PartialDate): publication date
        """
        try:
            return PartialDate.loads(get_value(self.record, 'imprints.date[0]') or get_publication_date(self.record))
        except ValueError:
            return None
