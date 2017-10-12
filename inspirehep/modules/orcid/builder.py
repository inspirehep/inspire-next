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
Builds an ORCID work record.
"""

from __future__ import absolute_import, division, print_function


class OrcidBuilder(object):
    """
    Class used to build ORCID-compatible work records in JSON.
    """
    def __init__(self, source=None):
        """
        Args:
            source (dict): Quoting ORCID v2.0 work schema: "Client application (member organization's system) or user
                that created the item. The identifier for the source may be either an ORCID iD (representing individuals
                and legacy client applications) or a Client ID (representing all newer client applications)". See:
                https://git.io/vdKXt#L114-L118
        """
        self.record = dict()

        if source:
            self.record['source'] = source

    def get_json(self):
        """
        Returns:
            dict: ORCID work record compatible with API v2.0
        """
        return self.record

    def set_title(self, title, subtitle=None, translated_title=None):
        """
        Set a title of the work, and optionaly a subtitle.

        Args:
            title (string): title of the work
            subtitle (string): subtitle of the work
            translated_title (Tuple[string, string]): tuple consiting of the translated title and its language code
        """
        title_field = {
            'title': {'value': title}
        }

        if subtitle:
            title_field['subtitle'] = {
                'value': subtitle
            }

        if translated_title:
            title_field['translated-title'] = {
                'value': translated_title[0],
                'language-code': translated_title[1],
            }

        self.record['title'] = title_field

    def set_type(self, work_type):
        """
        Args:
            work_type (string): type of work, see: https://git.io/vdKXv#L118-L155
        """
        self.record['type'] = work_type

    def set_url(self, url):
        """
        Args:
            url (string): alternative url of the record
        """
        self.record['url'] = {
            'value': url
        }

    def set_publication_date(self, partial_date, media_type=None):
        """
        Set publication date field.

        Args:
            partial_date (inspire_utils.date.PartialDate): publication date
            media_type (string): publication medium type, one of ("print", "online", "other"), optional, see:
                https://git.io/vdKXt#L958-L960
        """
        publication_date = {
            'year': {
                'value': '{:04d}'.format(partial_date.year)
            }
        }

        if partial_date.month:
            publication_date['month'] = {'value': '{:02d}'.format(partial_date.month)}

        if partial_date.day:
            publication_date['day'] = {'value': '{:02d}'.format(partial_date.day)}

        if media_type:
            publication_date['media-type'] = media_type

        self.record['publication-date'] = publication_date

    def set_country(self, country_code):
        """Set country if the ORCID record.

        Args:
            country_code (string): ISO ALPHA-2 country code
        """
        self.record['country'] = {
            'value': country_code
        }

    def add_contributor(self, credit_name, role='AUTHOR', orcid=None, email=None):
        """Adds a contributor entry to the record.

        Args:
            credit_name (string): contributor's name
            orcid (string): ORCID identifier string
            role (string): role, see `OrcidBuilder._make_contributor_field`
            email (string): contributor's email address
        """
        if 'contributors' not in self.record:
            self.record['contributors'] = {'contributor': [
                self._make_contributor_field(credit_name, role, orcid, email, first=True)
            ]}
        else:
            self.record['contributors']['contributor'].append(
                self._make_contributor_field(credit_name, role, orcid, email, first=False)
            )

    def add_external_id(self, type, value, url=None, relationship=None):
        """Add external identifier to the record.

        Args:
            type (string): type of external ID (DOI, etc.)
            value (string): the identifier itself
            url (string): URL for the resource
            relationship (string): either "part-of" or "self", optional, see `OrcidBuilder._make_external_id_field`
        """
        if 'external-ids' not in self.record:
            self.record['external-ids'] = {'external-id': [
                self._make_external_id_field(type, value, url, relationship)
            ]}
        else:
            self.record['external-ids']['external-id'].append(
                self._make_external_id_field(type, value, url, relationship)
            )

    def add_doi(self, value, relationship=None):
        self.add_external_id('doi', value, 'http://dx.doi.org/{}'.format(value), relationship)

    def add_arxiv(self, value, relationship=None):
        self.add_external_id('arxiv', value, 'http://arxiv.org/abs/{}'.format(value), relationship)

    def set_citation(self, type, value):
        """Adds a citation string.

        Args:
            type (string): citation type, one of: https://git.io/vdKXv#L313-L321
            value (string): citation string for the provided citation type
        """
        self.record['citation'] = {
            'citation-type': type,
            'citation-value': value,
        }

    def set_journal_title(self, journal_title):
        """Set title of the publication containing the record.

        Args:
            journal_title (string): Title of publication containing the record.

                After ORCID v2.0 schema (https://git.io/vdKXv#L268-L280):
                "The title of the publication or group under which the work was published.
                - If a journal, include the journal title of the work.
                - If a book chapter, use the book title.
                - If a translation or a manual, use the series title.
                - If a dictionary entry, use the dictionary title.
                - If a conference poster, abstract or paper, use the conference name."
        """
        self.record['journal-title'] = {
            'value': journal_title
        }

    def set_visibility(self, visibility):
        """Set visibility setting on ORCID.

        Can only be set during record creation.

        Args:
            visibility (string): one of (private, limited, registered-only, public), see https://git.io/vdKXt#L904-L937
        """
        self.record['visibility'] = visibility

    def _make_contributor_field(self, credit_name, role, orcid, email, first):
        """
        Args:
            credit_name (string): contributor's name
            orcid (string): ORCID identifier string
            role (string): role, see https://git.io/vdKXv#L235-L245
            email (string): contributor's email address
            first (bool): is mentioned first on the list of authors

        Returns:
            dict: contributor field
        """
        contributor = {
            'credit-name': {
                'value': credit_name
            },
            'contributor-attributes': {
                'contributor-sequence': 'first' if first else 'additional',
                'contributor-role': role,
            }
        }

        if orcid:
            contributor['contributor-orcid'] = self._make_reference_field(orcid)

        if email:
            contributor['contributor-email'] = {
                'value': email
            }

        return contributor

    def _make_external_id_field(self, type, value, url, relationship):
        """
        Args:
            type (string): type of external ID (doi, issn, etc.)
            value (string): the identifier itself
            url (string): URL for the resource
            relationship (string): either "part-of" or "self", optional, see https://git.io/vdKXt#L1603-L1604

        Returns:
            dict: ORCID-compatible external ID field
        """
        external_id = {
            'external-id-type': type,
            'external-id-value': value,
        }

        if url:
            external_id['external-id-url'] = {
                'value': url,
            }

        if relationship:
            external_id['external-id-relationship'] = relationship

        return external_id

    def _make_reference_field(self, reference):
        return {
            'uri': 'http://orcid.org/{}'.format(reference),
            'path': reference,
            'host': 'orcid.org',
        }
