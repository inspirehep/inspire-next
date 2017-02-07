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

import json
import os
import pkg_resources

import pytest
from freezegun import freeze_time

from inspirehep.modules.literaturesuggest.tasks import formdata_to_model


class WorkflowMockObj(object):

    def __init__(self, workflow_id, id_user):
        self.id = workflow_id
        self.id_user = id_user

        self.data = {}
        self.extra_data = {}


def load_record_dict(file_name):
    return json.loads(
        pkg_resources.resource_string(
            __name__,
            os.path.join('fixtures', file_name + '.json')
        )
    )


@pytest.fixture(scope='function')
def record_journal_article_input():
    yield load_record_dict('journal_article_input')


@pytest.fixture(scope='function')
def record_journal_article_expected():
    yield load_record_dict('journal_article_expected')


@pytest.fixture(scope='function')
def record_conference_article_input():
    yield load_record_dict('conference_article_input')


@pytest.fixture(scope='function')
def record_conference_article_expected():
    yield load_record_dict('conference_article_expected')


@pytest.fixture(scope='function')
def record_thesis_input():
    yield load_record_dict('thesis_input')


@pytest.fixture(scope='function')
def record_thesis_expected():
    yield load_record_dict('thesis_expected')


@freeze_time('1993-02-02 06:00:00')
def test_formdata_to_model_journal_article(record_journal_article_input,
                                           record_journal_article_expected,
                                           mock_user):
    workflow_obj = WorkflowMockObj(1, mock_user.id)

    input_data = record_journal_article_input

    expected_data = record_journal_article_expected

    output_data = formdata_to_model(workflow_obj, input_data)

    assert expected_data == output_data


@freeze_time('1993-02-02 06:00:00')
def test_formdata_to_model_conference_article(record_conference_article_input,
                                              record_conference_article_expected,
                                              mock_user):
    workflow_obj = WorkflowMockObj(1, mock_user.id)

    input_data = record_conference_article_input

    expected_data = record_conference_article_expected

    output_data = formdata_to_model(workflow_obj, input_data)

    assert expected_data == output_data


@freeze_time('1993-02-02 06:00:00')
def test_formdata_to_model_thesis(record_thesis_input,
                                  record_thesis_expected,
                                  mock_user):
    workflow_obj = WorkflowMockObj(1, mock_user.id)

    input_data = record_thesis_input

    expected_data = record_thesis_expected

    output_data = formdata_to_model(workflow_obj, input_data)

    assert expected_data == output_data
