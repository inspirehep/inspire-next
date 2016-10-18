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
from selenium.webdriver.common.action_chains import ActionChains


# Components Tests
def test_import_from_arXiv(selenium, login):
    """Test the import from arXiv"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("arxiv_id").send_keys("hep-th/9711200")
    selenium.find_element_by_id("importData").click()
    WebDriverWait(selenium, 20).until(EC.visibility_of_element_located((By.ID, "acceptData"))).click()

    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "arxiv_id")))
    assert '10.1023/A:1026654312961' in selenium.find_element_by_id('doi').get_attribute('value')
    assert 'The Large N Limit of Superconformal Field Theories and Supergravity' in selenium.find_element_by_id('title').get_attribute('value')
    assert 'Maldacena, Juan' in selenium.find_element_by_id('authors-0-name').get_attribute('value')
    assert 'We show that the large $N$ limit of certain conformal field theories in' in selenium.find_element_by_id('abstract').get_attribute('value')
    assert 'International Journal of Theoretical Physics' in selenium.find_element_by_id('journal_title').get_attribute('value')
    assert '38' in selenium.find_element_by_id('volume').get_attribute('value')
    assert '4' in selenium.find_element_by_id('issue').get_attribute('value')
    assert '1999' in selenium.find_element_by_id('year').get_attribute('value')
    assert '1113-1133' in selenium.find_element_by_id('page_range_article_id').get_attribute('value')


def test_import_from_doi(selenium, login):
    """Test the import from doi"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("doi").send_keys("10.1086/305772")
    selenium.find_element_by_id("importData").click()
    WebDriverWait(selenium, 20).until(EC.visibility_of_element_located((By.ID, "acceptData"))).click()

    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "arxiv_id")))
    assert 'Maps of Dust Infrared Emission for Use in Estimation of Reddening and Cosmic Microwave Background Radiation Foregrounds' in selenium.find_element_by_id('title').get_attribute('value')
    assert 'Schlegel, David J.' in selenium.find_element_by_id('authors-0-name').get_attribute('value')
    assert 'Finkbeiner, Douglas P.' in selenium.find_element_by_id('authors-1-name').get_attribute('value')
    assert 'Davis, Marc' in selenium.find_element_by_id('authors-2-name').get_attribute('value')
    assert 'The Astrophysical Journal' in selenium.find_element_by_id('journal_title').get_attribute('value')
    assert '500' in selenium.find_element_by_id('volume').get_attribute('value')
    assert '2' in selenium.find_element_by_id('issue').get_attribute('value')
    assert '1998' in selenium.find_element_by_id('year').get_attribute('value')
    assert '525-553' in selenium.find_element_by_id('page_range_article_id').get_attribute('value')


def test_import_from_doi_arXiv(selenium, login):
    """Test the import from doi and arXiv"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("arxiv_id").send_keys("1207.7235")
    selenium.find_element_by_id("doi").send_keys("10.1086/305772")
    selenium.find_element_by_id("importData").click()
    WebDriverWait(selenium, 20).until(EC.visibility_of_element_located((By.ID, "acceptData"))).click()

    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "arxiv_id")))
    assert 'Maps of Dust Infrared Emission for Use in Estimation of Reddening and Cosmic Microwave Background Radiation Foregrounds' in selenium.find_element_by_id('title').get_attribute('value')
    assert 'Schlegel, David J.' in selenium.find_element_by_id('authors-0-name').get_attribute('value')
    assert 'Finkbeiner, Douglas P.' in selenium.find_element_by_id('authors-1-name').get_attribute('value')
    assert 'Davis, Marc' in selenium.find_element_by_id('authors-2-name').get_attribute('value')
    assert 'Results are presented from searches for the standard model Higgs boson in' in selenium.find_element_by_id('abstract').get_attribute('value')
    assert 'The Astrophysical Journal' in selenium.find_element_by_id('journal_title').get_attribute('value')
    assert '500' in selenium.find_element_by_id('volume').get_attribute('value')
    assert '2' in selenium.find_element_by_id('issue').get_attribute('value')
    assert '1998' in selenium.find_element_by_id('year').get_attribute('value')
    assert '525-553' in selenium.find_element_by_id('page_range_article_id').get_attribute('value')


def test_format_input_arXiv(selenium, login):
    """Test the string format for arXiv input"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')

    try:
        selenium.find_element_by_id("arxiv_id").send_keys("1001.4538")
        selenium.find_element_by_id("arxiv_id").send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-arxiv_id")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "The provided ArXiv ID is invalid - it should look" not in selenium.page_source
    selenium.find_element_by_id("arxiv_id").clear()

    selenium.find_element_by_id("arxiv_id").send_keys("hep-th.9711200")
    selenium.find_element_by_id("arxiv_id").send_keys(Keys.TAB)
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "state-arxiv_id"), "The provided ArXiv ID is invalid - it should look"))
    assert "The provided ArXiv ID is invalid - it should look" in selenium.page_source
    selenium.find_element_by_id("arxiv_id").clear()

    try:
        selenium.find_element_by_id("arxiv_id").send_keys("hep-th/9711200")
        selenium.find_element_by_id("arxiv_id").send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-arxiv_id")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "The provided ArXiv ID is invalid - it should look" not in selenium.page_source


