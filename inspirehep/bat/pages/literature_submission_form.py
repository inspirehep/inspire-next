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
from selenium.webdriver.support.ui import WebDriverWait

from inspirehep.bat.arsenic import Arsenic, ArsenicResponse
from inspirehep.bat.actions import (
    click,
    get_text_of,
    get_value_of,
    write,
    select,
    wait_for,
)


SUBMIT_BUTTON = '//div[@id="webdeposit_form_accordion"]/div[4]/span/button'
SUBMIT_RESULT_ALERT_SUCCESS = (
    '(//div[@class="alert alert-success alert-form-success"])'
)
SUBMIT_RESULT_ALERT_CHAPTER_SUCCESS = (
    '(//div[@class="alert alert-warning alert-form-warning"])'
)
SUBJECTS_BUTTON = '(//button[@type="button"])[8]'
GOOD_MESSAGE = (
    'The INSPIRE staff will review it and your changes will be added '
    'to INSPIRE.'
)
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
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('article')
    _populate_links(input_data)
    _populate_basic_info(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_thesis(input_data):
    def _assert_has_no_errors():
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('thesis')
    _populate_links(input_data)
    _populate_basic_info(input_data)
    _populate_thesis_info(input_data)
    _populate_references_comment(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_book(input_data):
    def _assert_has_no_errors():
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('book')
    _populate_links(input_data)
    _populate_basic_info(input_data)
    _populate_book_info(input_data)
    _populate_references_comment(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_chapter(input_data):
    def _assert_has_no_errors():
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_CHAPTER_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_document_type('chapter')
    _populate_links(input_data)
    _populate_chapter_info(input_data)
    _populate_basic_info(input_data)
    _populate_references_comment(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_journal_article_with_proceeding(input_data):
    def _assert_has_no_errors():
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_links(input_data)
    _populate_basic_info(input_data)
    _populate_proceedings(input_data)
    _populate_journal_conference(input_data)
    _populate_references_comment(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_journal_article(input_data):
    def _assert_has_no_errors():
        message = get_text_of(xpath=SUBMIT_RESULT_ALERT_SUCCESS)
        assert GOOD_MESSAGE in message

    _skip_import_data()
    Arsenic().hide_title_bar()
    _populate_links(input_data)
    _populate_basic_info(input_data)
    _populate_journal_conference(input_data)
    _populate_references_comment(input_data)
    click(xpath=SUBMIT_BUTTON)
    Arsenic().show_title_bar()

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def _populate_thesis_info(input_data):
    wait_for(_id='supervisors-0-name')
    write(_id='supervisors-0-name', data=input_data.supervisor_name)
    write(
        _id='supervisors-0-affiliation',
        data=input_data.supervisor_affiliation,
    )
    write(_id='thesis_date', data=input_data.thesis_date)
    write(_id='defense_date', data=input_data.defense_date)
    write(_id='degree_type', data=input_data.degree_type)
    write(_id='institution', data=input_data.institution)


def _populate_book_info(input_data):
    wait_for(_id='series_title')
    write(_id='publisher_name', data=input_data.publisher_name)
    write(_id='publication_date', data=input_data.publication_date)
    write(_id='publication_place', data=input_data.publication_place)
    write(_id='series_title', data=input_data.book_title)
    write(_id='series_volume', data=input_data.book_volume)


def _populate_chapter_info(input_data):
    wait_for(_id='book_title')
    write(_id='book_title', data=input_data.book_title)
    write(_id='start_page', data=input_data.page_start)
    write(_id='end_page', data=input_data.page_end)


def _populate_links(input_data):
    if 'pdf_url' in input_data:
        write(_id='url', data=input_data.pdf_url)


def _populate_basic_info(input_data):
    if 'title' in input_data:
        write(_id='title', data=input_data.title)

    if 'language' in input_data:
        select(_id='language', value=input_data.language)

    if 'title_translation' in input_data:
        write(_id='title_translation', data=input_data.title_translation)

    _populate_subjects(input_data.subjects)
    _populate_authors(input_data.authors)

    if 'collaboration' in input_data:
        try:
            write(_id='collaboration', data=input_data.collaboration)
        except (ElementNotVisibleException, WebDriverException):
            pass

    if 'experiment' in input_data:
        write(_id='experiment', data=input_data.experiment)

    if 'abstract' in input_data:
        write(_id='abstract', data=input_data.abstract)

    _populate_report_numbers(input_data.report_numbers)


def _populate_journal_conference(input_data):
    write(_id='journal_title', data=input_data.journal_title)
    write(_id='volume', data=input_data.volume)
    write(_id='issue', data=input_data.issue)
    write(_id='year', data=input_data.year)
    write(_id='page_range_article_id', data=input_data.page_range)
    write(_id='conf_name', data=input_data.conf_name)


def _populate_proceedings(input_data):
    write(_id='nonpublic_note', data=input_data.nonpublic_note)


def _populate_references_comment(input_data):
    write(_id='references', data=input_data.references)
    write(_id='extra_comments', data=input_data.extra_comments)


def write_pdf_link(pdf_link):
    try:
        wait_for(_id='url')
    except (ElementNotVisibleException, WebDriverException):
        _skip_import_data()
    field = wait_for(_id='url')
    field.send_keys(pdf_link)
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-url', 5, 5)
    try:
        message_err = get_text_of(_id='state-url')
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
        wait_for(_id=date_field)
    except (ElementNotVisibleException, WebDriverException):
        _skip_import_data()
        _populate_document_type('thesis')

    field = wait_for(_id=date_field)
    field.send_keys(date)
    Arsenic().hide_title_bar()
    Arsenic().click_with_coordinates('state-group-supervisors', 5, 5)
    try:
        error_message = get_text_of(_id=error_message_id)
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
    wait_for(_id='supervisors-0-affiliation')
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
    write(_id='arxiv_id', data=arxiv_id)
    click(_id='importData')
    click(_id='acceptData')
    wait_for(_id='arxiv_id')
    _skip_import_data()

    output_data = {
        'doi': get_value_of(_id='doi'),
        'year': get_value_of(_id='year'),
        'issue': get_value_of(_id='issue'),
        'title': get_value_of(_id='title'),
        'volume': get_value_of(_id='volume'),
        'abstract': get_value_of(_id='abstract'),
        'author': get_value_of(_id='authors-0-name'),
        'journal': get_value_of(_id='journal_title'),
        'page-range': get_value_of(_id='page_range_article_id'),
    }

    def _assert_has_no_errors():
        return expected_data == output_data

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def submit_doi_id(doi_id, expected_data):
    write(_id='doi', data=doi_id)
    click(_id='importData')
    click(_id='acceptData')
    wait_for(_id='doi')
    _skip_import_data()

    output_data = {
        'year': get_value_of(_id='year'),
        'title': get_value_of(_id='title'),
        'issue': get_value_of(_id='issue'),
        'volume': get_value_of(_id='volume'),
        'journal': get_value_of(_id='journal_title'),
        'author': get_value_of(_id='authors-0-name'),
        'author-1': get_value_of(_id='authors-1-name'),
        'author-2': get_value_of(_id='authors-2-name'),
        'page-range': get_value_of(_id='page_range_article_id'),
    }

    def _assert_has_no_errors():
        assert expected_data == output_data

    return ArsenicResponse(assert_has_no_errors_func=_assert_has_no_errors)


def _skip_import_data():
    Arsenic().hide_title_bar()
    click(_id='skipImportData')
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
    select(_id='type_of_doc', value=document_type)


def _populate_subjects(subjects):

    click(xpath=SUBJECTS_BUTTON)
    for subject in subjects:
        click(xpath='//input[@value="' + subject + '"]')

    click(xpath=SUBJECTS_BUTTON)


def _populate_authors(authors):
    for index, author in enumerate(authors):
        write(_id='authors-%s-name' % index, data=author['name'])
        if 'affiliation' in author:
            write(
                _id='authors-%s-affiliation' % index,
                data=(
                    author['affiliation'],
                    author['name'],
                ),
            )

        click(link_text='Add another author')


def _populate_report_numbers(report_numbers):
    for index, report_number in enumerate(report_numbers):
        write(_id='report_numbers-%s-report_number' % index, data=report_number)
        click(link_text='Add another report number')
