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

"""CV_format_html serializer for records."""

from __future__ import absolute_import, division, print_function

from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text


class CVFORMATHTMLSerializer(object):
    """CV_format_html serializer for records."""

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single cv_format_html from a record.
        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for the link generation,
        which are added to the response.
        """
        return Cv_latex_html_text(record, 'cv_latex_html', '<br/>').format()

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """Serialize a search result.
        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        records = []
        for hit in search_result['hits']['hits']:
            records.append(Cv_latex_html_text(hit['_source'],
                                              'cv_latex_html',
                                              '<br/>').format())

        return "\n".join(records)