def test_format_input_DOI(selenium, login):
    """Test the string format for DOI input"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')

    try:
        selenium.find_element_by_id("doi").send_keys("10.1086/305772")
        selenium.find_element_by_id("doi").send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-doi")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "The provided DOI is invalid - it should look" not in selenium.page_source
    selenium.find_element_by_id("doi").clear()

    selenium.find_element_by_id("doi").send_keys("dummy:10.1086/305772")
    selenium.find_element_by_id("doi").send_keys(Keys.TAB)
    WebDriverWait(selenium, 20).until(EC.text_to_be_present_in_element((By.ID, "state-doi"), "The provided DOI is invalid - it should look"))
    assert "The provided DOI is invalid - it should look" in selenium.page_source
    selenium.find_element_by_id("doi").clear()

    try:
        selenium.find_element_by_id("doi").send_keys("doi:10.1086/305772")
        selenium.find_element_by_id("doi").send_keys(Keys.TAB)
        WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.ID, "state-doi")))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "The provided DOI is invalid - it should look" not in selenium.page_source


def test_basic_info_autocomplete_affilation(selenium, login):
    """Test the autocompletion for the affilation in the basic info section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    field = selenium.find_element_by_id('authors-0-affiliation')
    field.send_keys("oxf")
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
    assert 'Oxford U.' in field.get_attribute('value')


def test_journal_info_autocomplete_title(selenium, login):
    """Test the autocompletion for the title in the journal info section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    field = selenium.find_element_by_id('journal_title')
    field.send_keys("Nuc")
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
    assert 'Nuclear Physics' in field.get_attribute('value')


def test_conference_info_autocomplete_title(selenium, login):
    """Test the autocompletion for the title in the conference info section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Conference Information'))
    selenium.find_element_by_link_text("Conference Information").click()
    field = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "conf_name")))
    field.send_keys("sos")
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
    show_title_bar(selenium)
    assert 'IN2P3 School of Statistics, 2012-05-28, Autrans, France' in field.get_attribute('value')


