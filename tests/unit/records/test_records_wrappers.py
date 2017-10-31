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

from inspirehep.modules.records.wrappers import LiteratureRecord


def test_literature_record_external_system_identifiers():
    record = LiteratureRecord({
        'external_system_identifiers': [
            {
                'schema': 'DESY',
                'value': 'D04-00213',
            },
            {
                'schema': 'ADS',
                'value': '2004PrPh...52..200K',
            },
            {
                'schema': 'ADS',
                'value': '2006PhR...429..121K',
            },
            {
                'schema': 'SPIRES',
                'value': 'SPIRES-5682037',
            },
        ],
    })

    expected = [
        {
            'schema': 'DESY',
            'value': 'D04-00213',
        },
        {
            'schema': 'ADS',
            'value': '2004PrPh...52..200K',
        },
        {
            'schema': 'SPIRES',
            'value': 'SPIRES-5682037',
        },
    ]
    result = record.external_system_identifiers

    assert expected == result
