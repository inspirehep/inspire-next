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

"""BibTex serializer for records."""

from __future__ import absolute_import, division, print_function

from pybtex.database import BibliographyData


class PybtexSerializerBase(object):
    """Pybtex serializer for records."""

    def create_bibliography_entry(self, record):
        """
        Args:
            record: A literature record.

        Returns:
            tuple: bibliography entry as a (texkey, pybtex_entry) tuple.
        """
        bibtex_schema = self.get_schema()
        data = bibtex_schema.load(record)
        return data

    def create_bibliography(self, record_list):
        """
        Args:
            record_list: A list of records of the bibliography.

        Returns:
            string: a serialized bibliography.
        """
        bib_dict = {}
        for record in record_list:
            texkey, entries = self.create_bibliography_entry(record)
            bib_dict[texkey] = entries

        bib_data = BibliographyData(bib_dict)
        return self.get_writer().to_string(bib_data)

    def get_writer(self):
        """
        Note:
            To be implemented by subclasses.

        Returns:
            Pybtex writer class to be used to generate bibliography output.
        """
        raise NotImplementedError()

    def get_schema(self):
        """
        Note:
            To be implemented by subclasses.

        Returns:
            Schema to be used to serialize the bibliography.
        """
        raise NotImplementedError()

    def serialize(self, pid, record, links_factory=None):
        """
        Args:
            pid: Persistent identifier instance.
            record: Record instance.
            links_factory: Factory function for the link generation, which are added to the response.

        Returns:
            string: single serialized Bibtex record
        """
        return self.create_bibliography([record])

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """
        Args:
            pid_fetcher: Persistent identifier fetcher.
            search_result: Elasticsearch search result.
            links: Dictionary of links to add to response.

        Returns:
            string: serialized search result(s)
        """
        records = [hit['_source'] for hit in search_result['hits']['hits']]
        return self.create_bibliography(records)
