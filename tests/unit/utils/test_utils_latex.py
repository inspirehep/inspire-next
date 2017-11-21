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

"""Unit tests for the LaTeX exporter."""

from __future__ import absolute_import, division, print_function

import mock
import pytest

from inspirehep.utils.latex import Latex


def test_format_output_row_unknown_field():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = ''
    result = latex._format_output_row('unknown_field', 'foo')

    assert expected == result


def test_format_output_row_one_author():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'  S.~L.~Glashow,\n'
    result = latex._format_output_row('author', ['S.~L.~Glashow'])

    assert expected == result


def test_format_output_row_between_one_and_eight_authors():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'  F.~Englert and R.~Brout,\n'
    result = latex._format_output_row('author', ['F.~Englert', 'R.~Brout'])

    assert expected == result


def test_format_output_row_more_than_eight_authors_collaboration():
    with_collaboration = {
        'collaboration': [
            {'value': 'Supernova Search Team'}
        ]
    }
    latex = Latex(with_collaboration, 'latex_eu')

    expected = u'  A.~G.~Riess {{\\it et al.}} [Supernova Search Team Collaboration],\n'
    result = latex._format_output_row('author', [
        'A.~G.~Riess', 'A.~V.~Filippenko', 'P.~Challis', 'A.~Clocchiattia',
        'A.~Diercks', 'P.~M.~Garnavich', 'R.~L.~Gilliland', 'C.~J.~Hogan',
        'S.~Jha', 'R.~P.~Kirshner', 'B.~Leibundgut', 'M.~M.~Phillips',
        'D.~Reiss', 'B.~P.~Schmidt', 'R.~A.~Schommer', 'R.~C.~Smith',
        'J.~Spyromilio', 'C.~Stubbs', 'N.~B.~Suntzeff', 'J.~Tonry'
    ])

    assert expected == result


def test_format_output_row_more_than_eight_authors_collaboration_in_collaboration():
    collaboration_in_collaboration = {
        'collaboration': [
            {'value': 'The ATLAS Collaboration'}
        ]
    }
    latex = Latex(collaboration_in_collaboration, 'latex_eu')

    expected = u'  G.~Aad {{\it et al.}} [The ATLAS Collaboration],\n'
    result = latex._format_output_row('author', [
        'G.~Aad', 'B.~Abbott', 'J.~Abdallah', 'O.~Abdinov', 'B.~Abeloos',
        'R.~Aben', 'M.~Abolins', 'O.~AbouZeid', 'H.~Abramowicz'
    ])

    assert expected == result


def test_format_output_row_more_than_eight_authors_no_collaboration():
    without_collaboration = {}
    latex = Latex(without_collaboration, 'latex_eu')

    expected = u'  L.~Cadamuro {\it et al.},\n'
    result = latex._format_output_row('author', [
        'L.~Cadamuro', 'M.~Calvi', 'L.~Cassina', 'A.~Giachero', 'C.~Gotti',
        'B.~Khanji', 'M.~Maino', 'C.~Matteuzzi', 'G.~Pessina'
    ])

    assert expected == result


@pytest.mark.xfail
def test_format_output_row_more_than_eight_authors_collaboration_an_empty_list():
    collaboration_an_empty_list = {'collaboration': []}
    latex = Latex(collaboration_an_empty_list, 'latex_eu')

    expected = '  0 {\\it et al.}'
    result = latex._format_output_row('author', [str(i) for i in range(9)])

    assert expected == result


@pytest.mark.xfail
def test_format_output_row_title():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u"  %``Partial Symmetries of Weak Interactions,''\n"
    result = latex._format_output_row('title', 'Partial Symmetries of Weak Interactions')

    assert expected == result


def test_format_output_row_publi_info_not_a_list():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'  Phys. Lett. 12 (1964) 132-133.\n'
    result = latex._format_output_row('publi_info', 'Phys. Lett. 12 (1964) 132-133')

    assert expected == result


