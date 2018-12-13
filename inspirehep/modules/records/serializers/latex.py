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

"""Latex serializer for records."""

from __future__ import absolute_import, division, print_function

from invenio_records_rest.serializers.json import MarshmallowMixin, PreprocessorMixin

import jinja2
import os
import pkg_resources


class LatexSerializer(MarshmallowMixin, PreprocessorMixin):
    """Latex serializer for records."""

    def __init__(self, format, **kwargs):
        """Initialize record."""
        self.format = format
        super(LatexSerializer, self).__init__(**kwargs)

    def serialize(self, pid, record, links_factory=None, **kwargs):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for record links.
        """
        data = self.transform_record(pid, record, links_factory, **kwargs)

        return self.latex_template().render(data=data, format=self.format)

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare a record and persistent identifier for serialization."""
        return record

    def latex_template(self):
        latex_jinja_env = jinja2.Environment(
            variable_start_string='\VAR{',
            variable_end_string='}',
            loader=jinja2.FileSystemLoader(os.path.abspath('/'))
        )
        template_path = pkg_resources.resource_filename('inspirehep', 'modules/records/serializers/templates/latex_template.tex')

        template = latex_jinja_env.get_template(template_path)

        return template

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
        records = (self.dump(hit['_source']) for hit in search_result['hits']['hits'])
        templates = [self.latex_template().render(data=data, format=self.format) for data in records]
        return u'\n\n'.join(templates)
