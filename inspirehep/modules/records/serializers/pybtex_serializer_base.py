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

    def __init__(self, schema, writer):
        self.schema = schema
        self.writer = writer

    def create_bibliography_entry(self, record):
        """Get a texkey and bibliography entry for an inspire record.

        Use the schema in ``self.schema`` to create a Pybtex bibliography entry
        and retrieve respective texkey from a ``record``.

        Args:
            record: A literature record.

        Returns:
            tuple: bibliography entry as a (texkey, pybtex_entry) tuple.
        """
        bibtex_schema = self.schema
        data = bibtex_schema.load(record)
        return data

    def create_bibliography(self, record_list):
        """Create a pybtex bibliography from individual entries.

        Args:
            record_list: A list of records of the bibliography.

        Returns:
            str: a serialized bibliography.
        """
        bib_dict = {}
        for record in record_list:
            texkey, entries = self.create_bibliography_entry(record)
            bib_dict[texkey] = entries

        bib_data = BibliographyData(bib_dict)
        return self.writer.to_string(bib_data)

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single Bibtex record.

        Args:
            pid: Persistent identifier instance.
            record: Record instance.
            links_factory: Factory function for the link generation, which are added to the response.

        Returns:
            str: single serialized Bibtex record
        """
        return self.create_bibliography([record])

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """Serialize search result(s).

        Args:
            pid_fetcher: Persistent identifier fetcher.
            search_result: Elasticsearch search result.
            links: Dictionary of links to add to response.

        Returns:
            str: serialized search result(s)
        """
        records = [hit['_source'] for hit in search_result['hits']['hits']]
        return self.create_bibliography(records)
