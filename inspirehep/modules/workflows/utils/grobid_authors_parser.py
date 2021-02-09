# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2020 CERN.
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
from urlparse import urljoin

from inspire_schemas.builders import LiteratureBuilder
from parsel import Selector


class GrobidAuthors(object):
    def __init__(self, xml_text):
        if isinstance(xml_text, str):
            xml_text = xml_text.decode('utf-8')
        self._xml = Selector(text=xml_text, type="xml")
        self._xml.remove_namespaces()
        self._parsed_authors = self._xml.xpath("//author")
        self._builder = None

    def __getitem__(self, item):
        return GrobidAuthor(self._parsed_authors[item])

    def __len__(self):
        return len(self._parsed_authors)

    def get(self):
        """yield parsed authors one by one"""
        self._builder = LiteratureBuilder()
        for author in self:
            yield {
                'author': self._builder.make_author(
                    full_name=author.fullname,
                    raw_affiliations=author.raw_affiliations,
                    emails=author.emails,
                ),
                'parsed_affiliations': author.processed_affiliations
            }

    def getall(self):
        """Returns all authors at once as a list"""
        parsed_authors = []
        for author_data in self.get():
            parsed_authors.append(author_data)
        return parsed_authors


class GrobidAuthor(object):
    def __init__(self, author_selector):
        self._author = author_selector

    def _extract(self, source, path, type=None, text=False):
        if type:
            path += "[@type='{type}']".format(type=type)
        if text:
            path += "/text()"
            return source.xpath(path)
        return source.xpath(path)

    def _extract_string(self, source, path, type=None, join_char=u' ', clean=True):
        data = self._extract(source, path, type, text=True).getall()
        if clean:
            data = [text.strip() for text in data]
        return join_char.join(data)

    def _extract_strings_list(self, source, path, type=None, clean=True):
        data = self._extract(source, path, type, text=True).getall()
        if clean:
            return [text.strip() for text in data]
        return data

    def _build_address(self, street, city, post_code, country):
        address_list = [element for element in [street, city, post_code, country] if element]
        address = {"postal_address": ', '.join(address_list)} if address_list else {}
        if city:
            address['cities'] = [city]
        if post_code:
            address['postal_code'] = post_code
        if country:
            address['country'] = country
        return address

    @property
    def names(self):
        return self._extract_string(self._author, "persName/forename")

    @property
    def lastname(self):
        return self._extract_string(self._author, "persName/surname")

    @property
    def fullname(self):
        return u" ".join([self.lastname, self.names])

    @property
    def raw_affiliations(self):
        return self._extract_strings_list(self._author, "affiliation/note", type="raw_affiliation")

    @property
    def processed_affiliations(self):
        affiliations = []
        for affiliation in self._extract(self._author, "affiliation"):
            affiliation_obj = {}
            name = self._extract_string(affiliation, "orgName", type="institution", join_char=', ')
            department = self._extract_strings_list(affiliation, "orgName", type="department")

            street = self._extract_string(affiliation, 'address/addrLine')
            settlement = self._extract_string(affiliation, 'address/settlement')
            post_code = self._extract_string(affiliation, 'address/post_code')
            country = self._extract_string(affiliation, 'address/country')

            address = self._build_address(street, settlement, post_code, country)

            if name:
                affiliation_obj['name'] = name
            if department:
                affiliation_obj['department'] = department
            if address:
                affiliation_obj['address'] = address
            affiliations.append(affiliation_obj)
        return affiliations or None

    @property
    def emails(self):
        return self._author.xpath("email/text()").getall()
