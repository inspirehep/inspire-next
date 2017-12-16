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


TITLE_AND_DESCRIPTION = '(//div[@class="ng-scope"])[2]'
SUBMISSION_INFO = '//p[@class="text-center ng-scope"]'
SUBJECT_AREAS = '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])'
FIRST_SUBJECT_AREA = SUBJECT_AREAS + '[1]'
SECOND_SUBJECT_AREA = SUBJECT_AREAS + '[2]'
ACCEPT_NON_CORE_BUTTON = '//button[@class="btn btn-warning"]'
ACCEPTED_MESSAGE = '//div[@class="alert ng-scope alert-accept"]'


def go_to():
    holdingpen_literature_list.go_to()
    holdingpen_literature_list.click_first_record()


def load_submitted_record(input_data):
    def _load_submitted_record():
        return (
            input_data.get('abstract', '') in record and
            'Submitted by admin@inspirehep.net\non' in record and
            input_data.get('title', '') in record and
            all(
                name_part in record
                for name_part in input_data.get('author-0', '').split()
            ) and
            input_data.get('author-0-affiliation', '') in record and
            all(
                name_part in record
                for name_part in input_data.get('author-1', '').split()
            ) and
            input_data.get('author-1-affiliation', '') in record and
            'Accelerators' in record and
            input_data.get('subject', '') in record
        )

    try:
        record = WebDriverWait(Arsenic(), 10).until(
            GetText((By.XPATH, TITLE_AND_DESCRIPTION))
        )
        record += Arsenic().find_element_by_xpath(SUBMISSION_INFO).text
        record += Arsenic().find_element_by_xpath(FIRST_SUBJECT_AREA).text
        record += Arsenic().find_element_by_xpath(SECOND_SUBJECT_AREA).text
    except (ElementNotVisibleException, WebDriverException):
        go_to()
        record = load_submitted_record(input_data)

    return ArsenicResponse(_load_submitted_record)


def accept_record():
    def _accept_record():
        return 'Accepted as Non-CORE' in WebDriverWait(Arsenic(), 10).until(
            GetText((By.XPATH, ACCEPTED_MESSAGE))
        )

    WebDriverWait(Arsenic(), 10).until(
        TryClick((By.XPATH, ACCEPT_NON_CORE_BUTTON))
    )

    return ArsenicResponse(_accept_record)
