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

"""Builds an ORCID work record."""

from __future__ import absolute_import, division, print_function

from six import text_type

from lxml import etree
from lxml.builder import ElementMaker

_NAMESPACES = {
    'work': 'http://www.orcid.org/ns/work',
    'common': 'http://www.orcid.org/ns/common'
}

_WORK = ElementMaker(namespace=_NAMESPACES['work'], nsmap=_NAMESPACES)
_COMMON = ElementMaker(namespace=_NAMESPACES['common'], nsmap=_NAMESPACES)

_ELEMENT_MAKERS = {
    'work': _WORK,
    'common': _COMMON
}


class OrcidBuilder(object):
    """Class used to build ORCID-compatible work records in JSON."""

    def __init__(self):
        self.record = _WORK.work()

    def get_xml(self):
        """Get an XML record.

        Returns:
            lxml.etree._Element: ORCID work record compatible with API v2.0
        """
        return self.record

    def __str__(self):
        """Get a string-serialized XML respresentation of a record.

        Returns:
            string: ORCID work record as an XML string
        """
        return etree.tostring(self.get_xml())

    def add_title(self, title, subtitle=None, translated_title=None):
        """Set a title of the work, and optionaly a subtitle.

        Args:
            title (string): title of the work
            subtitle (string): subtitle of the work
            translated_title (Tuple[string, string]): tuple consiting of the translated title and its language code
        """
        title_field = _WORK.title(_COMMON.title(title))

        if subtitle:
            title_field.append(_COMMON.subtitle(subtitle))

        if translated_title:
            attributes = {'language-code': translated_title[1]}
            title_field.append(_COMMON('translated-title', translated_title[0], **attributes))

        self.record.append(title_field)

    def add_type(self, work_type):
        """Add a work type.

        Args:
            work_type (string): type of work, see: https://git.io/vdKXv#L118-L155
        """
        self.record.append(_WORK.type(work_type))

    def add_url(self, url):
        """Add a url.

        Args:
            url (string): alternative url of the record
        """
        self.record.append(_WORK.url(url))

    def add_publication_date(self, partial_date):
        """Set publication date field.

        Args:
            partial_date (inspire_utils.date.PartialDate): publication date
        """
        publication_date = _COMMON('publication-date')

        publication_date.append(_COMMON.year('{:04d}'.format(partial_date.year)))

        if partial_date.month:
            publication_date.append(_COMMON.month('{:02d}'.format(partial_date.month)))

        if partial_date.day:
            publication_date.append(_COMMON.day('{:02d}'.format(partial_date.day)))

        self.record.append(publication_date)

    def add_country(self, country_code):
        """Set country if the ORCID record.

        Args:
            country_code (string): ISO ALPHA-2 country code
        """
        self.record.append(_COMMON.country(country_code.upper()))

    def add_contributor(self, credit_name, role='author', orcid=None, email=None):
        """Adds a contributor entry to the record.

        Args:
            credit_name (string): contributor's name
            orcid (string): ORCID identifier string
            role (string): role, see `OrcidBuilder._make_contributor_field`
            email (string): contributor's email address
        """
        contributors = self._get_or_make_field(self.record, 'work:contributors')
        contributor = self._make_contributor_field(credit_name, role, orcid, email, not len(contributors))
        contributors.append(contributor)

    def add_external_id(self, type, value, url=None, relationship=None):
        """Add external identifier to the record.

        Args:
            type (string): type of external ID (doi, etc.)
            value (string): the identifier itself
            url (string): URL for the resource
            relationship (string): either "part-of" or "self", optional, see `OrcidBuilder._make_external_id_field`
        """
        external_ids_field = self._get_or_make_field(self.record, 'common:external-ids')
        external_ids_field.append(self._make_external_id_field(type, value, url, relationship))

    def add_doi(self, value, relationship=None):
        """Add DOI to the record.

        Args:
            value (string): the identifier itself
            relationship (string): either "part-of" or "self", optional, see `OrcidBuilder._make_external_id_field`
        """
        self.add_external_id('doi', value, 'https://doi.org/{}'.format(value), relationship)

    def add_arxiv(self, value, relationship=None):
        """Add arXiv identifier to the record.

        Args:
            value (string): the identifier itself
            relationship (string): either "part-of" or "self", optional, see `OrcidBuilder._make_external_id_field`
        """
        self.add_external_id('arxiv', value, 'http://arxiv.org/abs/{}'.format(value), relationship)

    def add_citation(self, _type, value):
        """Add a citation string.

        Args:
            _type (string): citation type, one of: https://git.io/vdKXv#L313-L321
            value (string): citation string for the provided citation type
        """
        self.record.append(
            _WORK.citation(
                _WORK('citation-type', _type),
                _WORK('citation-value', value)
            )
        )

    def add_journal_title(self, journal_title):
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
        self.record.append(_WORK('journal-title', journal_title))

    def set_visibility(self, visibility):
        """Set visibility setting on ORCID.

        Can only be set during record creation.

        Args:
            visibility (string): one of (private, limited, registered-only, public), see https://git.io/vdKXt#L904-L937
        """
        self.record.attrib['visibility'] = visibility

    def set_put_code(self, put_code):
        """Set the put-code of an ORCID record, to update existing one.

        Args:
            put_code (string | integer): a number, being a put code
        """
        self.record.attrib['put-code'] = text_type(put_code)

    def _make_contributor_field(self, credit_name, role, orcid, email, first):
        """
        Args:
            credit_name (string): contributor's name
            orcid (string): ORCID identifier string
            role (string): role, see https://git.io/vdKXv#L235-L245
            email (string): contributor's email address
            first (bool): is mentioned first on the list of authors

        Returns:
            lxml.etree._Element: contributor field
        """

        contributor_attributes = _WORK(
            'contributor-attributes', _WORK('contributor-sequence', 'first' if first else 'additional')
        )

        if role:
            contributor_attributes.append(_WORK('contributor-role', role))

        contributor = _WORK('contributor')

        if orcid:
            contributor.append(self._make_contributor_orcid_field(orcid))

        contributor.append(_WORK('credit-name', credit_name))

        if email:
            contributor.append(_WORK('contributor-email', email))

        contributor.append(contributor_attributes)

        return contributor

    def _make_external_id_field(self, type, value, url, relationship):
        """
        Args:
            type (string): type of external ID (doi, issn, etc.)
            value (string): the identifier itself
            url (string): URL for the resource
            relationship (string): either "part-of" or "self", optional, see https://git.io/vdKXt#L1603-L1604

        Returns:
            lxml.etree._Element: ORCID-compatible external ID field
        """
        external_id_field = _COMMON(
            'external-id',
            _COMMON('external-id-type', type),
            _COMMON('external-id-value', value)
        )

        if url:
            external_id_field.append(_COMMON('external-id-url', url))

        if relationship:
            external_id_field.append(_COMMON('external-id-relationship', relationship))

        return external_id_field

    def _make_contributor_orcid_field(self, reference):
        """Generate a contributor-orcid field.

        Args:
            reference (string): ORCID identifier

        Returns:
            lxml.etree._Element: contributor-orcid field
        """
        return _COMMON(
            'contributor-orcid',
            _COMMON.uri('http://orcid.org/{}'.format(reference)),
            _COMMON.path(reference),
            _COMMON.host('orcid.org')
        )

    def _get_or_make_field(self, root, field_tag):
        """Return existing ``field_tag`` element in ``root`` or add and return a new one.

        Args:
            root (lxml.etree._Element): root element to search the tag in
            field_tag (string): XML tag, including the namespace

        Returns:
            lxml.etree._Element: new or existing ``field_tag`` element
        """
        namespace, relative_tag = tuple(field_tag.split(':'))
        element_maker = _ELEMENT_MAKERS[namespace]
        try:
            field = root.xpath('/*/{}'.format(field_tag), namespaces=_NAMESPACES)[0]
        except IndexError:
            field = element_maker(relative_tag)
            root.append(field)
        return field
