# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Impact Graph serializer for records."""

from __future__ import absolute_import, division, print_function

import json

from inspirehep.utils.record import get_title
from inspirehep.modules.search import LiteratureSearch
from inspirehep.modules.relations.api import LiteratureRelationsSearch


class ImpactGraphSerializer(object):

    """Impact Graph serializer for records."""

    def serialize(self, pid, record, links_factory=None):
        """
        Serialize a single impact graph from a record.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for the link generation,
                              which are added to the response.
        """

        # Get reference and citation info
        summary = LiteratureRelationsSearch.get_impact_graph_summary(
            record['control_number']
        )

        # Add information about current record
        summary['inspire_id'] = record['control_number']
        summary['title'] = get_title(record)
        summary['year'] = record['earliest_date'].split('-')[0]

        return json.dumps(summary)
