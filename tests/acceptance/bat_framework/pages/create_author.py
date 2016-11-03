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

from __future__ import absolute_import, division, print_function

import os

from bat_framework.arsenic import Arsenic
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException


def go_to():
    Arsenic().get(os.environ['SERVER_NAME'] + '/submit/author/create')


def write_institution(institution):
    return Arsenic().write_in_autocomplete_field('institution_history-0-name', institution)


def write_experiment(experiment):
    return Arsenic().write_in_autocomplete_field('experiments-0-name', experiment)


def write_advisor(advisor):
    return Arsenic().write_in_autocomplete_field('advisors-0-name', advisor)


def write_mail(mail):
    message_err = ''
    mail_field = Arsenic().find_element_by_id('public_emails-0-email')
    mail_field.send_keys(mail)
    try:
        mail_field.send_keys(Keys.TAB)
        message_err = WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'state-public_emails-0-email'))).text
    except (ElementNotVisibleException, WebDriverException):
        pass
    mail_field.clear()
    return message_err


def write_orcid(orcid):
    message_err = ''
    ORCID_field = Arsenic().find_element_by_id('orcid')
    ORCID_field.send_keys(orcid)
    try:
        ORCID_field.send_keys(Keys.TAB)
        message_err = WebDriverWait(Arsenic(), 10).until(EC.presence_of_element_located((By.ID, 'state-orcid'))).text
    except (ElementNotVisibleException, WebDriverException):
        pass
    ORCID_field.clear()
    return message_err


def write_year(input_id, error_message_id, year):
    message_err = ''
    year_field = Arsenic().find_element_by_id(input_id)
    year_field.send_keys(year)
    try:
        year_field.send_keys(Keys.TAB)
        message_err = WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, error_message_id))).text
    except (ElementNotVisibleException, WebDriverException):
        pass
    year_field.clear()
    return message_err


def submit_empty_form():
    output_data = {}
    Arsenic().find_element_by_xpath('//button[@class="btn btn-success form-submit"]').click()
    try:
        WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'state-given_names')))
        WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'state-display_name')))
        WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'state-research_field')))
        output_data = {
            'given-name': Arsenic().find_element_by_id('state-given_names').text,
            'display-name': Arsenic().find_element_by_id('state-display_name').text,
            'reserach-field': Arsenic().find_element_by_id('state-research_field').text
            }
    except (ElementNotVisibleException, WebDriverException):
        pass
    return output_data
