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

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException



def test_institutions_typehead(selenium, login):
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    institution_field = selenium.find_element_by_id('institution_history-0-name')
    institution_field.send_keys('CER')
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    institution_field.send_keys(Keys.DOWN)
    institution_field.send_keys(Keys.ENTER)
    assert 'CERN' in institution_field.get_attribute('value')


def test_experiments_typehead(selenium, login):
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    experiment_field = selenium.find_element_by_id('experiments-0-name')
    experiment_field.send_keys('ATL')
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    experiment_field.send_keys(Keys.DOWN)
    experiment_field.send_keys(Keys.ENTER)
    assert 'ATLAS' in experiment_field.get_attribute('value')


def test_advisors_typehead(selenium, login):
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    advisor_field = selenium.find_element_by_id('advisors-0-name')
    advisor_field.send_keys('alexe')
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    advisor_field.send_keys(Keys.DOWN)
    advisor_field.send_keys(Keys.ENTER)
    assert 'Vorobyev, Alexey' in advisor_field.get_attribute('value')


def test_mail_format(selenium, login):
    """Test mail format in Personal Information for an author"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    mail_field = selenium.find_element_by_id('public_email')

    try:
        mail_field.send_keys('wrong.mail')
        mail_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-public_email")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Invalid email address." in selenium.page_source
    mail_field.clear()

    try:
        mail_field.send_keys('me@me.com')
        mail_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-public_email")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Invalid email address." not in selenium.page_source


def test_ORCID_format(selenium, login):
    """Test ORCID format in Personal Information for an author"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    ORCID_field = selenium.find_element_by_id('orcid')

    try:
        ORCID_field.send_keys('wrong.ORCID')
        ORCID_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, 'state-orcid')))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'A valid ORCID iD consists of 16 digits separated by dashes.' in selenium.page_source
    ORCID_field.clear()

    try:
        ORCID_field.send_keys('1111-1111-1111-1111')
        ORCID_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, 'state-orcid')))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'A valid ORCID iD consists of 16 digits separated by dashes.' not in selenium.page_source
