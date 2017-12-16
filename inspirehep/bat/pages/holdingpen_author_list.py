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
    Arsenic().get(
        os.environ['SERVER_NAME'] +
        (
            '/holdingpen/list/?workflow_name=Author&is-update=false&size=10'
            '&status=HALTED'
        )
    )


def click_first_record():
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//a[@class="title ng-binding ng-scope"]')
        )
    ).click()
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '(//div[@class="detail-panel"])[1]')
        )
    )


def load_submission_record(input_data):
    def _load_submission_record():
        return (
            'CERN' in record and
            'cond-mat' in record and
            'astro-ph' in record and
            'Twain, Mark' in record and
            'admin@inspirehep.net' in record
        )

    try:
        record = WebDriverWait(Arsenic(), 10).until(
            GetText(
                (By.XPATH, '//div[@class="row hp-item ng-scope"][1]')
            )
        )
    except (ElementNotVisibleException, WebDriverException):
        go_to()
        return load_submission_record(input_data)

    return ArsenicResponse(_load_submission_record)
