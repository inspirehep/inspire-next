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

from __future__ import absolute_import, division, print_function

import sys

from inspirehep.modules.records.serializers.impactgraph_serializer import (
    ImpactGraphSerializer,
)


def test_impact_graph_serializer_does_not_raise_maximum_recursion_error(app):
    serializer = ImpactGraphSerializer()
    record = {
        'control_number': 111,
        'earliest_date': '1993-02-02',
        'references': [
            {'recid': 4328} for _ in range(sys.getrecursionlimit() + 1)
        ]
    }

    serializer.serialize(111, record)
