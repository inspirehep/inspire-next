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

"""Tests for Impact Graph API."""

from __future__ import absolute_import, division, print_function

import json


def test_impact_graphs_api(api_client):
    """Test response of impact graph API."""
    result = api_client.get(
        "/literature/712925",
        headers={"Accept": "application/x-impact.graph+json"}
    )

    result = json.loads(result.data)
    assert result['title'] == u'PYTHIA 6.4 Physics and Manual'
    assert result['year'] == u'2006'
    assert len(result['citations']) == 2
