# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

import os

from selenium.common.exceptions import (
    ElementNotVisibleException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..arsenic import Arsenic, ArsenicResponse


def go_to():
    Arsenic().get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&status=HALTED&workflow_name=HEP')


def click_first_record():
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler'))).click()

    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '(//div[@class="ng-scope"])[2]')))


def load_submission_record(input_data):
    def _load_submission_record():
        return (
            'Computing' in record and
            'Accelerators' in record and
            'My Title For Test' in record and
            'admin@inspirehep.net' in record and
            'Mister White; Mister Brown' in record and
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.' in record
        )

    record = _force_load_record(input_data)
    return ArsenicResponse(_load_submission_record)


def _force_load_record(input_data):
    try:
        WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler/div[3]/a'))).click()
        record = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class="row hp-item ng-scope"][1]'))).text
    except (ElementNotVisibleException, WebDriverException):
        go_to()
        record = _force_load_record(input_data)

    return record
