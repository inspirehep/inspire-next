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

from __future__ import absolute_import, division, print_function

import mock
import pytest

from inspirehep.modules.records.api import InspireRecord
from inspirehep.utils.cv_latex import Cv_latex


# TODO: test _format_output_row


def test_get_author_from_authors_a_list_with_one_element():
    authors_a_list_with_one_element = InspireRecord({
        'authors': [
            {'full_name': 'Glashow, S.L.'}
        ]
    })

    expected = ['S.~L.~Glashow']
    result = Cv_latex(authors_a_list_with_one_element)._get_author()

    assert expected == result


def test_get_author_from_authors_a_list_with_two_elements():
    authors_a_list_with_two_elements = InspireRecord({
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    })

    expected = ['F.~Englert', 'R.~Brout']
    result = Cv_latex(authors_a_list_with_two_elements)._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_an_empty_list_of_full_names():
    one_author_with_an_empty_list_of_full_names = InspireRecord({
        'authors': [
            {'full_name': []}
        ]
    })

    expected = []
    result = Cv_latex(one_author_with_an_empty_list_of_full_names)._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_one_full_name():
    one_author_with_a_list_of_one_full_name = InspireRecord({
        'authors': [
            {'full_name': ['Glashow, S.L.']}
        ]
    })

    expected = ['S.~L.~Glashow']
    result = Cv_latex(one_author_with_a_list_of_one_full_name)._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_two_full_names():
    one_author_with_a_list_of_two_full_names = InspireRecord({
        'authors': [
            {
                'full_name': [
                    'Englert, F.',
                    'Brout, R.'
                ]
            }
        ]
    })

    expected = ['F.~B.~Englert, R.']
    result = Cv_latex(one_author_with_a_list_of_two_full_names)._get_author()

    assert expected == result


def test_get_author_from_corporate_author_an_empty_list():
    corporate_author_an_empty_list = InspireRecord({'corporate_author': []})

    expected = []
    result = Cv_latex(corporate_author_an_empty_list)._get_author()

    assert expected == result


@pytest.mark.xfail(reason='corporate_author is parsed as a real name')
def test_get_author_from_corporate_author_a_list_with_one_element():
    corporate_author_a_list_of_one_element = InspireRecord({
        'corporate_author': [
            'CMS Collaboration'
        ]
    })

    expected = ['CMS Collaboration']
    result = Cv_latex(corporate_author_a_list_of_one_element)._get_author()

    assert expected == result


@pytest.mark.xfail(reason='corporate_author is parsed as a real name')
def test_get_author_from_corporate_author_a_list_with_two_elements():
    corporate_author_a_list_of_two_elements = InspireRecord({
        'corporate_author': [
            'CMS Collaboration',
            'The ATLAS Collaboration'
        ]
    })

    expected = ['CMS Collaboration', 'The ATLAS Collaboration']
    result = Cv_latex(corporate_author_a_list_of_two_elements)._get_author()

    assert expected == result


def test_get_title_returns_empty_string_when_no_titles():
    without_titles = InspireRecord({})

    expected = ''
    result = Cv_latex(without_titles)._get_title()

    assert expected == result


def test_get_title_returns_first_title_found_when_titles_is_a_list():
    a_list_of_titles = InspireRecord({
        'titles': [
            {'title': ('Effective relational dynamics of a '
                       'nonintegrable cosmological model')},
            {'title': ('Effective relational dynamics of the '
                       'closed FRW model universe minimally '
                       'coupled to a massive scalar field')},
            {'title': ('Effective relational dynamics of a '
                       'nonintegrable cosmological model')}
        ]
    })

    expected = ("{\\bf ``Effective relational dynamics of a "
                "nonintegrable cosmological model''}")
    result = Cv_latex(a_list_of_titles)._get_title()

    assert expected == result


def test_get_publi_info_no_publication_info():
    no_publication_info = InspireRecord({})

    assert Cv_latex(no_publication_info)._get_publi_info() is None


def test_get_publi_info_from_publication_info_an_empty_list():
    publication_info_an_empty_list = InspireRecord({'publication_info': []})

    expected = []
    result = Cv_latex(publication_info_an_empty_list)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_not_a_list():
    journal_title_not_a_list = InspireRecord({
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'}
        ]
    })

    expected = ['Nucl.\\ Phys.\\ ']
    result = Cv_latex(journal_title_not_a_list)._get_publi_info()

    assert expected == result


