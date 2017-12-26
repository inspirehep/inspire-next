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
from selenium.webdriver.support.ui import Select, WebDriverWait

from ..arsenic import Arsenic, ArsenicResponse
from ..EC import TryClick


SUBMIT_BUTTON = '//div[@id="webdeposit_form_accordion"]/div[4]/span/button'
SUBMIT_RESULT_ALERT_SUCCESS = (
    '(//div[@class="alert alert-success alert-form-success"])'
)
SUBMIT_RESULT_ALERT_CHAPTER_SUCCESS = (
    '(//div[@class="alert alert-warning alert-form-warning"])'
)
SUBJECTS_BUTTON = '(//button[@type="button"])[8]'
SUBJECT_ACCELERATORS = 'input[type=\"checkbox\"]'
EXPAND_CONFERENCE_INFO = """
    document.evaluate(
        "//div[@id='webdeposit_form_accordion']/div[3]/div[8]/div[1]",
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue.click()
"""
EXPAND_PROCEEDINGS_INFO = """
    document.evaluate(
        "//div[@id='webdeposit_form_accordion']/div[3]/div[9]/div[1]",
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue.click()
"""
EXPAND_REFERENCES = """
    document.evaluate(
        "//div[@id='webdeposit_form_accordion']/div[3]/div[10]/div[1]",
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue.click()
"""
EXPAND_ADDITIONAL_COMMENTS = """
    document.evaluate(
        "//div[@id='webdeposit_form_accordion']/div[3]/div[11]/div[1]",
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue.click()
"""


class InputData(object):
    def __init__(self, data=None):
        self.data = data or {}

    def __getitem__(self, key):
        return self.data[key]

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(
                '%s instance has no attribute %s' % (
                    self.__class__.__name__,
                    key,
                )
            )

    def __contains__(self, key):
        return key in self.data


    def _add_all(self, **kwargs):
        self.data.update(kwargs)

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def add_thesis_info(
        self,
        defense_date,
        degree_type,
        institution,
        supervisor_affiliation,
        supervisor_name,
        thesis_date,
    ):
        self._add_all(
            defense_date=defense_date,
            degree_type=degree_type,
            institution=institution,
            supervisor_affiliation=supervisor_affiliation,
            supervisor_name=supervisor_name,
            thesis_date=thesis_date,
        )

    def add_links(self, pdf_url):
        self.data['pdf_url'] = pdf_url

    def add_basic_info(
        self,
        abstract,
        title,
        language,
        title_translation,
        collaboration,
        experiment,
        authors=(),
        report_numbers=(),
        subjects=(),
    ):
        self._add_all(
            abstract=abstract,
            collaboration=collaboration,
            experiment=experiment,
            language=language,
            title=title,
            title_translation=title_translation,
            authors=authors,
            report_numbers=report_numbers,
            subjects=subjects,
        )

    def add_book_info(
        self,
        book_title,
        book_volume,
        publication_date,
        publication_place,
        publisher_name,
    ):
        self._add_all(
            book_title=book_title,
            book_volume=book_volume,
            publication_date=publication_date,
            publication_place=publication_place,
            publisher_name=publisher_name,
        )

    def add_book_chapter_info(self, book_title, page_start, page_end):
        self._add_all(
            book_title=book_title,
            page_start=page_start,
            page_end=page_end,
        )

    def add_journal_info(
        self,
        journal_title,
        volume,
        issue,
        year,
        page_range,
        conf_name,
    ):
        self._add_all(
            journal_title=journal_title,
            volume=volume,
            issue=issue,
            year=year,
            page_range=page_range,
            conf_name=conf_name,
        )

    def add_references_comments(self, references, extra_comments):
        self._add_all(
            references=references,
            extra_comments=extra_comments,
        )

    def add_proceedings(self, nonpublic_note):
        self._add_all(nonpublic_note=nonpublic_note)


