# -*- coding: utf-8 -*-
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

import mock
import pytest

from invenio_records.api import Record

from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text


# TODO: test _get_format_output_row


def test_get_author_from_authors_a_list_with_one_element():
    authors_a_list_with_one_element = Record({
        'authors': [
            {'full_name': 'Glashow, S.L.'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        authors_a_list_with_one_element, 'cv_latex_html', ',')

    expected = ['S.L. Glashow']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_a_list_with_two_elements():
    authors_a_list_with_two_elements = Record({
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        authors_a_list_with_two_elements, 'cv_latex_html', ',')

    expected = ['F. Englert', 'R. Brout']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_an_empty_list_of_full_names():
    one_author_with_an_empty_list_of_full_names = Record({
        'authors': [
            {'full_name': []}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_an_empty_list_of_full_names, 'cv_latex_html', ',')

    expected = []
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_one_full_name():
    one_author_with_a_list_of_one_full_name = Record({
        'authors': [
            {'full_name': ['Glashow, S.L.']}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_a_list_of_one_full_name, 'cv_latex_html', ',')

    expected = ['S.L. Glashow']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_two_full_names():
    one_author_with_a_list_of_two_full_names = Record({
        'authors': [
            {
                'full_name': [
                    'Englert, F.',
                    'Brout, R.'
                ]
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        one_author_with_a_list_of_two_full_names, 'cv_latex_html', ',')

    expected = ['F.Brout Englert, R.']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_an_empty_list():
    corporate_author_an_empty_list = Record({'corporate_author': []})
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_an_empty_list, 'cv_latex_html_text', ',')

    expected = []
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_a_list_with_one_element():
    corporate_author_a_list_of_one_element = Record({
        'corporate_author': [
            'CMS Collaboration'
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_a_list_of_one_element, 'cv_latex_html_text', ',')

    expected = ['CMS Collaboration']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_author_from_corporate_author_a_list_with_two_elements():
    corporate_author_a_list_of_two_elements = Record({
        'corporate_author': [
            'CMS Collaboration',
            'The ATLAS Collaboration'
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        corporate_author_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = ['CMS Collaboration', 'The ATLAS Collaboration']
    result = cv_latex_html_text._get_author()

    assert expected == result


def test_get_title_returns_empty_string_when_no_titles():
    no_titles = Record({})
    cv_latex_html_text = Cv_latex_html_text(
        no_titles, 'cv_latex_html_text', ',')

    expected = ''
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_returns_empty_string_when_titles_is_an_empty_list():
    titles_an_empty_list = Record({
        'titles': []
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_an_empty_list, 'cv_latex_html_text', ',')

    expected = ''
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_one_element_without_subtitles():
    titles_a_list_of_one_element_without_subtitles = Record({
        'titles': [
            {'title': 'foo'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_one_element_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_titles_when_titles_is_a_list_of_two_elements_without_subtitles():
    titles_a_list_of_two_elements_without_subtitles = Record({
        'titles': [
            {'title': 'foo'},
            {'title': 'bar'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_two_elements_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_one_element_with_subtitle():
    titles_a_list_of_one_element_with_subtitle = Record({
        'titles': [
            {
                'title': 'foo',
                'subtitle': 'bar'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_one_element_with_subtitle, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_a_list_of_two_elements_with_subtitles():
    titles_a_list_of_two_elements_with_subtitles = Record({
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
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_a_list_of_two_elements_with_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_not_a_list_without_subtitles():
    titles_not_a_list_without_subtitles = Record({
        'titles': {
            'title': 'foo'
        }
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_not_a_list_without_subtitles, 'cv_latex_html_text', ',')

    expected = 'foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_when_titles_is_not_a_list_with_subtitle():
    titles_not_a_list_with_subtitle = Record({
        'titles': {
            'title': 'foo',
            'subtitle': 'bar'
        }
    })
    cv_latex_html_text = Cv_latex_html_text(
        titles_not_a_list_with_subtitle, 'cv_latex_html_text', ',')

    expected = 'foo : bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_capitalizes_when_title_is_uppercase():
    title_is_uppercase = Record({
        'titles': [
            {'title': 'FOO'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        title_is_uppercase, 'cv_latex_html_text', ',')

    expected = 'Foo'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_title_capitalizes_when_title_contains_uppercase_the():
    title_contains_uppercase_the = Record({
        'titles': [
            {'title': 'foo THE bar'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        title_contains_uppercase_the, 'cv_latex_html_text', ',')

    expected = 'Foo The Bar'
    result = cv_latex_html_text._get_title()

    assert expected == result


def test_get_publi_info_no_publication_info():
    no_publication_info = Record({})
    cv_latex_html_text = Cv_latex_html_text(
        no_publication_info, 'cv_latex_html_text', ',')

    assert cv_latex_html_text._get_publi_info() is None


def test_get_publi_info_from_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({'publication_info': []})
    cv_latex_html_text = Cv_latex_html_text(
        publication_info_an_empty_list, 'cv_latex_html_text', ',')

    expected = []
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_not_a_list():
    journal_title_not_a_list = Record({
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_title_not_a_list, 'cv_latex_html_text', ',')

    expected = ['Submitted to:Nucl.Phys.']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


@pytest.mark.xfail(reason='IndexError when accessing last element')
def test_get_publi_info_from_publication_info_with_journal_title_an_empty_list():
    journal_title_an_empty_list = Record({
        'publication_info': [
            {'journal_title': []}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_title_an_empty_list, 'cv_latex_html_text', ',')

    expected = []
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_one_element():
    journal_title_a_list_of_one_element = Record({
        'publication_info': [
            {'journal_title': ['foo']}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_title_a_list_of_one_element, 'cv_latex_html_text', ',')

    expected = ['Submitted to:foo']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_two_elements():
    journal_title_a_list_of_two_elements = Record({
        'publication_info': [
            {'journal_title': ['foo', 'bar']}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_title_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = ['Submitted to:bar']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume():
    journal_volume = Record({
        'publication_info': [
            {
                'journal_title': 'eConf',
                'journal_volume': 'C050318'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_volume, 'cv_latex_html_text', ',')

    expected = ['eConf C050318']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume_with_letter():
    journal_volume_with_letter = Record({
        'publication_info': [
            {
                'journal_title': 'Eur.Phys.J.',
                'journal_volume': 'C73'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_volume_with_letter, 'cv_latex_html_text', ',')

    expected = ['Eur.Phys.J. C73']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_not_a_list():
    year_not_a_list = Record({
        'publication_info': [
            {
                'journal_title': 'Phys.Lett.',
                'year': '1999'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        year_not_a_list, 'cv_latex_html_text', ',')

    expected = ['Submitted to:Phys.Lett. (1999)']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


@pytest.mark.xfail(reason='IndexError when accessing last element')
def test_get_publi_info_from_publication_info_with_year_an_empty_list():
    year_an_empty_list = Record({
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.',
                'year': []
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        year_an_empty_list, 'cv_latex_html_text', ',')

    expected = ['Submitted to:Phys.Rev.']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_one_element():
    year_a_list_of_one_element = Record({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'year': ['1999']
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        year_a_list_of_one_element, 'cv_latex_html_text', ',')

    expected = ['Submitted to:JHEP (1999)']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_two_elements():
    year_a_list_of_two_elements = Record({
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.Lett.',
                'year': ['1999', '2000']
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        year_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = ['Submitted to:Phys.Rev.Lett. (2000)']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_issue():
    journal_issue = Record({
        'publication_info': [
            {
                'journal_title': 'Class.Quant.Grav.',
                'journal_issue': '10'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        journal_issue, 'cv_latex_html_text', ',')

    expected = ['Class.Quant.Grav. 10,']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_artid_not_a_list():
    page_artid_not_a_list = Record({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'page_artid': '190'
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        page_artid_not_a_list, 'cv_latex_html_text', ',')

    expected = ['JHEP 190']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_artid_an_empty_list():
    page_artid_an_empty_list = Record({
        'publication_info': [
            {
                'journal_title': 'Phys.Lett.',
                'page_artid': []
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        page_artid_an_empty_list, 'cv_latex_html_text', ',')

    expected = ['Phys.Lett.']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_artid_a_list_of_one_element():
    page_artid_a_list_of_one_element = Record({
        'publication_info': [
            {
                'journal_title': 'Eur.Phys.J.',
                'page_artid': ['2466']
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        page_artid_a_list_of_one_element, 'cv_latex_html_text', ',')

    expected = ['Eur.Phys.J. 2466']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_artid_a_list_of_two_elements():
    page_artid_a_list_of_two_elements = Record({
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.Lett.',
                'page_artid': [
                    '321-323',
                    '1-188'
                ]
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        page_artid_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = ['Phys.Rev.Lett. 1-188']
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_pubinfo_freetext():
    pubinfo_freetext = Record({
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Lett. 12 (1964) 132-133'}
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        pubinfo_freetext, 'cv_latex_html_text', ',')

    expected = 'Phys. Lett. 12 (1964) 132-133'
    result = cv_latex_html_text._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_a_list_of_two_elements():
    publication_info_a_list_of_two_elements = Record({
        'publication_info': [
            {
                'journal_title': 'Int.J.Theor.Phys.',
                'journal_volume': '38',
                'page_artid': '1113-1133',
                'year': 1999
            },
            {
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '2',
                'page_artid': '231-252',
                'year': 1998
            }
        ]
    })
    cv_latex_html_text = Cv_latex_html_text(
        publication_info_a_list_of_two_elements, 'cv_latex_html_text', ',')

    expected = [
        'Int.J.Theor.Phys. 38 (1999) 1113-1133',
        'Adv.Theor.Math.Phys. 2 (1998) 231-252'
    ]
    result = cv_latex_html_text._get_publi_info()

    assert expected == result
