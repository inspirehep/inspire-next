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

from selenium.common.exceptions import (
    ElementNotVisibleException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from . import holdingpen_literature_list
from ..arsenic import Arsenic, ArsenicResponse
from inspirehep.bat.EC import GetText, TryClick
from inspirehep.bat.utils import handle_timeuot_exception

BASIC_INFO = '(//div[@class="ng-scope"])[2]'
SUBMISSION_INFO = '//p[@class="text-center ng-scope"]'
SUBJECT_AREAS = '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])'
FIRST_SUBJECT_AREA = SUBJECT_AREAS + '[1]'
SECOND_SUBJECT_AREA = SUBJECT_AREAS + '[2]'
ACCEPT_NON_CORE_BUTTON = '//button[@class="btn btn-warning"]'
ACCEPTED_MESSAGE = '//div[@class="alert ng-scope alert-accept"]'


def go_to():
    holdingpen_literature_list.go_to()
    holdingpen_literature_list.click_first_record()


def assert_first_record_matches(input_data, try_count=0):
    def _assert_author_matches(author, authors_info):
        for name_part in author.get('name', ''):
            assert name_part in authors_info

        assert author.get('affiliation', '') in authors_info

    try:
        basic_info = WebDriverWait(Arsenic(), 10).until(
            GetText((By.XPATH, BASIC_INFO))
        )
        submission_info = Arsenic().find_element_by_xpath(SUBMISSION_INFO).text
        first_subject = Arsenic().find_element_by_xpath(FIRST_SUBJECT_AREA).text
        second_subject = Arsenic().find_element_by_xpath(SECOND_SUBJECT_AREA).text
    except (ElementNotVisibleException, WebDriverException):
        try_count += 1
        go_to()
        if try_count > 15:
            raise
        assert_first_record_matches(input_data, try_count=try_count)

    for author in input_data.authors:
        _assert_author_matches(author, basic_info)
    if input_data.subjects:
        assert input_data.subjects[0] in first_subject
    if len(input_data.subjects) > 1:
        assert input_data.subjects[1] in second_subject

    assert input_data.get('abstract', '') in basic_info
    assert 'Submitted by admin@inspirehep.net\non' in submission_info


def accept_record():
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            GetText((By.XPATH, ACCEPTED_MESSAGE))
        )
        assert 'Accepted as Non-CORE' in message

    arsenic = Arsenic()
    try:
        WebDriverWait(Arsenic(), 10).until(
            TryClick((By.XPATH, ACCEPT_NON_CORE_BUTTON))
        )
    except Exception as exc:
        handle_timeuot_exception(arsenic=arsenic, exc=exc, with_api=True)

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)
