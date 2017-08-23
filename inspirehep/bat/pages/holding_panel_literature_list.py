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

import os

from selenium.common.exceptions import (
    ElementNotVisibleException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..arsenic import Arsenic, ArsenicResponse
from inspirehep.bat.EC import GetText


def go_to():
    Arsenic().get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=HEP')


def force_load_record(xpath):
    def _refresh_page():
        go_to()
        return force_load_record(xpath)

    try:
        WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, xpath)
            )
        ).click()
        record = WebDriverWait(Arsenic(), 10).until(
            GetText(
                (By.XPATH, '//div[@class="row hp-item ng-scope"][1]')
            )
        )
    except (ElementNotVisibleException, WebDriverException):
        record = _refresh_page()

    if 'Waiting' in record:
        return _refresh_page()

    return record


def click_first_record():
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler'))).click()

    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '(//div[@class="ng-scope"])[2]')))


def load_submitted_record():
    def _load_submitted_record():
        return (
            'Computing' in record and
            'Accelerators' in record and
            'My Title For Test' in record and
            'admin@inspirehep.net' in record and
            'White, Barry; Brown, James' in record and
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.' in record
        )

    record = force_load_record('//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler/div[3]/a')
    return ArsenicResponse(_load_submitted_record)


def load_completed_record():
    def _load_completed_record():
        return 'Completed' in record

    record = force_load_record('//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler/div[4]/a')
    return ArsenicResponse(_load_completed_record)