@pytest.mark.xfail(reason='IndexError when accessing last element')
def test_get_publi_info_from_publication_info_with_journal_title_an_empty_list():
    journal_title_an_empty_list = InspireRecord({
        'publication_info': [
            {'journal_title': []}
        ]
    })

    expected = []
    result = Cv_latex(journal_title_an_empty_list)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_one_element():
    journal_title_a_list_of_one_element = InspireRecord({
        'publication_info': [
            {'journal_title': ['foo']}
        ]
    })

    expected = ['foo']
    result = Cv_latex(journal_title_a_list_of_one_element)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_two_elements():
    journal_title_a_list_of_two_elements = InspireRecord({
        'publication_info': [
            {'journal_title': ['foo', 'bar']}
        ]
    })

    expected = ['bar']
    result = Cv_latex(journal_title_a_list_of_two_elements)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume():
    journal_volume = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'eConf',
                'journal_volume': 'C050318'
            }
        ]
    })

    expected = ['eConf C {\\bf 050318}']
    result = Cv_latex(journal_volume)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume_with_letter():
    journal_volume_with_letter = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'Eur.Phys.J.',
                'journal_volume': 'C73'
            }
        ]
    })

    expected = ['Eur.\\ Phys.\\ J.\\ C {\\bf 73}']
    result = Cv_latex(journal_volume_with_letter)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_not_a_list():
    year_not_a_list = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'Phys.Lett.',
                'year': '1999'
            }
        ]
    })

    expected = ['Phys.\\ Lett.\\  (1999)']
    result = Cv_latex(year_not_a_list)._get_publi_info()

    assert expected == result


@pytest.mark.xfail(reason='IndexError when accessing last element')
def test_get_publi_info_from_publication_info_with_year_an_empty_list():
    year_an_empty_list = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.',
                'year': []
            }
        ]
    })

    expected = ['Phys.\\ Rev.\\ ']
    result = Cv_latex(year_an_empty_list)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_one_element():
    year_a_list_of_one_element = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'year': ['1999']
            }
        ]
    })

    expected = ['JHEP (1999)']
    result = Cv_latex(year_a_list_of_one_element)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_two_elements():
    year_a_list_of_two_elements = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.Lett.',
                'year': ['1999', '2000']
            }
        ]
    })

    expected = ['Phys.\\ Rev.\\ Lett.\\  (2000)']
    result = Cv_latex(year_a_list_of_two_elements)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_issue():
    journal_issue = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'Class.Quant.Grav.',
                'journal_issue': '10'
            }
        ]
    })

    expected = ['Class.\\ Quant.\\ Grav.\\ , no. 10']
    result = Cv_latex(journal_issue)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_start():
    page_start = InspireRecord({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'page_start': '190'
            }
        ]
    })

    expected = ['JHEP, 190']
    result = Cv_latex(page_start)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_pubinfo_freetext():
    pubinfo_freetext = InspireRecord({
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Lett. 12 (1964) 132-133'}
        ]
    })

    expected = 'Phys. Lett. 12 (1964) 132-133'
    result = Cv_latex(pubinfo_freetext)._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_a_list_of_two_elements():
    publication_info_a_list_of_two_elements = InspireRecord({
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
    })

    expected = [
        'Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38}, 1113 (1999)',
        '[Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2}, 231 (1998)]'
    ]
    result = Cv_latex(publication_info_a_list_of_two_elements)._get_publi_info()

    assert expected == result


@mock.patch(
    'inspirehep.utils.cv_latex.config',
    mock.Mock(SERVER_NAME='http://localhost:5000'))
def test_get_url():
    record = InspireRecord({'control_number': 1})

    expected = 'http://localhost:5000/record/1'
    result = Cv_latex(record)._get_url()

    assert expected == result


def test_get_date_without_any_date_returns_none():
    without_any_date = InspireRecord({})

    assert Cv_latex(without_any_date)._get_date() is None


def test_get_date_from_preprint_date():
    preprint_date = InspireRecord({'preprint_date': '2015-11-25'})

    expected = 'Nov 25, 2015'
    result = Cv_latex(preprint_date)._get_date()

    assert expected == result