@pytest.mark.xfail
def test_format_output_row_publi_info_an_empty_list():
    record = {}
    latex = Latex(record, 'latex_eu')

    latex._format_output_row('publi_info', [])


def test_format_output_row_publi_info_a_list_with_one_element():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'  Phys.\\ Rev.\\ D {\\bf 73} (2006) 014022\n'
    result = latex._format_output_row('publi_info', [
        'Phys.\\ Rev.\\ D {\\bf 73} (2006) 014022'
    ])

    assert expected == result


def test_format_output_row_publi_info_a_list_with_two_elelemts():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'''  Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113
    [Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]
'''

    result = latex._format_output_row('publi_info', [
        'Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113',
        '[Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]'
    ])

    assert expected == result


def test_format_output_row_arxiv_with_publi_info():
    with_publi_info = {
        'publication_info': [
            {'journal_title': ''}
        ]
    }
    latex = Latex(with_publi_info, 'latex_eu')

    expected = u'  [arXiv:1512.01381 [hep-th]].\n'
    result = latex._format_output_row('arxiv', 'arXiv:1512.01381 [hep-th]')

    assert expected == result


def test_format_output_row_arxiv_without_publi_info():
    without_publi_info = {}
    latex = Latex(without_publi_info, 'latex_eu')

    expected = u'  arXiv:1512.01296 [hep-th].\n'
    result = latex._format_output_row('arxiv', 'arXiv:1512.01296 [hep-th]')

    assert expected == result


def test_format_output_row_report_number():
    record = {}
    latex = Latex(record, 'latex_eu')

    expected = u'  CMS-PAS-TOP-13-007.\n'
    result = latex._format_output_row('report_number', 'CMS-PAS-TOP-13-007')

    assert expected == result


def test_get_author_from_authors_an_empty_list():
    authors_an_empty_list = {'authors': []}
    latex = Latex(authors_an_empty_list, 'latex_eu')

    expected = []
    result = latex._get_author()

    assert expected == result


def test_get_author_from_authors_a_list_with_one_element():
    authors_a_list_with_one_element = {
        'authors': [
            {'full_name': 'Glashow, S.L.'}
        ]
    }
    latex = Latex(authors_a_list_with_one_element, 'latex_eu')

    expected = ['S.~L.~Glashow']
    result = latex._get_author()

    assert expected == result


def test_get_author_from_authors_a_list_with_two_elements():
    authors_a_list_with_two_elements = {
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    }
    latex = Latex(authors_a_list_with_two_elements, 'latex_eu')

    expected = ['F.~Englert', 'R.~Brout']
    result = latex._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_an_empty_list_of_full_names():
    one_author_with_an_empty_list_of_full_names = {
        'authors': [
            {'full_name': []}
        ]
    }
    latex = Latex(one_author_with_an_empty_list_of_full_names, 'latex_eu')

    expected = []
    result = latex._get_author()

    assert expected == result


def test_get_author_from_authors_one_author_with_a_list_of_one_full_name():
    one_author_with_a_list_of_one_full_name = {
        'authors': [
            {'full_name': ['Glashow, S.L.']}
        ]
    }
    latex = Latex(one_author_with_a_list_of_one_full_name, 'latex_eu')

    expected = ['S.~L.~Glashow']
    result = latex._get_author()

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
    latex = Latex(one_author_with_a_list_of_two_full_names, 'latex_eu')

    expected = ['F.~B.~Englert, R.']
    result = latex._get_author()

    assert expected == result


def test_get_author_from_corporate_author_an_empty_list():
    corporate_author_an_empty_list = {'corporate_author': []}
    latex = Latex(corporate_author_an_empty_list, 'latex_eu')

    expected = []
    result = latex._get_author()

    assert expected == result


@pytest.mark.xfail
def test_get_author_from_corporate_author_a_list_with_one_element():
    corporate_author_a_list_of_one_element = {
        'corporate_author': [
            'CMS Collaboration'
        ]
    }
    latex = Latex(corporate_author_a_list_of_one_element, 'latex_eu')

    expected = ['CMS Collaboration']
    result = latex._get_author()

    assert expected == result