def go_to():
    Arsenic().get(os.environ['SERVER_NAME'] + '/literature/new')


def submit_article(input_data):
    def _assert_has_no_errors():
        result = (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_SUCCESS)
            )
        ).text
        assert result

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('article')
    _populate_links(input_data)
    _populate_basic_info(input_data)
    _populate_thesis_info(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_thesis(input_data):
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_SUCCESS)
            )
        ).text
        assert (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('thesis')
    _populate_links(input_data)
    _deprecated_populate_basic_info(input_data)
    _populate_thesis_info(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_book(input_data):
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_SUCCESS)
            )
        ).text

        assert (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('book')
    _populate_links(input_data)
    _deprecated_populate_basic_info(input_data)
    _populate_book_info(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_chapter(input_data):
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_CHAPTER_SUCCESS)
            )
        ).text

        assert (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('chapter')
    _populate_links(input_data)
    _populate_chapter_info(input_data)
    _deprecated_populate_basic_info(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_journal_article_with_proceeding(input_data):
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_SUCCESS)
            )
        ).text

        assert (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_links(input_data)
    _deprecated_populate_basic_info(input_data)
    _populate_proceedings(input_data)
    _populate_journal_conference(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_journal_article(input_data):
    def _assert_has_no_errors():
        message = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, SUBMIT_RESULT_ALERT_SUCCESS)
            )
        ).text
        assert (
            'The INSPIRE staff will review it and your changes will be added '
            'to INSPIRE.'
        ) in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_links(input_data)
    _deprecated_populate_basic_info(input_data)
    _populate_journal_conference(input_data)
    _populate_references_comment(input_data)
    Arsenic().find_element_by_xpath(SUBMIT_BUTTON).click()
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def _populate_thesis_info(input_data):
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((By.ID, 'supervisors-0-name'))
    )
    Arsenic().find_element_by_id('supervisors-0-name').send_keys(
        input_data['supervisor']
    )
    Arsenic().find_element_by_id('supervisors-0-affiliation').send_keys(
        input_data['supervisor-affiliation']
    )
    Arsenic().find_element_by_id('thesis_date').send_keys(
        input_data['thesis-date']
    )
    Arsenic().find_element_by_id('defense_date').send_keys(
        input_data['defense-date']
    )
    Select(Arsenic().find_element_by_id('degree_type')).select_by_value(
        input_data['degree-type']
    )
    Arsenic().find_element_by_id('institution').send_keys(
        input_data['institution']
    )


def _populate_book_info(input_data):
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((By.ID, 'series_title'))
    )
    Arsenic().find_element_by_id('publisher_name').send_keys(
        input_data['publisher-name']
    )
    Arsenic().find_element_by_id('publication_date').send_keys(
        input_data['publication-date']
    )
    Arsenic().find_element_by_id('publication_place').send_keys(
        input_data['publication-place']
    )
    Arsenic().find_element_by_id('series_title').send_keys(
        input_data['book-title']
    )
    Arsenic().find_element_by_id('series_volume').send_keys(
        input_data['book-volume']
    )


def _populate_chapter_info(input_data):
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((By.ID, 'book_title'))
    )
    Arsenic().find_element_by_id('book_title').send_keys(
        input_data['book-title']
    )
    Arsenic().find_element_by_id('start_page').send_keys(
        input_data['page-start']
    )
    Arsenic().find_element_by_id('end_page').send_keys(
        input_data['page-end']
    )


def _populate_links(input_data):
    if 'pdf-1' in input_data:
        Arsenic().find_element_by_id('url').send_keys(input_data['pdf-1'])


