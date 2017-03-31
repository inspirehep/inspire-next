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

import mock

from inspirehep.modules.literaturesuggest.form_normalization import (
    journal_title_normalization,
    split_page_artid_normalization,
    remove_english_language,
)


class WorkflowMockObj(object):

    def __init__(self, workflow_id, id_user):
        self.id = workflow_id
        self.id_user = id_user

        self.data = {}
        self.extra_data = {}


@mock.patch(
    'inspirehep.modules.literaturesuggest.form_normalization.split_page_artid',
    return_value=['789', '890', None]
)
def test_split_page_artid_normalization_wrong(mock_split_page_artid):
    input_data = {}
    expected_data = {}

    result_data = split_page_artid_normalization(input_data)

    assert result_data == expected_data


@mock.patch(
    'inspirehep.modules.literaturesuggest.form_normalization.split_page_artid',
    return_value=['789', '890', None]
)
def test_split_page_artid_normalization_correct(mock_split_page_artid):
    input_data = {'page_range_article_id': '789-890'}
    expected_data = {
        'page_range_article_id': '789-890',
        'page_start': '789',
        'page_end': '890',
        'artid': None,
    }
    result_data = split_page_artid_normalization(input_data)

    assert result_data == expected_data


@mock.patch(
    'inspirehep.modules.literaturesuggest.form_normalization.normalize_journal_title',
    return_value='Open Physics Journal'
)
def test_journal_title_normalization_with_journal(mock_normalize_journal_title):
    input_data = {'journal_title': 'open physics journal'}
    expected_data = {'journal_title': 'Open Physics Journal'}

    result_data = journal_title_normalization(input_data)

    assert result_data == expected_data


@mock.patch(
    'inspirehep.modules.literaturesuggest.form_normalization.normalize_journal_title',
    return_value='Open Physics Journal'
)
def test_journal_title_normalization_with_empty_journal(mock_normalize_journal_title):
    input_data = {}
    expected_data = {}

    result_data = journal_title_normalization(input_data)

    assert result_data == expected_data


def test_remove_english_language_with_english():
    input_data = {'language': 'en'}
    expected_data = {}

    result_data = remove_english_language(input_data)

    assert result_data == expected_data


def test_remove_english_language_with_italian():
    input_data = {'language': 'it'}
    expected_data = {'language': 'it'}

    result_data = remove_english_language(input_data)

    assert result_data == expected_data
