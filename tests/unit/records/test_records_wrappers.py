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
                'schema': 'CDS',
                'value': '2231692',
            },
            {
                'schema': 'CDS',
                'value': '2232052',
            },
            {
                'schema': 'HAL',
                'value': 'in2p3-01394924',
            },
            {
                'schema': 'KEKSCAN',
                'value': '200727065'
            }
        ],
    })

    expected = [
        {
            'url_name': 'CERN Document Server',
            'url_link': 'http://cds.cern.ch/record/2231692'
        },
        {
            'url_name': 'HAL Archives Ouvertes',
            'url_link': 'https://hal.archives-ouvertes.fr/in2p3-01394924'
        },
        {
            'url_name': 'KEK scanned document',
            'url_link': 'https://lib-extopc.kek.jp/preprints/PDF/2007/0727/0727065.pdf'
        }
    ]

    result = record.external_system_identifiers

    assert expected == result