@pytest.mark.xfail
def test_get_author_from_corporate_author_a_list_with_two_elements():
    corporate_author_a_list_of_two_elements = {
        'corporate_author': [
            'CMS Collaboration',
            'The ATLAS Collaboration'
        ]
    }
    latex = Latex(corporate_author_a_list_of_two_elements, 'latex_eu')

    expected = ['CMS Collaboration', 'The ATLAS Collaboration']
    result = latex._get_author()

    assert expected == result


def test_get_title_no_titles():
    no_titles = {}
    latex = Latex(no_titles, 'latex_eu')

    expected = ''
    result = latex._get_title()

    assert expected == result


def test_get_title_from_titles_an_empty_list():
    titles_an_empty_list = {'titles': []}
    latex = Latex(titles_an_empty_list, 'latex_eu')

    expected = ''
    result = latex._get_title()

    assert expected == result


def test_get_title_from_titles_a_list_with_one_element():
    titles_a_list_with_one_element = {
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'}
        ]
    }
    latex = Latex(titles_a_list_with_one_element, 'latex_eu')

    expected = 'Partial Symmetries of Weak Interactions'
    result = latex._get_title()

    assert expected == result


def test_get_title_from_titles_a_list_with_two_elements():
    titles_a_list_with_two_elements = {
        'titles': [
            {'title': 'Broken Symmetries and the Masses of Gauge Bosons'},
            {'title': 'BROKEN SYMMETRIES AND THE MASSES OF GAUGE BOSONS.'}
        ]
    }
    latex = Latex(titles_a_list_with_two_elements, 'latex_eu')

    expected = 'Broken Symmetries and the Masses of Gauge Bosons'
    result = latex._get_title()

    assert expected == result


def test_get_title_from_titles_not_a_list():
    titles_not_a_list = {
        'titles': {
            'title': 'Partial Symmetries of Weak Interactions'
        }
    }
    latex = Latex(titles_not_a_list, 'latex_eu')

    expected = 'Partial Symmetries of Weak Interactions'
    result = latex._get_title()

    assert expected == result


def test_get_publi_info_no_publication_info():
    no_publication_info = {}
    latex = Latex(no_publication_info, 'latex_eu')

    assert latex._get_publi_info() is None


def test_get_publi_info_from_publication_info_an_empty_list():
    publication_info_an_empty_list = {'publication_info': []}
    latex = Latex(publication_info_an_empty_list, 'latex_eu')

    expected = []
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_not_a_list():
    journal_title_not_a_list = {
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'}
        ]
    }
    latex = Latex(journal_title_not_a_list, 'latex_eu')

    expected = ['Nucl.\\ Phys.\\ ']
    result = latex._get_publi_info()

    assert expected == result


@pytest.mark.xfail
def test_get_publi_info_from_publication_info_with_journal_title_an_empty_list():
    journal_title_an_empty_list = {
        'publication_info': [
            {'journal_title': []}
        ]
    }
    latex = Latex(journal_title_an_empty_list, 'latex_eu')

    expected = []
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_one_element():
    journal_title_a_list_of_one_element = {
        'publication_info': [
            {'journal_title': ['foo']}
        ]
    }
    latex = Latex(journal_title_a_list_of_one_element, 'latex_eu')

    expected = ['foo']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_two_elements():
    journal_title_a_list_of_two_elements = {
        'publication_info': [
            {'journal_title': ['foo', 'bar']}
        ]
    }
    latex = Latex(journal_title_a_list_of_two_elements, 'latex_eu')

    expected = ['bar']
    result = latex._get_publi_info()

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
    latex = Latex(journal_volume, 'latex_eu')

    expected = ['eConf C {\\bf 050318}']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_volume_with_letter():
    journal_volume_with_letter = {
        'publication_info': [
            {
                'journal_title': 'Eur.Phys.J.',
                'journal_volume': 'C73'
            }
        ]
    }
    latex = Latex(journal_volume_with_letter, 'latex_eu')

    expected = ['Eur.\\ Phys.\\ J.\\ C {\\bf 73}']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_not_a_list():
    year_not_a_list = {
        'publication_info': [
            {
                'journal_title': 'Phys.Lett.',
                'year': '1999'
            }
        ]
    }
    latex = Latex(year_not_a_list, 'latex_eu')

    expected = ['Phys.\\ Lett.\\  (1999)']
    result = latex._get_publi_info()

    assert expected == result


