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

import pytest

from pytest_bdd import scenario, when, then, parsers
from selenium.common.exceptions import (
    ElementNotVisibleException,
    WebDriverException,
)

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from inspirehep.bat.locators import CreateLiteraturePageLocators as CL
from inspirehep.bat.locators import HoldingpenLiteratureListPageLocators as HL
from inspirehep.bat.locators import HoldingpenLiteratureDetailPageLocators as HD
from inspirehep.bat.steps.given import *
from inspirehep.bat.steps.when import *
from inspirehep.bat.steps.then import *


@pytest.fixture
def pytestbdd_strict_gherkin():
    return False


@scenario('literature_suggestion.feature', 'Submit article and verify entry in the list page')
def test_verify_article_record_in_the_list_page():
    pass


@scenario('literature_suggestion.feature', 'Submit article and verify record detail in the detail page')
def test_verify_article_record_in_the_detail_page():
    pass


@scenario('literature_suggestion.feature', 'Accept article and verify the confirmation message')
def test_verify_accepted_article():
    pass


@scenario('literature_suggestion.feature', 'Using the autocomplete for the supervisor institution')
def test_autocomplete_supervisor_institution():
    pass


@scenario('literature_suggestion.feature', 'Using the autocomplete for the journal title')
def test_autocomplete_journal_title():
    pass


@scenario('literature_suggestion.feature', 'Using the autocomplete for the conference title')
def test_autocomplete_conference_title():
    pass


@scenario('literature_suggestion.feature', 'Using the autocomplete for the affilitaion')
def test_autocomplete_affilation():
    pass


@scenario('literature_suggestion.feature', 'Import an article using the arXiv id')
def test_import_from_arxiv():
    pass


@scenario('literature_suggestion.feature', 'Import an article using the DOI id')
def test_import_from_doi():
    pass


@scenario('literature_suggestion.feature', 'Writing the wrong arXiv id')
def test_wrong_arxiv():
    pass


@scenario('literature_suggestion.feature', 'Writing the correct arXiv id')
def test_correct_arxiv():
    pass


@scenario('literature_suggestion.feature', 'Writing the wrong DOI')
def test_wrong_doi():
    pass


@scenario('literature_suggestion.feature', 'Writing the correct DOI')
def test_correct_doi():
    pass


@scenario('literature_suggestion.feature', 'Writing a wrong url')
def test_wrong_url():
    pass


@scenario('literature_suggestion.feature', 'Writing a wrong thesis date')
def test_wrong_thesis_date():
    pass


@scenario('literature_suggestion.feature', 'Writing a correct thesis date')
def test_correct_thesis_date():
    pass


@scenario('literature_suggestion.feature', 'Writing a correct url')
def test_correct_url():
    pass


@scenario('literature_suggestion.feature', 'Submit thesis and verify entry in the list page')
def test_verify_thesis_record_in_the_list_page():
    pass


@scenario('literature_suggestion.feature', 'Submit thesis and verify record detail in the Holding Pen')
def test_verify_thesis_record_in_the_detail_page():
    pass


@scenario('literature_suggestion.feature', 'Accept thesis and verify the confirmation message')
def test_verify_accepted_thesis():
    pass


# when statements for create literature page
@when('I go to the literature suggestion page')
def go_to_create_literature():
    Arsenic().get(os.environ['SERVER_NAME'] + '/literature/new')


@when('I click on the submit button')
def click_submit_button():
    Arsenic().get_element_with_locator(CL.SUBMIT_BUTTON).click()


@when('I click on the accept button')
def click_accept_button():
    Arsenic().get_element_with_locator(CL.ACCEPT_BUTTON).click()


@when('I click on the button Skip, and uncollapse all panels')
def click_skip_and_fill_manually():
    Arsenic().hide_title_bar()
    Arsenic().get_element_with_locator(CL.SKIP_IMPORT_DATA, waiting_time=5).click()

    WebDriverWait(Arsenic(), 10).until(
        EC.text_to_be_present_in_element(
            CL.LITERATURE_FORM,
            'Type of Document',
        )
    )

    Arsenic().get_element_with_locator(CL.CONFERENCE_PANEL).click()
    Arsenic().get_element_with_locator(CL.PROCEEDINGS_TAB).click()
    Arsenic().get_element_with_locator(CL.REFERENCES_TAB).click()
    Arsenic().get_element_with_locator(CL.COMMENTS_TAB).click()

    Arsenic().show_title_bar()


