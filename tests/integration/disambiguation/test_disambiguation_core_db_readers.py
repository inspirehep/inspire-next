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
    get_all_publications,
    get_signatures_matching_a_phonetic_encoding,
)


def test_get_all_curated_signatures(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    expected = {
        'author_affiliation': 'CERN',
        'author_id': 1010819,
        'author_name': 'Ellis, John R.',
        'publication_id': 792017,
        'signature_block': 'ELj',
        'signature_uuid': '94f560d2-6791-43ec-a379-d3dc4ad0ceb7',
    }
    result = list(get_all_curated_signatures())

    assert expected in result


def test_get_all_curated_signatures_does_not_raise_on_authors_without_a_signature_block(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '1662077.json')

    list(get_all_curated_signatures())  # Does not raise.


def test_get_signatures_matching_a_phonetic_encoding(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '8201.json', index_name='records-hep')
    TestRecordMetadata.create_from_file(__name__, '1518353.json', index_name='records-hep')

    expected = [
        {
            'author_affiliation': 'SUNY, Stony Brook',
            'author_id': 991871,
            'author_name': 'Rho, Mannque',
            'publication_id': 8201,
            'signature_block': 'Rm',
            'signature_uuid': 'fe4220bf-7c57-4191-8d0c-6e791e84c505',
        },
        {
            'author_affiliation': '',
            'author_id': None,
            'author_name': 'Rao, Mayuri Sathyanarayana',
            'publication_id': 1518353,
            'signature_block': 'Rm',
            'signature_uuid': '383d97f4-5213-4735-9c7d-0d1cf992cce7',
        },
    ]
    result = list(get_signatures_matching_a_phonetic_encoding('Rm'))

    assert sorted(expected) == sorted(result)


def test_get_signatures_matching_a_phonetic_encoding_does_not_raise_on_authors_without_a_signature_block(isolated_app):
    TestRecordMetadata.create_from_file(__name__, '1662077.json', index_name='records-hep')

    list(get_signatures_matching_a_phonetic_encoding('WANGm'))  # Does not raise.


def test_get_all_publications():
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    expected = {
        'abstract': 'This talk describes past progress in probing the structure of matter and the content of the Universe, which has led to the Standard Model of elementary particles, and the prospects for establishing new physics beyond the Standard Model using the LHC particle collider at CERN.',
        'authors': ['Ellis, John R.'],
        'collaborations': [],
        'keywords': [
            '29.20.Db',
            '98.80.-k',
            '12.60.-i',
            'elementary particles',
            'standard model',
            'cosmology',
            'particle accelerators',
            'Elementary particles',
            'Beyond the Standard Model',
            'Colliders',
            'Large Hadron Collider',
            'Standard Model',
        ],
        'publication_id': 792017,
        'title': 'The quest for elementary particles',
        'topics': ['Phenomenology-HEP'],
    }
    result = list(get_all_publications())

    assert expected in result