@pytest.mark.xfail
def test_get_publi_info_from_publication_info_with_year_an_empty_list():
    year_an_empty_list = {
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.',
                'year': []
            }
        ]
    }
    latex = Latex(year_an_empty_list, 'latex_eu')

    expected = ['Phys.\\ Rev.\\ ']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_one_element():
    year_a_list_of_one_element = {
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'year': ['1999']
            }
        ]
    }
    latex = Latex(year_a_list_of_one_element, 'latex_eu')

    expected = ['JHEP (1999)']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_year_a_list_of_two_elements():
    year_a_list_of_two_elements = {
        'publication_info': [
            {
                'journal_title': 'Phys.Rev.Lett.',
                'year': ['1999', '2000']
            }
        ]
    }
    latex = Latex(year_a_list_of_two_elements, 'latex_eu')

    expected = ['Phys.\\ Rev.\\ Lett.\\  (2000)']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_issue_latex_eu():
    journal_issue = {
        'publication_info': [
            {
                'journal_title': 'Int.J.Mod.Phys.',
                'journal_issue': '29'
            }
        ]
    }
    latex_eu = Latex(journal_issue, 'latex_eu')

    expected = ['Int.\\ J.\\ Mod.\\ Phys.\\  29, ']
    result = latex_eu._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_journal_issue_latex_us():
    journal_issue = {
        'publication_info': [
            {
                'journal_title': 'Class.Quant.Grav.',
                'journal_issue': '10'
            }
        ]
    }
    latex_us = Latex(journal_issue, 'latex_us')

    expected = ['Class.\\ Quant.\\ Grav.\\ , no. 10']
    result = latex_us._get_publi_info()

    assert expected == result


def test_get_publi_info_from_publication_info_with_page_start():
    page_start = {
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'page_start': '190'
            }
        ]
    }
    latex = Latex(page_start, 'latex_eu')

    expected = ['JHEP 190']
    result = latex._get_publi_info()

    assert expected == result


def test_get_publi_info_from_pubinfo_freetext():
    pubinfo_freetext = {
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Lett. 12 (1964) 132-133'}
        ]
    }
    latex = Latex(pubinfo_freetext, 'latex_eu')

    expected = 'Phys. Lett. 12 (1964) 132-133'
    result = latex._get_publi_info()

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
    latex = Latex(publication_info_a_list_of_two_elements, 'latex_eu')

    expected = [
        'Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113',
        '[Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]'
    ]
    result = latex._get_publi_info()

    assert expected == result


@mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
@mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
def test_get_report_number_no_publi_info_yes_arxiv(g_a, g_p_i):
    g_a.return_value = False
    g_p_i.return_value = True

    record = {}
    latex = Latex(record, 'latex_eu')

    assert latex._get_report_number() is None


@mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
@mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
def test_get_report_number_yes_publi_info_no_arxiv(g_a, g_p_i):
    g_a.return_value = True
    g_p_i.return_value = False

    record = {}
    latex = Latex(record, 'latex_eu')

    assert latex._get_report_number() is None


@mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
@mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
def test_get_report_number_yes_publi_info_yes_arxiv(g_a, g_p_i):
    g_a.return_value = True
    g_p_i.return_value = True

    record = {}
    latex = Latex(record, 'latex_eu')

    assert latex._get_report_number() is None