@pytest.mark.xfail(reason='zero is not added to the day')
def test_get_date_from_preprint_date_adds_zero_to_day():
    preprint_date = InspireRecord({'preprint_date': '2014-10-1'})

    expected = 'Oct 01, 2014'
    result = Cv_latex(preprint_date)._get_date()

    assert expected == result


# TODO: test_get_date_from_arxiv_field


# TODO: test_get_date_from_arxiv_field_returns_none_when_date_is_short


# TODO: test_get_date_from_arxiv_field_doesnt_add_double_zero_as_a_day


def test_get_date_from_publication_info():
    publication_info = InspireRecord({
        'publication_info': [
            {'year': '2011'}
        ]
    })

    expected = 2011
    result = Cv_latex(publication_info)._get_date()

    assert expected == result


def test_get_date_from_publication_info_returns_none_when_no_year():
    publication_info_without_a_year = InspireRecord({
        'publication_info': []
    })

    assert Cv_latex(publication_info_without_a_year)._get_date() is None


def test_get_date_from_publication_info_uses_first_year_found():
    publication_info = InspireRecord({
        'publication_info': [
            {},
            {'year': '2012'}
        ]
    })

    expected = 2012
    result = Cv_latex(publication_info)._get_date()

    assert expected == result


def test_get_date_from_legacy_creation_date():
    legacy_creation_date = InspireRecord({
        'legacy_creation_date': '2012'
    })

    expected = 2012
    result = Cv_latex(legacy_creation_date)._get_date()

    assert expected == result


def test_get_date_from_imprints_returns_none_when_no_date():
    imprints_without_a_date = InspireRecord({
        'imprints': []
    })

    assert Cv_latex(imprints_without_a_date)._get_date() is None


def test_get_date_from_imprints_uses_first_date_found():
    imprints = InspireRecord({
        'imprints': [
            {},
            {'date': '2011-03-29'}
        ]
    })

    expected = 'Mar 29, 2011'
    result = Cv_latex(imprints)._get_date()

    assert expected == result


def test_get_date_from_thesis_returns_none_when_no_date():
    thesis_without_a_date = InspireRecord({
        'thesis': {}
    })

    assert Cv_latex(thesis_without_a_date)._get_date() is None


def test_get_date_from_thesis_uses_first_date_found():
    thesis = InspireRecord({
        'thesis': {'date': '1966'}
    })

    expected = 1966
    result = Cv_latex(thesis)._get_date()

    assert expected == result


def test_format_date_when_datestruct_has_one_element():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = 1993
    result = cv_latex._format_date((1993,))

    assert expected == result


def test_format_date_when_datestruct_has_two_elements():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = 'Feb 1993'
    result = cv_latex._format_date((1993, 2))

    assert expected == result


def test_format_date_when_datestruct_has_three_elements():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = 'Feb 2, 1993'
    result = cv_latex._format_date((1993, 2, 2))

    assert expected == result


def test_format_date_returns_none_when_datestruct_has_four_elements():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    assert cv_latex._format_date((1993, 2, 2, 1)) is None


def test_parse_date_returns_none_when_datetext_is_none():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    assert cv_latex.parse_date(None) is None


def test_parse_date_returns_none_when_datetext_is_an_empty_string():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    assert cv_latex.parse_date('') is None


def test_parse_date_returns_none_when_datetext_is_not_of_type_str():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    assert cv_latex.parse_date(0) is None


@pytest.mark.xfail(reason='too strict check against str type')
def test_parse_date_supports_unicode_strings():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2, 2)
    result = cv_latex.parse_date(u'1993-02-02')

    assert expected == result


def test_parse_date_partial_spires_format_year_only():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993,)
    result = cv_latex.parse_date('1993')

    assert expected == result


def test_parse_date_partial_spires_format_year_and_month():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2)
    result = cv_latex.parse_date('199302')

    assert expected == result


def test_parse_date_full_spires_format():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2, 2)
    result = cv_latex.parse_date('19930202')

    assert expected == result


def test_parse_date_invalid_spires_format():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2)
    result = cv_latex.parse_date('199302ab')

    assert expected == result


def test_parse_date_full_invenio_format():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2, 2)
    result = cv_latex.parse_date('1993-02-02')

    assert expected == result


def test_parse_date_invalid_invenio_format():
    record = InspireRecord({})
    cv_latex = Cv_latex(record)

    expected = (1993, 2)
    result = cv_latex.parse_date('1993-02-ab')

    assert expected == result