@when(parsers.cfparse('I select the value {input_select} in the subject dropdown list'))
def select_value_in_subject_multiselect_widget(input_select):
    Arsenic().get_element_with_locator(CL.DROPDOWN_BUTTON).click()
    Arsenic().find_element_by_xpath(
        '//input[@value="' + input_select + '"]'
    ).click()
    Arsenic().get_element_with_locator(CL.DROPDOWN_BUTTON).click()


# when statements for holdingpen pages
@when('I go to the holding panel list page')
def go_to_holding_pen_literature_list():
    Arsenic().get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&status=HALTED&workflow_name=HEP')


@then('I should see the record in the list page')
def is_the_record_in_the_list_page():
    def _force_load_record(refresh_limit, refresh_counter=0):
        if refresh_limit == refresh_counter:
            return None
        refresh_counter += 1

        try:
            record = Arsenic().get_element_with_locator(HL.RECORD_ENTRY).text
        except (ElementNotVisibleException, WebDriverException):
            go_to_holding_pen_literature_list()
            record = _force_load_record(refresh_limit, refresh_counter=refresh_counter)

        return record

    record_text = _force_load_record(100)
    assert record_text is not None


# then statements for create literature page
@then(parsers.cfparse('I should see the {field} error message'))
def is_there_a_message_error(field):
    assert globals()['_is_' + field + '_error_message_present']()


@then(parsers.cfparse('I should not see the {field} error message'))
def is_not_there_a_message_error(field):
    assert not globals()['_is_' + field + '_error_message_present']()


@then('I should see the message of confirmation')
def is_the_confirmation_message_there():
    assert 'Accepted as Non-CORE' in Arsenic().get_element_with_locator(
        HD.CONFIRMATION_MESSAGE
    ).text


# then statements for holdingpen pages
@then(parsers.cfparse('I should see {value_record_entry} in the record entry'))
def is_the_record_detail_in_the_list_page(value_record_entry):
    record = Arsenic().get_element_with_locator(HL.RECORD_ENTRY).text

    assert value_record_entry in record


@then(parsers.cfparse('I should see {value_record_detail} in the record detail'))
def is_the_record_detail_in_the_detail_page(value_record_detail):
    record = Arsenic().get_element_with_locator(HD.PRINCIPAL_RECORD_PANEL).text
    record += Arsenic().get_element_with_locator(HD.SUBMISSION_PANEL).text
    record += Arsenic().get_element_with_locator(HD.FIRST_SUBJECT_AREA).text

    assert value_record_detail in record


def _is_arxiv_error_message_present():
    try:
        message_err = Arsenic().get_element_with_locator(CL.ARXIV_ERROR_MSG).text
    except (ElementNotVisibleException, WebDriverException):
        message_err = ''
    return 'The provided ArXiv ID is invalid - it should look' in message_err


def _is_doi_error_message_present():
    try:
        message_err = Arsenic().get_element_with_locator(CL.DOI_ERROR_MSG).text
    except (ElementNotVisibleException, WebDriverException):
        message_err = ''
    return 'The provided DOI is invalid - it should look' in message_err


def _is_url_error_message_present():
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-url', 5, 5)
    try:
        message_err = Arsenic().get_element_with_locator(CL.URL_ERROR_MSG).text
    except (ElementNotVisibleException, WebDriverException):
        message_err = ''
    Arsenic().show_title_bar()
    return 'Please, provide an accessible direct link to a PDF document.' in message_err


def _is_date_error_message_present():
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-supervisors', 5, 5)
    try:
        error_message = Arsenic().get_element_with_locator(CL.DATE_ERROR_MSG).text
    except (ElementNotVisibleException, WebDriverException):
        error_message = ''
    Arsenic().show_title_bar()
    return 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.' in error_message
