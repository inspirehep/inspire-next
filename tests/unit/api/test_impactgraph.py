# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from __future__ import absolute_import, division, print_function

import mock

from inspirehep.modules.records.serializers.impactgraph_serializer import \
    ImpactGraphSerializer


class MockESReturn(object):

    @property
    def hits(self):
        return []


@mock.patch('inspirehep.modules.records.serializers.impactgraph_serializer.get_es_records')
@mock.patch('inspirehep.modules.records.serializers.impactgraph_serializer.LiteratureSearch.execute')
def test_impactgraph_calls_get_es_records_for_references(e, g, app):
    e.return_value = MockESReturn()
    serializer = ImpactGraphSerializer()
    record = {
        'control_number': 123,
        'title': 'Hello world',
        'earliest_date': '1999-01-01',
        'references': [
            {
                'recid': 123
            }
        ]
    }
    with app.app_context():
        serializer.serialize(111, record)

    g.assert_called_with(
        'lit',
        [123],
        _source=['control_number', 'citation_count', 'titles', 'earliest_date']
    )
