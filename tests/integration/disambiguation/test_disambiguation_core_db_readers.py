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

from factories.db.invenio_records import TestRecordMetadata

from inspirehep.modules.disambiguation.core.db.readers import (
    get_all_curated_signatures,
    get_signatures_matching_a_phonetic_encoding,
)


def test_get_all_curated_signatures(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    expected = {
        'affiliations': [
            {
                'record': {
                    '$ref': 'http://labs.inspirehep.net/api/institutions/902725',
                },
                'value': 'CERN',
            },
        ],
        'curated_relation': True,
        'full_name': 'Ellis, John R.',
        'ids': [
            {
                'schema': 'INSPIRE ID',
                'value': 'INSPIRE-00146525',
            },
        ],
        'raw_affiliations': [
            {
                'value': 'CERN. Department of Physics. TH Division Geneva, Switzerland',
            },
        ],
        'record': {
            '$ref': 'http://labs.inspirehep.net/api/authors/1010819',
        },
        'signature_block': 'ELj',
        'uuid': '94f560d2-6791-43ec-a379-d3dc4ad0ceb7',
    }
    result = list(get_all_curated_signatures())

    assert expected in result


def test_get_signatures_matching_a_phonetic_encoding(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '8201.json', index_name='records-hep')
    TestRecordMetadata.create_from_file(__name__, '1518353.json', index_name='records-hep')

    expected = [
        {
            'affiliations': [
                {
                    'record': {
                        '$ref': 'http://labs.inspirehep.net/api/institutions/903237',
                    },
                    'value': 'SUNY, Stony Brook',
                },
            ],
            'full_name': 'Rho, Mannque',
            'record': {
                '$ref': 'http://labs.inspirehep.net/api/authors/991871',
            },
            'signature_block': 'Rm',
            'uuid': 'fe4220bf-7c57-4191-8d0c-6e791e84c505',
        },
        {
            'full_name': 'Rao, Mayuri Sathyanarayana',
            'signature_block': 'Rm',
            'uuid': '383d97f4-5213-4735-9c7d-0d1cf992cce7',
        },
    ]
    result = list(get_signatures_matching_a_phonetic_encoding('Rm'))

    assert sorted(expected) == sorted(result)
