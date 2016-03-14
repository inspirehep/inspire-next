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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tests for Impact Graph API."""

import json
import os
import pkg_resources

from invenio.testsuite import InvenioTestCase


class ImpactGraphTests(InvenioTestCase):

    """Tests Impact Graph views"""

    impact_output = json.loads(pkg_resources.resource_string(
        'tests',
        os.path.join(
            'fixtures',
            'test_impact_graph_output.json')
         )
    )

    def test_impact_graph_api(self):
        """Test response of impact graph API."""
        result = self.client.get("/record/api/impactgraph?recid=613135")
        assert result.json == self.impact_output
