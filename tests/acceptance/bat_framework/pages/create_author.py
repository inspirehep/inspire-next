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
from bat_framework.arsenic_response import ArsenicResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException


def go_to():
    Arsenic().get(os.environ['SERVER_NAME'] + '/submit/author/create')


def write_institution(institution, expected_data):
    return ArsenicResponse(lambda: expected_data in Arsenic().write_in_autocomplete_field('institution_history-0-name', institution))


def write_experiment(experiment, expected_data):
    return ArsenicResponse(lambda: expected_data in Arsenic().write_in_autocomplete_field('experiments-0-name', experiment))


def write_advisor(advisor, expected_data):
    return ArsenicResponse(lambda: expected_data in Arsenic().write_in_autocomplete_field('advisors-0-name', advisor))


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
    return ArsenicResponse(lambda: 'Invalid email address.' in message_err)


def write_orcid(orcid):
    message_err = ''
    ORCID_field = Arsenic().find_element_by_id('orcid')
    ORCID_field.send_keys(orcid)
    try:
        ORCID_field.send_keys(Keys.TAB)
        message_err = WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'state-orcid'))).text
    except (ElementNotVisibleException, WebDriverException):
        pass
    ORCID_field.clear()
    return ArsenicResponse(lambda: 'A valid ORCID iD consists of 16 digits separated by dashes.' in message_err)


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
    return ArsenicResponse(lambda: 'is not a valid year' in message_err)


def submit_empty_form(expected_data):
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
    return ArsenicResponse(lambda: expected_data == output_data)


def submit_author(input_data):
    Arsenic().hide_title_bar()
    WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'given_names'))).send_keys(input_data['given-names'])
    Arsenic().find_element_by_id('family_name').send_keys(input_data['family-name'])
    Arsenic().find_element_by_id('display_name').send_keys(input_data['display-name'])
    Arsenic().find_element_by_id('native_name').send_keys(input_data['native-name'])
    Arsenic().find_element_by_id('public_emails-0-email').send_keys(input_data['public-email'])
    Arsenic().find_element_by_id('orcid').send_keys(input_data['orcid'])
    Arsenic().find_element_by_id('websites-0-webpage').send_keys(input_data['websites-0'])
    Arsenic().find_element_by_xpath('(//a[@class="add-element"])[2]').click()
    WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'websites-1-webpage'))).send_keys(input_data['websites-1'])
    Arsenic().find_element_by_id('linkedin_url').send_keys(input_data['linkedin-url'])
    Arsenic().find_element_by_id('twitter_url').send_keys(input_data['twitter-url'])
    Arsenic().find_element_by_id('blog_url').send_keys(input_data['blog-url'])
    Arsenic().find_element_by_id('institution_history-0-name').send_keys(input_data['institution-name'])
    Arsenic().find_element_by_id('institution_history-0-start_year').send_keys(input_data['institution-start_year'])
    Arsenic().find_element_by_id('institution_history-0-end_year').send_keys(input_data['institution-end_year'])
    Select(Arsenic().find_element_by_id('institution_history-0-rank')).select_by_value(input_data['institution-rank'])
    Arsenic().find_element_by_id('experiments-0-name').send_keys(input_data['experiments-name'])
    Arsenic().find_element_by_id('experiments-0-start_year').send_keys(input_data['experiments-start_year'])
    Arsenic().find_element_by_id('experiments-0-end_year').send_keys(input_data['experiments-end_year'])
    Arsenic().find_element_by_id('advisors-0-name').send_keys(input_data['advisors-name'])
    Arsenic().find_element_by_id('comments').send_keys(input_data['comments'])
    Arsenic().find_element_by_xpath('//button[@class="multiselect dropdown-toggle btn btn-default"]').click()
    Arsenic().find_element_by_xpath('//input[@value="' + input_data['subject-0'] + '"]').click()
    Arsenic().find_element_by_xpath('//input[@value="' + input_data['subject-1'] + '"]').click()
    Arsenic().find_element_by_xpath('//button[@class="btn btn-success form-submit"]').click()
    Arsenic().show_title_bar()
    return ArsenicResponse(lambda: 'Thank you for adding new profile information!' in WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'))).text)