def test_thesis_info_autocomplete_institution_supervisor(selenium, login):
    """Test the autocompletion for the supervisor institution in the thesis section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    Select(selenium.find_element_by_id('type_of_doc')).select_by_value('thesis')
    field = selenium.find_element_by_id('authors-0-affiliation')
    field.send_keys("cer")
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
    assert 'CERN' in field.get_attribute('value')


def test_thesis_info_autocomplete_institution(selenium, login):
    """Test the autocompletion for the institution in the thesis section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    Select(selenium.find_element_by_id('type_of_doc')).select_by_value('thesis')
    field = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "institution")))
    field.send_keys("cer")
    WebDriverWait(selenium, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
    assert 'CERN' in field.get_attribute('value')


def test_pdf_link(selenium, login):
    """Test the autocompletion for the institution in the thesis section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, 'form_container'), 'Type of Document'))

    field = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'url')))
    field.send_keys('pdf_url_correct')
    field.send_keys(Keys.TAB)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, 'state-url'), 'Please, provide an accessible direct link to a PDF document.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'Please, provide an accessible direct link to a PDF document.' not in selenium.page_source
    field.clear()

    field = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'url')))
    field.send_keys('pdf_url_wrong')
    field.send_keys(Keys.TAB)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, 'state-url'), 'Please, provide an accessible direct link to a PDF document.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert 'Please, provide an accessible direct link to a PDF document.' in selenium.page_source


def test_thesis_info_date_submission(selenium, login):
    """Test the format for the submission date in the thesis section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    Select(selenium.find_element_by_id('type_of_doc')).select_by_value('thesis')
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Date of Submission'))
    field = selenium.find_element_by_id('defense_date')
    _date_format_controls(field, selenium, 'state-defense_date')
    show_title_bar(selenium)


def test_thesis_info_date_defence(selenium, login):
    """Test the format for the defense date in the thesis section"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Type of Document'))
    Select(selenium.find_element_by_id('type_of_doc')).select_by_value('thesis')
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"), 'Date of Submission'))
    field = selenium.find_element_by_id('thesis_date')
    _date_format_controls(field, selenium, 'state-thesis_date')
    show_title_bar(selenium)


def _date_format_controls(field, selenium, id_message_error):
    field.send_keys("")
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." not in selenium.page_source
    field.clear()

    field.send_keys('wrong')
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." in selenium.page_source
    field.clear()

    field.send_keys("2016-01")
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." not in selenium.page_source
    field.clear()

    field.send_keys("2016-02-30")
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." in selenium.page_source
    field.clear()

    field.send_keys("2016")
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." not in selenium.page_source

    field.send_keys("2016-13")
    _click_outside_the_field(selenium)
    try:
        WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, id_message_error), 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'))
    except (ElementNotVisibleException, WebDriverException):
        pass
    assert "Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY." in selenium.page_source
    field.clear()


def _click_outside_the_field(selenium):
    el = selenium.find_element_by_id('state-group-supervisors')
    action = ActionChains(selenium)
    action.move_to_element_with_offset(el, 5, 5)
    action.click()
    action.perform()


# Form Tests
def test_literature_create_article_journal_manually(selenium, login):
    """Submit the form for article creation from scratch"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"),'Type of Document'))
    _links_population(selenium)
    _basic_info_population(selenium)
    _journal_population(selenium)
    _conference_population(selenium)
    _references_population(selenium)
    _comments_population(selenium)
    selenium.find_element_by_xpath("//div[@id='webdeposit_form_accordion']/div[4]/span/button").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source
    _back_office_article(selenium)
    show_title_bar(selenium)


def test_literature_create_article_proceeding_manually(selenium, login):
    """Submit the form for article creation from scratch"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"),'Type of Document'))
    _links_population(selenium)
    _basic_info_population(selenium)
    _conference_population(selenium)
    _proceedings_population(selenium)
    _references_population(selenium)
    _comments_population(selenium)
    selenium.find_element_by_xpath("//div[@id='webdeposit_form_accordion']/div[4]/span/button").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source
    _back_office_article(selenium)
    show_title_bar(selenium)

def test_literature_create_thesis_manually(selenium, login):
    """Submit the form for thesis creation from scratch"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/literature/create')
    hide_title_bar(selenium)
    selenium.find_element_by_id("skipImportData").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.ID, "form_container"),'Type of Document'))
    Select(selenium.find_element_by_id('type_of_doc')).select_by_value('thesis')
    _populate_thesis_field(selenium)
    _links_population(selenium)
    _basic_info_population(selenium)
    _references_population(selenium)
    _comments_population(selenium)
    selenium.find_element_by_xpath("//div[@id='webdeposit_form_accordion']/div[4]/span/button").click()
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source
    _back_office_article(selenium)
    show_title_bar(selenium)


def _links_population(selenium):
    selenium.find_element_by_id("url").send_keys("pdf_url_correct")
    selenium.find_element_by_id("additional_url").send_keys("pdf_another_url_correct")
    selenium.find_element_by_link_text("Links").click()


def _basic_info_population(selenium):
    selenium.find_element_by_id("title").send_keys("My Title For Test")
    Select(selenium.find_element_by_id("language")).select_by_value("rus")
    selenium.find_element_by_id("title_translation").send_keys("My Title was in Rdsaussian")
    selenium.find_element_by_xpath("(//button[@type='button'])[8]").click()
    selenium.find_element_by_css_selector("input[type=\"checkbox\"]").click()
    selenium.find_element_by_xpath("//input[@value='Computing']").click()
    selenium.find_element_by_xpath("(//button[@type='button'])[8]").click()
    selenium.find_element_by_id("authors-0-name").send_keys("Mister White")
    selenium.find_element_by_id("authors-0-affiliation").send_keys("Wisconsin U., Madison")
    selenium.find_element_by_link_text("Add another author").click()
    selenium.find_element_by_id("authors-1-name").send_keys("Mister Brown")
    selenium.find_element_by_id("authors-1-affiliation").send_keys("CERN")

    try:
        selenium.find_element_by_id("collaboration").send_keys("This is a collaboration")
    except (ElementNotVisibleException, WebDriverException):
        pass

    selenium.find_element_by_id("experiment").send_keys("This is a collaboration")
    selenium.find_element_by_id("abstract").send_keys("Lorem ipsum dolor sit amet, consetetur sadipscing elitr.")
    selenium.find_element_by_id("report_numbers-0-report_number").send_keys("100")
    selenium.find_element_by_link_text("Add another report number").click()
    selenium.find_element_by_id("report_numbers-1-report_number").send_keys("101")
    selenium.find_element_by_link_text("Basic Information").click()


