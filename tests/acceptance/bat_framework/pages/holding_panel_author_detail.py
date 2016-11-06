# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

import os

from bat_framework.arsenic import Arsenic
from bat_framework.arsenic_response import ArsenicResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException
from bat_framework.pages import holding_panel_author_list


def go_to():
    holding_panel_author_list.go_to()
    holding_panel_author_list.click_first_record()


def load_submitted_record(input_data):
    try:
        record = WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="detail-panel"])[1]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="ng-scope"])[2]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="detail-panel"])[4]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="detail-panel"])[5]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])[2]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="detail-panel panel-100"]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="subject-list"]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="advisors"]'))).text
        record += WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="table-body"]'))).text
    except (ElementNotVisibleException, WebDriverException):
        go_to()
        record = load_submitted_record(input_data)
    return ArsenicResponse(lambda:  'M. Twain' in record and
                                    'Twain, Mark' in record and
                                    'Experiment: ATLAS - From: 2002 To: 2005' in record and
                                    'Submitted by admin@inspirehep.net\non' in record and
                                    'Some comments about the author' in record and
                                    'http://www.example1.com' in record and
                                    'http://www.example3.com' in record and
                                    'http://www.example4.com' in record and
                                    'http://www.example5.com' in record and
                                    'ACC-PHYS' in record and
                                    'ASTRO-PH' in record and
                                    'Bob White' in record and
                                    'CERN' in record and
                                    '2000' in record and
                                    '2001' in record)


def accept_record():
    Arsenic().find_element_by_xpath('//button[@class="btn btn-success"]').click()
    return ArsenicResponse(lambda: 'Accepted as Non-CORE' in WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="alert ng-scope alert-accept"]'))).text)


def reject_record():
    Arsenic().find_element_by_xpath('//button[@class="btn btn-danger"]').click()
    return ArsenicResponse(lambda: 'Rejected' in WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="alert ng-scope alert-reject"]'))).text)


def curation_record():
    Arsenic().find_element_by_xpath('//button[@class="btn btn-warning"]').click()
    return ArsenicResponse(lambda: 'Accepted with Curation' in WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '//span[@ng-switch-when="accept_curate"]'))).text)


def review_record():
    Arsenic().find_element_by_xpath('(//button[@class="btn btn-info"])[2]').click()
    return ArsenicResponse(lambda: WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'inspireid'))) and WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'bai'))))
