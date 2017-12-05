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

"""MARCXML serializer."""

from __future__ import absolute_import, division, print_function

from inspire_dojson import record2marcxml

MARCXML_TEMPLATE = '''\
<?xml version="1.0" encoding="UTF-8" ?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
{}
</collection>
'''


class MARCXMLSerializer(object):

    """MARCXML serializer."""

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record as MARCXML."""
        return MARCXML_TEMPLATE.format(record2marcxml(record))

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize a search result as MARCXML."""
        result = [record2marcxml(el['_source']) for el in search_result['hits']['hits']]
        return MARCXML_TEMPLATE.format(''.join(result))
