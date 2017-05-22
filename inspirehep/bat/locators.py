# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from selenium.webdriver.common.by import By


# Literature Classes
class LoginPageLocators(object):
    LOG_OUT_BUTTON = (By.XPATH, '(//button[@type="button"])[2]')
    SUBMIT_BUTTON = (By.XPATH, '//button[@type="submit"]')
    PROFILE_BUTTON = (By.ID, 'user-info')
    PASSW_TEXT_BOX = (By.ID, 'password')
    EMAIL_TEXT_BOX = (By.ID, 'email')


class CreateLiteraturePageLocators(object):
    SUBMIT_BUTTON = (By.XPATH, '//div[@id="webdeposit_form_accordion"]/div[4]/span/button')
    ACCEPT_BUTTON = (By.XPATH, '//button[@class="btn btn-warning"]')
    SKIP_IMPORT_DATA = (By.ID, 'skipImportData')
    LITERATURE_FORM = (By.ID, 'form_container')
    DROPDOWN_BUTTON = (By.XPATH, '(//button[@type="button"])[8]')
    DROPDOWN_CHECKBOX = (By.XPATH, 'input[type=\"checkbox\"]')
    CONFERENCE_PANEL = (By.LINK_TEXT, 'Conference Information')
    PROCEEDINGS_TAB = (By.LINK_TEXT, 'Proceedings Information (if not published in a journal)')
    REFERENCES_TAB = (By.LINK_TEXT, 'References')
    COMMENTS_TAB = (By.LINK_TEXT, 'Additional comments')
    ARXIV_ERROR_MSG = (By.ID, 'state-arxiv_id')
    DOI_ERROR_MSG = (By.ID, 'state-doi')
    URL_ERROR_MSG = (By.ID, 'state-url')
    DATE_ERROR_MSG = (By.ID, 'state-thesis_date')


class HoldingpenLiteratureListPageLocators(object):
    RECORD_ENTRY = (By.XPATH, '//div[@class="row hp-item ng-scope"][1]')
    SHOW_ABSTRACT_BUTTON = (By.XPATH, '//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler/div[3]/a')


class HoldingpenLiteratureDetailPageLocators(object):
    PRINCIPAL_RECORD_PANEL = (By.XPATH, '(//div[@class="ng-scope"])[2]')
    SUBMISSION_PANEL = (By.XPATH, '//p[@class="text-center ng-scope"]')
    FIRST_SUBJECT_AREA = (By.XPATH, '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])[1]')
    SECOND_SUBJECT_AREA = (By.XPATH, '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])[2]')
    CONFIRMATION_MESSAGE = (By.XPATH, '//div[@class="alert ng-scope alert-accept"]')


# Author Classes
class CreateAuthorPageLocators(object):
    pass


class HoldingpenAuthorListPageLocators(object):
    pass


class HoldingpenAuthorDetailPageLocators(object):
    pass


class GeneralLocators(object):
    AUTOCOMPLETION_LIST = (By.CLASS_NAME, 'tt-suggestions')