def _populate_basic_info(input_data):
    if 'title' in input_data:
        Arsenic().find_element_by_id('title').send_keys(input_data['title'])

    if 'language' in input_data:
        Select(Arsenic().find_element_by_id('language')).select_by_value(
            input_data['language']
        )

    if 'title_translation' in input_data:
        Arsenic().find_element_by_id('title_translation').send_keys(
            input_data['title_translation']
        )

    _populate_subjects(input_data.get('subjects', []))
    _populate_authors(input_data.get('authors', []))

    if 'collaboration' in input_data:
        try:
            Arsenic().find_element_by_id('collaboration').send_keys(
                input_data['collaboration']
            )
        except (ElementNotVisibleException, WebDriverException):
            pass

    if 'experiment' in input_data:
        Arsenic().find_element_by_id('experiment').send_keys(
            input_data['experiment']
        )

    if 'abstract' in input_data:
        Arsenic().find_element_by_id('abstract').send_keys(
            input_data['abstract']
        )

    _populate_report_numbers(input_data.get('report_numbers', []))


def _deprecated_populate_basic_info(input_data):
    Arsenic().find_element_by_id('title').send_keys(input_data['title'])
    Select(Arsenic().find_element_by_id('language')).select_by_value(
        input_data['language']
    )
    Arsenic().find_element_by_id('title_translation').send_keys(
        input_data['title_translation']
    )

    Arsenic().find_element_by_xpath('(//button[@type="button"])[8]').click()
    Arsenic().find_element_by_css_selector('input[type=\"checkbox\"]').click()
    Arsenic().find_element_by_xpath(
        '//input[@value="' + input_data['subject'] + '"]'
    ).click()

    Arsenic().find_element_by_xpath('(//button[@type="button"])[8]').click()
    Arsenic().find_element_by_id('authors-0-name').send_keys(
        input_data['author-0']
    )
    Arsenic().find_element_by_id('authors-0-affiliation').send_keys(
        input_data['author-0-affiliation']
    )
    Arsenic().find_element_by_link_text('Add another author').click()
    Arsenic().find_element_by_id('authors-1-name').send_keys(
        input_data['author-1']
    )
    Arsenic().find_element_by_id('authors-1-affiliation').send_keys(
        input_data['author-1-affiliation']
    )

    try:
        Arsenic().find_element_by_id('collaboration').send_keys(
            input_data['collaboration']
        )
    except (ElementNotVisibleException, WebDriverException):
        pass

    Arsenic().find_element_by_id('experiment').send_keys(
        input_data['experiment']
    )
    Arsenic().find_element_by_id('abstract').send_keys(
        input_data['abstract']
    )
    Arsenic().find_element_by_id('report_numbers-0-report_number').send_keys(
        input_data['report-number-0']
    )
    Arsenic().find_element_by_link_text('Add another report number').click()
    Arsenic().find_element_by_id('report_numbers-1-report_number').send_keys(
        input_data['report-number-1']
    )


def _populate_journal_conference(input_data):
    Arsenic().find_element_by_id('journal_title').send_keys(
        input_data['journal_title']
    )
    Arsenic().find_element_by_id('volume').send_keys(input_data['volume'])
    Arsenic().find_element_by_id('issue').send_keys(input_data['issue'])
    Arsenic().find_element_by_id('year').send_keys(input_data['year'])
    Arsenic().find_element_by_id('page_range_article_id').send_keys(
        input_data['page-range-article']
    )

    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.ID, 'conf_name'))).send_keys(input_data['conf-name'])


def _populate_proceedings(input_data):
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.ID, 'nonpublic_note')
        )
    ).send_keys(input_data['non-public-note'])


def _populate_references_comment(input_data):
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located(
            (By.ID, 'references')
        )
    ).send_keys(input_data['references'])

    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((By.ID, 'extra_comments'))
    ).send_keys(input_data['extra-comments'])


