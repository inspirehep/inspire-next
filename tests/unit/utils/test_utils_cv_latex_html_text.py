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

from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text


def test_get_author_from_authors_a_list_with_one_element():
    authors_a_list_with_one_element = {
        'authors': [
            {'full_name': 'Glashow, S.L.'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        authors_a_list_with_one_element, 'cv_latex_html', ',')

    expected = ['S.L. Glashow']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_a_list_with_two_elements():
    authors_a_list_with_two_elements = {
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        authors_a_list_with_two_elements, 'cv_latex_html', ',')

    expected = ['F. Englert', 'R. Brout']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_an_empty_list_of_full_names():
    one_author_with_an_empty_list_of_full_names = {
        'authors': [
            {'full_name': []}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_an_empty_list_of_full_names, 'cv_latex_html', ',')

    expected = []
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_one_full_name():
    one_author_with_a_list_of_one_full_name = {
        'authors': [
            {'full_name': ['Glashow, S.L.']}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_a_list_of_one_full_name, 'cv_latex_html', ',')

    expected = ['S.L. Glashow']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_two_full_names():
    one_author_with_a_list_of_two_full_names = {
        'authors': [
            {
                'full_name': [
                    'Englert, F.',
                    'Brout, R.'
                ]
            }
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_a_list_of_two_full_names, 'cv_latex_html', ',')

    expected = ['F.Brout Englert, R.']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_an_empty_list():
    corporate_author_an_empty_list = {'corporate_author': []}
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_an_empty_list, 'cv_latex_html_text', ',')

    expected = []
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_a_list_with_one_element():
    corporate_author_a_list_of_one_element = {
        'corporate_author': [
            'CMS Collaboration'
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_a_list_of_one_element, 'cv_latex_html_text', ',')

    expected = ['CMS Collaboration']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_a_list_with_two_elements():
    corporate_author_a_list_of_two_elements = {
        'corporate_author': [
            'CMS Collaboration',
            'The ATLAS Collaboration'
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = ['CMS Collaboration', 'The ATLAS Collaboration']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_title_returns_empty_string_when_no_titles():
    no_titles = {}
    cv_latex_html_text = Cv_latex_html_text(
        no_titles, 'cv_latex_html_text', ',')

    expected = ''
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_returns_empty_string_when_titles_is_an_empty_list():
    titles_an_empty_list = {
        'titles': []
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_an_empty_list, 'cv_latex_html_text', ',')

    expected = ''
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_one_element_without_subtitles():
    titles_a_list_of_one_element_without_subtitles = {
        'titles': [
            {'title': 'foo'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_one_element_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_titles_when_titles_is_a_list_of_two_elements_without_subtitles():
    titles_a_list_of_two_elements_without_subtitles = {
        'titles': [
            {'title': 'foo'},
            {'title': 'bar'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_two_elements_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_one_element_with_subtitle():
    titles_a_list_of_one_element_with_subtitle = {
        'titles': [
            {
                'title': 'foo',
                'subtitle': 'bar'
            }
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_one_element_with_subtitle, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_two_elements_with_subtitles():
    titles_a_list_of_two_elements_with_subtitles = {
        'titles': [
            {
                'title': 'foo',
                'subtitle': 'bar'
            },
            {
                'title': 'baz',
                'subtitle': 'quux'
            }
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_two_elements_with_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_not_a_list_without_subtitles():
    titles_not_a_list_without_subtitles = {
        'titles': {
            'title': 'foo'
        }
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_not_a_list_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_not_a_list_with_subtitle():
    titles_not_a_list_with_subtitle = {
        'titles': {
            'title': 'foo',
            'subtitle': 'bar'
        }
    }
    cv_latex_html_text = Cv_latex_html_text(
        titles_not_a_list_with_subtitle, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_capitalizes_when_title_is_uppercase():
    title_is_uppercase = {
        'titles': [
            {'title': 'FOO'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        title_is_uppercase, 'cv_latex_html_text', ',')

    expected = 'Foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_capitalizes_when_title_contains_uppercase_the():
    title_contains_uppercase_the = {
        'titles': [
            {'title': 'foo THE bar'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        title_contains_uppercase_the, 'cv_latex_html_text', ',')

    expected = 'Foo The Bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_publi_info_no_publication_info():
    no_publication_info = {}
    cv_latex_html_text = Cv_latex_html_text(
        no_publication_info, 'cv_latex_html_text', ',')

    assert cv_latex_html_text._get_publi_info() is None


def test_get_publi_info_from_publication_info_an_empty_list():
    publication_info_an_empty_list = {'publication_info': []}
    cv_latex_html_text = Cv_latex_html_text(
        publication_info_an_empty_list, 'cv_latex_html_text', ',')

    expected = []
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume():
    journal_volume = {
        'publication_info': [
            {
                'journal_title': 'eConf',
                'journal_volume': 'C050318'
            }
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        journal_volume, 'cv_latex_html_text', ',')

    expected = ['eConf C050318']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_pubinfo_freetext():
    pubinfo_freetext = {
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Lett. 12 (1964) 132-133'}
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        pubinfo_freetext, 'cv_latex_html_text', ',')

    expected = 'Phys. Lett. 12 (1964) 132-133'
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_a_list_of_two_elements():
    publication_info_a_list_of_two_elements = {
        'publication_info': [
            {
                'journal_title': 'Int.J.Theor.Phys.',
                'journal_volume': '38',
                'page_start': '1113',
                'page_end': '1133',
                'year': 1999
            },
            {
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '2',
                'page_start': '231',
                'page_end': '252',
                'year': 1998
            }
        ]
    }
    cv_latex_html_text = Cv_latex_html_text(
        publication_info_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = [
        'Int.J.Theor.Phys. 38 (1999) 1113-1133',
        'Adv.Theor.Math.Phys. 2 (1998) 231-252'
    ]
    result = cv_latex_html_text._get_publi_info()

    assert expected == result
