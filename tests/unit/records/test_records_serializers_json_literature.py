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

from mock import patch

from inspirehep.modules.records.serializers.json_literature import \
    _preprocess_result

SERIALIZED_RECORD_WITH_UI_METADATA = {
    'metadata': {
        'references': [
            {
                'title': 'reference 1',
            },
            {
                'title': 'reference 2',
            },
        ],
        'authors': [
            {
                'full_name': 'Luke Cage',
            },
            {
                'full_name': 'Frank Castle',
            },
            {
                'full_name': 'Misty Knight',
            },
            {
                'full_name': 'Foggy Nelson',
            },
            {
                'full_name': 'Claire Temple',
            },
            {
                'full_name': 'Patsy Walker',
            },
            {
                'full_name': 'Dany Rand',
            },
            {
                'full_name': 'Karen Page',
            },
            {
                'full_name': 'Stick',
            },
            {
                'full_name': 'Bakuto',
            },
            {
                'full_name': 'Malcome Ducasse',
            },
        ],
        'title': 'Jessica Jones - PI',
    }
}

SERIALIZED_RECORD_WITHOUT_UI_METADATA = {
    'metadata': {
        'title': 'Jessica Jones - PI',
    }
}


def test_preprocess_with_ui_metadata():
    with patch('inspirehep.modules.records.wrappers.LiteratureRecord.admin_tools'):
        result = _preprocess_result(SERIALIZED_RECORD_WITH_UI_METADATA)

    assert len(result['metadata']['authors']) == 10
    assert result['metadata']['number_of_references'] == 2
    assert result['metadata']['number_of_authors'] == 11
    assert 'display' in result
    assert 'references' not in result['metadata']


def test_preprocess_without_ui_metadata():
    with patch('inspirehep.modules.records.wrappers.LiteratureRecord.admin_tools'):
        result = _preprocess_result(SERIALIZED_RECORD_WITHOUT_UI_METADATA)

    assert 'display' in result
    assert 'title' in result['metadata']
    assert 'number_of_references' not in result['metadata']
    assert 'number_of_authors' not in result['metadata']