def write_pdf_link(pdf_link):
    try:
        WebDriverWait(Arsenic(), 5).until(
            EC.visibility_of_element_located((By.ID, 'url'))
        )
    except (ElementNotVisibleException, WebDriverException):
        _skip_import_data()
    field = WebDriverWait(Arsenic(), 5).until(
        EC.visibility_of_element_located((By.ID, 'url'))
    )
    field.send_keys(pdf_link)
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-url', 5, 5)
    try:
        message_err = WebDriverWait(Arsenic(), 10).until(
            EC.visibility_of_element_located((By.ID, 'state-url'))
        ).text
    except (ElementNotVisibleException, WebDriverException):
        message_err = ''
    Arsenic().show_title_bar()
    field.clear()

    def _assert_has_errors():
        assert (
            'Please, provide an accessible direct link to a PDF document.'
        ) in message_err

    def _assert_has_no_errors():
        assert (
            'Please, provide an accessible direct link to a PDF document.'
        ) not in message_err

    return ArsenicResponse(
        assert_has_errors_func=_assert_has_errors,
        assert_has_no_errors_func=_assert_has_no_errors,
    )


def write_date_thesis(date_field, error_message_id, date):
    try:
        WebDriverWait(Arsenic(), 5).until(
            EC.visibility_of_element_located((By.ID, date_field))
        )
    except (ElementNotVisibleException, WebDriverException):
        _skip_import_data()
        _populate_document_type('thesis')

    field = WebDriverWait(Arsenic(), 5).until(
        EC.visibility_of_element_located((By.ID, date_field))
    )
    field.send_keys(date)
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-supervisors', 5, 5)
    try:
        error_message = WebDriverWait(Arsenic(), 5).until(
            EC.visibility_of_element_located((By.ID, error_message_id))
        ).text
    except (ElementNotVisibleException, WebDriverException):
        error_message = ''
    Arsenic().show_title_bar()
    field.clear()

    def _assert_has_errors():
        return (
            'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM '
            'or YYYY.'
        ) in error_message

    def _assert_has_no_errors():
        return (
            'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM '
            'or YYYY.'
        ) not in error_message

    return ArsenicResponse(
        assert_has_errors_func=_assert_has_errors,
        assert_has_no_errors_func=_assert_has_no_errors,
    )


