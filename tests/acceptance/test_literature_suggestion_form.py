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


# Components Tests
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
    show_title_bar(selenium)
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source


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
    show_title_bar(selenium)
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source


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
    show_title_bar(selenium)
    WebDriverWait(selenium, 10).until(EC.text_to_be_present_in_element((By.XPATH, '(//div[@class="alert alert-success alert-form-success"])'), 'The INSPIRE staff will review it and your changes will be added to INSPIRE.'))
    assert 'The INSPIRE staff will review it and your changes will be added to INSPIRE.' in selenium.page_source


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
