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

from inspirehep.modules.literaturesuggest.form_normalization import normalization_formdata


class WorkflowMockObj(object):

    def __init__(self, workflow_id, id_user):
        self.id = workflow_id
        self.id_user = id_user

        self.data = {}
        self.extra_data = {}


def test_formdata_to_model_journal_article(
    mock_user
):
    workflow_obj = WorkflowMockObj(1, mock_user.id)

    input_data = {
        'page_range_article_id': '789-890',
        'journal_title': 'open physics journal',
        'language': 'en'
    }

    expected_data = {
        'page_range_article_id': '789-890',
        'page_start': '789',
        'page_end': '890',
        'artid': None,
        'journal_title': 'open physics journal',
        'orcid': '0000-0001-9412-8627',
        'email': 'test_orcid_user@inspirehep.net'
    }

    output_data = normalization_formdata(workflow_obj, input_data)

    assert expected_data == output_data
