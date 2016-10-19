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

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException

from test_literature_suggestion_form import show_title_bar
from test_literature_suggestion_form import hide_title_bar


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


def test_author_creation(selenium, login):
    """Submit the form for author creation from scratch"""
    _insert_author(selenium)
    selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=Author&is-update=false&status=HALTED')
    hide_title_bar(selenium)
    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="row hp-item ng-scope"][1]'))).text
    assert 'CERN' in record
    assert 'ACC-PHYS' in record
    assert 'ASTRO-PH' in record
    assert 'Twain, Mark' in record
    assert 'inspire:uid:1' in record
    assert 'admin@inspirehep.net' in record
    assert '1 record found.' in selenium.find_element_by_xpath('//div[@class="invenio-search-results"]/ng-pluralize').text

    selenium.find_element_by_xpath('//a[@class="title ng-binding ng-scope"]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="detail-panel"])[1]'), 'M. Twain'))
    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="detail-panel"])[1]'))).text
    assert 'M. Twain' in record
    assert 'M. Twain' in record
    assert 'Twain, Mark' in record
    assert 'mark.twain@history.org' in record
    assert 'Experiment: ATLAS - From: 2002 To: 2005' in record
    assert 'Submitted by admin@inspirehep.net\non' in selenium.find_element_by_xpath('(//div[@class="detail-panel"])[4]').text
    assert 'Some comments about the author' in selenium.find_element_by_xpath('(//div[@class="detail-panel"])[5]').text

    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="detail-panel panel-100"]'))).text
    assert 'http://www.example1.com' in record
    assert 'http://www.example2.com' in record
    assert 'http://www.example3.com' in record
    assert 'http://www.example4.com' in record
    assert 'http://www.example5.com' in record

    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="subject-list"]'))).text
    assert 'ACC-PHYS' in record
    assert 'ASTRO-PH' in record

    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="advisors"]'))).text
    assert 'Bob White' in record
    assert 'PhD' in record

    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="table-body"]'))).text
    assert 'CERN' in record
    assert 'STAFF' in record
    assert '2000' in record
    assert '2001' in record
    show_title_bar(selenium)


def test_review_submission_author(selenium, login):
    _insert_author(selenium)
    selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=Author&is-update=false&status=HALTED')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@class="title ng-binding ng-scope"]'))).click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="detail-panel"])[1]'), 'M. Twain'))
    selenium.find_element_by_xpath('(//button[@class="btn btn-info"])[2]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '//h1'), 'Reviewing author information'))
    assert 'Reviewing author information' in selenium.find_element_by_xpath('//h1').text
    hide_title_bar(selenium)
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'bai'))).send_keys('M.Santos.1')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'inspireid'))).send_keys('INSPIRE-0000000')
    _fill_author_field(selenium)
    selenium.find_element_by_xpath('//a[@class="btn btn-success form-submit"]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The author update has been approved'))
    assert 'The author update has been approved' in selenium.page_source
    selenium.get(os.environ['SERVER_NAME'] + '/search?page=1&size=25&cc=authors&q=Diego')
    author = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '(//a[@class="title ng-binding ng-scope"])[1]'))).text
    assert 'Diego' in author
    show_title_bar(selenium)


def test_accept_author(selenium, login):
    _insert_author(selenium)
    selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=Author&is-update=false&status=HALTED')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@class="title ng-binding ng-scope"]'))).click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="detail-panel"])[1]'), 'M. Twain'))
    selenium.find_element_by_xpath('//button[@class="btn btn-success"]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '//div[@class="alert ng-scope alert-accept"]'), 'Accepted as Non-CORE'))
    assert 'Accepted as Non-CORE' in selenium.find_element_by_xpath('//div[@class="alert ng-scope alert-accept"]').text


def test_reject_author(selenium, login):
    _insert_author(selenium)
    selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=Author&is-update=false&status=HALTED')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@class="title ng-binding ng-scope"]'))).click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="detail-panel"])[1]'), 'M. Twain'))
    selenium.find_element_by_xpath('//button[@class="btn btn-danger"]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '//div[@class="alert ng-scope alert-reject"]'), 'Rejected'))
    assert 'Rejected' in selenium.find_element_by_xpath('//div[@class="alert ng-scope alert-reject"]').text


def test_curation_author(selenium, login):
    _insert_author(selenium)
    selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&workflow_name=Author&is-update=false&status=HALTED')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@class="title ng-binding ng-scope"]'))).click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="detail-panel"])[1]'), 'M. Twain'))
    selenium.find_element_by_xpath('(//button[@class="btn btn-warning"])[1]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '//div[@class="text-muted ng-scope"]'), 'Accepted with Curation'))
    assert 'Accepted with Curation' in selenium.find_element_by_xpath('//div[@class="text-muted ng-scope"]').text


def _insert_author(selenium):
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    hide_title_bar(selenium)
    _fill_author_field(selenium)
    selenium.find_element_by_xpath('//button[@class="btn btn-success form-submit"]').click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'Thank you for adding new profile information!'))
    assert 'Thank you for adding new profile information!' in selenium.page_source
    show_title_bar(selenium)


def _fill_author_field(selenium):
    selenium.find_element_by_id('given_names').send_keys('Mark')
    selenium.find_element_by_id('family_name').send_keys('Twain')
    selenium.find_element_by_id('display_name').send_keys('M. Twain')
    selenium.find_element_by_id('native_name').send_keys('M. Twain')
    selenium.find_element_by_id('public_email').send_keys('mark.twain@history.org')
    selenium.find_element_by_id('orcid').send_keys('1111-1111-1111-1111')
    selenium.find_element_by_id('websites-0-webpage').send_keys('http://www.example1.com')
    selenium.find_element_by_xpath('(//a[@class="add-element"])[1]').click()
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'websites-1-webpage'))).send_keys('http://www.example2.com')
    selenium.find_element_by_id('linkedin_url').send_keys('http://www.example3.com')
    selenium.find_element_by_id('twitter_url').send_keys('http://www.example4.com')
    selenium.find_element_by_id('blog_url').send_keys('http://www.example5.com')
    selenium.find_element_by_id('institution_history-0-name').send_keys('CERN')
    selenium.find_element_by_id('institution_history-0-start_year').send_keys('2000')
    selenium.find_element_by_id('institution_history-0-end_year').send_keys('2001')
    Select(selenium.find_element_by_id('institution_history-0-rank')).select_by_value('STAFF')
    selenium.find_element_by_id('experiments-0-name').send_keys('ATLAS')
    selenium.find_element_by_id('experiments-0-start_year').send_keys('2002')
    selenium.find_element_by_id('experiments-0-end_year').send_keys('2005')
    selenium.find_element_by_id('advisors-0-name').send_keys('Bob White')
    Select(selenium.find_element_by_id('advisors-0-degree_type')).select_by_value('PhD')
    selenium.find_element_by_id('comments').send_keys('Some comments about the author')
    selenium.find_element_by_xpath('//button[@class="multiselect dropdown-toggle btn btn-default"]').click()
    selenium.find_element_by_xpath('//input[@value="ACC-PHYS"]').click()
    selenium.find_element_by_xpath('//input[@value="ASTRO-PH"]').click()


def _check_year_format(input_id, error_message_id, selenium):
    year_field = selenium.find_element_by_id(input_id)
    try:
        year_field.send_keys('wrongyear')
        year_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, error_message_id)))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'is not a valid year' in selenium.page_source
    year_field.clear()

    try:
        year_field.send_keys('2016')
        year_field.send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, error_message_id)))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'is not a valid year' not in selenium.page_source