def _populate_thesis_field(selenium):
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "supervisors-0-name")))
    selenium.find_element_by_id("supervisors-0-name").send_keys("Mister Yellow")
    selenium.find_element_by_id("supervisors-0-affiliation").send_keys("CERN")
    selenium.find_element_by_id("thesis_date").send_keys("2016-09-27")
    selenium.find_element_by_id("defense_date").send_keys("2016-09-27")
    Select(selenium.find_element_by_id("degree_type")).select_by_value("Bachelor")
    selenium.find_element_by_id("institution").send_keys("Wisconsin U., Madison")
    selenium.find_element_by_link_text("Thesis Information").click()


def _journal_population(selenium):
    selenium.find_element_by_id("journal_title").send_keys("europ")
    selenium.find_element_by_id("volume").send_keys("Volume")
    selenium.find_element_by_id("issue").send_keys("issue")
    selenium.find_element_by_id("year").send_keys("2014")
    selenium.find_element_by_id("page_range_article_id").send_keys("100-110")
    selenium.find_element_by_link_text("Journal Information").click()


def _conference_population(selenium):
    selenium.find_element_by_link_text("Conference Information").click()
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "conf_name"))).send_keys("This Conference")


def _proceedings_population(selenium):
    selenium.execute_script("""document.evaluate("//div[@id='webdeposit_form_accordion']/div[3]/div[7]/div[1]",
                               document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()""")
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "nonpublic_note"))).send_keys("This proceedings")


def _references_population(selenium):
    selenium.execute_script("""document.evaluate("//div[@id='webdeposit_form_accordion']/div[3]/div[8]/div[1]",
                               document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()""")
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "references"))).send_keys("references")


def _comments_population(selenium):
    selenium.execute_script("""document.evaluate("//div[@id='webdeposit_form_accordion']/div[3]/div[9]/div[1]",
                               document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()""")
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, "extra_comments"))).send_keys("comments about the document")


def hide_title_bar(selenium):
    selenium.execute_script('document.getElementById("collections-section").style.display = "none"')
    selenium.execute_script('document.getElementById("topnav").style.display = "none"')


def show_title_bar(selenium):
    selenium.execute_script('document.getElementById("collections-section").style.display = ""')
    selenium.execute_script('document.getElementById("topnav").style.display = ""')


def _back_office_article(selenium):
    # list page
    record = _load_entries(selenium)
    assert 'Computing' in record
    assert 'Accelerators' in record
    assert 'My Title For Test' in record
    assert 'admin@inspirehep.net' in record
    assert 'Mister White; Mister Brown' in record
    assert 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.' in record
    assert 'found.' in WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="invenio-search-results"]/ng-pluralize'))).text
    selenium.find_element_by_xpath('//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler').click()
    # back office
    record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="ng-scope"])[2]'))).text
    assert 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.' in record
    assert 'Wisconsin U., Madison' in record
    assert 'My Title For Test' in record
    assert 'Mister Brown' in record
    assert 'Mister White' in record
    assert 'CERN' in record
    assert 'Submitted by admin@inspirehep.net\non' in WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//p[@class="text-center ng-scope"]'))).text
    assert 'Accelerators' in WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])[1]'))).text
    assert 'Computing' in WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '(//div[@class="col-md-9 col-sm-9 col-xs-8 ng-binding"])[2]'))).text
    selenium.find_element_by_xpath('//button[@class="btn btn-warning"]').click()
    assert 'Accepted as Non-CORE' in WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="alert ng-scope alert-accept"]'))).text


def _load_entries(selenium):
    try:
        selenium.get(os.environ['SERVER_NAME'] + '/holdingpen/list/?page=1&size=10&source=submission&workflow_name=HEP&status=HALTED')
        WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="row hp-item ng-scope"][1]/div/div/div[2]/holding-pen-template-handler/div[3]/a'))).click()
        record = WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="row hp-item ng-scope"][1]'))).text
    except (ElementNotVisibleException, WebDriverException):
        record = _load_entries(selenium)
    return record