def write_institution_thesis(institution, expected_data):
    def _assert_has_no_errors():
        assert (
            expected_data == Arsenic().write_in_autocomplete_field(
                'supervisors-0-affiliation',
                institution,
            )
        )

    _skip_import_data()
    _populate_document_type('thesis')
    WebDriverWait(Arsenic(), 5).until(
        EC.visibility_of_element_located((By.ID, 'supervisors-0-affiliation'))
    )
    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def write_conference(conference_title, expected_data):
    def _assert_has_no_errors():
        assert (
            expected_data in Arsenic().write_in_autocomplete_field(
                'conf_name',
                conference_title,
            )
        )

    _skip_import_data()
    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def write_journal_title(journal_title, expected_data):
    def _assert_has_no_errors():
        assert (
            expected_data in Arsenic().write_in_autocomplete_field(
                'journal_title',
                journal_title,
            )
        )

    _skip_import_data()
    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def write_affiliation(affiliation, expected_data):
    def _assert_has_no_errors():
        assert (
            expected_data == Arsenic().write_in_autocomplete_field(
                'authors-0-affiliation',
                affiliation,
            )
        )

    _skip_import_data()
    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_arxiv_id(arxiv_id, expected_data):
    Arsenic().find_element_by_id('arxiv_id').send_keys(arxiv_id)
    WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((By.ID, 'importData'))
    ).click()
    WebDriverWait(Arsenic(), 20).until(
        EC.visibility_of_element_located((By.ID, 'acceptData'))
    ).click()
    WebDriverWait(Arsenic(), 20).until(
        EC.visibility_of_element_located((By.ID, 'arxiv_id'))
    )
    _skip_import_data()

    output_data = {
        'doi': Arsenic().find_element_by_id('doi').get_attribute('value'),
        'year': Arsenic().find_element_by_id('year').get_attribute('value'),
        'issue': Arsenic().find_element_by_id('issue').get_attribute('value'),
        'title': Arsenic().find_element_by_id('title').get_attribute('value'),
        'volume': Arsenic().find_element_by_id('volume').get_attribute(
            'value'
        ),
        'abstract': Arsenic().find_element_by_id('abstract').get_attribute(
            'value'
        ),
        'author': Arsenic().find_element_by_id('authors-0-name').get_attribute(
            'value'
        ),
        'journal': Arsenic().find_element_by_id('journal_title').get_attribute(
            'value'
        ),
        'page-range': Arsenic().find_element_by_id(
            'page_range_article_id'
        ).get_attribute('value')
    }

    def _assert_has_no_errors():
        return expected_data == output_data

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_doi_id(doi_id, expected_data):
    Arsenic().find_element_by_id('doi').send_keys(doi_id)
    Arsenic().find_element_by_id('importData').click()
    WebDriverWait(Arsenic(), 20).until(
        EC.visibility_of_element_located((By.ID, 'acceptData'))
    ).click()
    WebDriverWait(Arsenic(), 20).until(
        EC.visibility_of_element_located((By.ID, 'doi'))
    )
    _skip_import_data()

    output_data = {
        'year': Arsenic().find_element_by_id('year').get_attribute('value'),
        'title': Arsenic().find_element_by_id('title').get_attribute('value'),
        'issue': Arsenic().find_element_by_id('issue').get_attribute('value'),
        'volume': Arsenic().find_element_by_id('volume').get_attribute(
            'value'
        ),
        'journal': Arsenic().find_element_by_id('journal_title').get_attribute(
            'value'
        ),
        'author': Arsenic().find_element_by_id('authors-0-name').get_attribute(
            'value'
        ),
        'author-1': Arsenic().find_element_by_id(
            'authors-1-name'
        ).get_attribute('value'),
        'author-2': Arsenic().find_element_by_id(
            'authors-2-name'
        ).get_attribute('value'),
        'page-range': Arsenic().find_element_by_id(
            'page_range_article_id'
        ).get_attribute('value')
    }

    def _assert_has_no_errors():
        assert expected_data == output_data

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def _skip_import_data():
    Arsenic().hide_title_bar()
    WebDriverWait(Arsenic(), 10).until(
        TryClick((By.ID, 'skipImportData'))
    ).click()
    WebDriverWait(Arsenic(), 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, 'form_container'),
            'Type of Document',
        )
    )
    Arsenic().execute_script(EXPAND_CONFERENCE_INFO)
    Arsenic().execute_script(EXPAND_PROCEEDINGS_INFO)
    Arsenic().execute_script(EXPAND_REFERENCES)
    Arsenic().execute_script(EXPAND_ADDITIONAL_COMMENTS)
    Arsenic().show_title_bar()


def _populate_document_type(document_type):
    Select(Arsenic().find_element_by_id('type_of_doc')).select_by_value(
        document_type
    )


def _populate_subjects(subjects):

    Arsenic().find_element_by_xpath(SUBJECTS_BUTTON).click()
    Arsenic().find_element_by_css_selector(SUBJECT_ACCELERATORS).click()
    for subject in subjects:
        Arsenic().find_element_by_xpath(
            '//input[@value="' + subject + '"]'
        ).click()

    Arsenic().find_element_by_xpath(SUBJECTS_BUTTON).click()


def _populate_authors(authors):
    for index, author in enumerate(authors):
        Arsenic().find_element_by_id('authors-%s-name' % index).send_keys(
            author['name']
        )
        if 'affiliation' in author:
            Arsenic().find_element_by_id(
                'authors-%s-affiliation' % index
            ).send_keys(
                author['affiliation'],
                author['name'],
            )

        Arsenic().find_element_by_link_text('Add another author').click()


def _populate_report_numbers(report_numbers):
    for index, report_number in enumerate(report_numbers):
        Arsenic().find_element_by_id(
            'report_numbers-%s-report_number' % index
        ).send_keys(report_number)
        Arsenic().find_element_by_link_text(
            'Add another report number'
        ).click()
