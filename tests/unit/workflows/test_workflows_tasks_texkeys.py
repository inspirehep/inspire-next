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

import datetime
import mock
import pytest

from inspire_schemas.api import (
    load_schema,
    validate,
)
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.texkeys import (
    inspire_texkey_minter,
    TexkeyMinterError,
    TexkeyMinterAlreadyValid,
)


class MockInspireRecord():
    def __init__(self, my_dict):
        self.my_dict = my_dict
        self.created = datetime.datetime(2017, 1, 1, 1, 1, 1, 1)

    def __getitem__(self, key):
        return self.my_dict[key]

    def get(self, key, value):
        if key in self.my_dict.keys():
            return self.my_dict[key]
        return value

    def setdefault(self, key, value):
        if key not in self.my_dict.keys():
            self.my_dict[key] = value


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_with_author(mock_store_pidstore, mock_random_letters, app):
    record = {
        'authors': [
            {'full_name': 'Cox, Brian'},
            {'full_name': 'Dan, Brown'}
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'Cox:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_with_more_than_10_authors(mock_store_pidstore, mock_random_letters, app):
    record = {
        'authors': [
            {'full_name': 'Arnaldi, R.'},
            {'full_name': 'Alexa, C.'},
            {'full_name': 'Alessandro, B.'},
            {'full_name': 'Atayan, M.'},
            {'full_name': 'Beole, S.'},
            {'full_name': 'Boldea, V.'},
            {'full_name': 'Bordalo, P.'},
            {'full_name': 'Borges, G.'},
            {'full_name': 'Castanier, C.'},
            {'full_name': 'Castor, J.'},
            {'full_name': 'Chaurand, B.'}
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'Arnaldi:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_with_more_than_10_authors_with_collaborations(mock_store_pidstore, mock_random_letters, app):
    record = {
        'authors': [
            {'full_name': 'Arnaldi, R.'},
            {'full_name': 'Alexa, C.'},
            {'full_name': 'Alessandro, B.'},
            {'full_name': 'Atayan, M.'},
            {'full_name': 'Beole, S.'},
            {'full_name': 'Boldea, V.'},
            {'full_name': 'Bordalo, P.'},
            {'full_name': 'Borges, G.'},
            {'full_name': 'Castanier, C.'},
            {'full_name': 'Castor, J.'},
            {'full_name': 'Chaurand, B.'}
        ],
        'collaborations': [
            {'value': 'CMS'}
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'CMS:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_without_author_with_collaborations(mock_store_pidstore, mock_random_letters, app):
    record = {
        'collaborations': [
            {'value': 'CMS'}
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'CMS:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_without_author_and_collaborations_with_corporate_author(mock_store_pidstore, mock_random_letters, app):
    record = {
        'corporate_author': [
            'CMS Collaboration'
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'CMSCollaboration:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_without_author_and_collaborations_and_corporate_author_with_proceedings(mock_store_pidstore, mock_random_letters, app):
    record = {
        'document_type': ['proceedings']
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'proceedings:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_without_author_and_collaborations_and_corporate_author_and_proceedings(mock_store_pidstore, mock_random_letters, app):
    record = {}
    record = MockInspireRecord(record)

    with pytest.raises(TexkeyMinterError):
        inspire_texkey_minter('', record)


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_different_not_used_in_other_records(mock_store_pidstore, mock_random_letters, app):
    record = {
        'texkeys': ['Dan:2017xyz'],
        'authors': [
            {'full_name': 'Cox, Brian'},
            {'full_name': 'Dan, Brown'}
        ]
    }
    record = MockInspireRecord(record)

    generated_texkey = inspire_texkey_minter('', record)
    expected_texkey = 'Cox:2017xyz'

    assert generated_texkey == expected_texkey


@mock.patch(
    'inspirehep.modules.records.texkeys.get_three_random_letters',
    return_value='xyz',
)
@mock.patch(
    'inspirehep.modules.records.texkeys.store_texkeys_pidstore',
    return_value=True,
)
def test_inspire_texkey_minter_generates_same_keys(mock_store_pidstore, mock_random_letters, app):
    record = {
        'texkeys': ['Cox:2017xyz'],
        'authors': [
            {
                'full_name': 'Cox, Brian',
            }, {
                'full_name': 'Dan, Brown'
            }
        ]
    }
    record = MockInspireRecord(record)

    with pytest.raises(TexkeyMinterAlreadyValid):
        inspire_texkey_minter('', record)
