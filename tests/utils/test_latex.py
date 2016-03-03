# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for the LaTeX exporter."""

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase

import mock

import pytest


Latex = lazy_import('inspirehep.utils.latex.Latex')
Record = lazy_import('invenio_records.api.Record')


class LatexTests(InvenioTestCase):

    """Unit tests for the LaTeX exporter."""

    @mock.patch('inspirehep.utils.export.time.strftime')
    @mock.patch('inspirehep.utils.export.es.get')
    def test_format_record_latex_eu(self, get, strftime):
        strftime.return_value = '02 Feb 1993'
        get.return_value = {'_source': {'citation_count': 9}}

        from invenio_records.api import get_record

        # TODO(jacquerie): replace with fixture.
        record = get_record(4328)
        latex_eu = Latex(record, 'latex_eu')

        expected = u'''%\\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,
  Nucl.\\ Phys.\\  {\\bf 22} (1961) 579
  doi:10.1016/0029-5582(61)90469-2.
  %%CITATION = NUPHA,22,579;%%
  %9 citations counted in INSPIRE as of 02 Feb 1993
'''
        result = latex_eu.format()

        self.assertEqual(expected, result)

    @mock.patch('inspirehep.utils.export.time.strftime')
    @mock.patch('inspirehep.utils.export.es.get')
    def test_format_record_latex_us(self, get, strftime):
        strftime.return_value = '02 Feb 1993'
        get.return_value = {'_source': {'citation_count': 9}}

        from invenio_records.api import get_record

        # TODO(jacquerie): replace with fixture.
        record = get_record(4328)
        latex_us = Latex(record, 'latex_us')

        expected = u'''%\\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,
  Nucl.\\ Phys.\\  {\\bf 22}, 579 (1961)
  doi:10.1016/0029-5582(61)90469-2.
  %%CITATION = NUPHA,22,579;%%
  %9 citations counted in INSPIRE as of 02 Feb 1993
'''
        result = latex_us.format()

        self.assertEqual(expected, result)

    def test_format_output_row_unknown_field(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = ''
        result = latex._format_output_row('unknown_field', 'foo')

        self.assertEqual(expected, result)

    def test_format_output_row_one_author(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'  S.~L.~Glashow,\n'
        result = latex._format_output_row('author', ['S.~L.~Glashow'])

        self.assertEqual(expected, result)

    def test_format_output_row_between_one_and_eight_authors(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'  F.~Englert and R.~Brout,\n'
        result = latex._format_output_row('author', ['F.~Englert', 'R.~Brout'])

        self.assertEqual(expected, result)

    def test_format_output_row_more_than_eight_authors_collaboration(self):
        with_collaboration = Record({
            'collaboration': [
                {'value': 'Supernova Search Team'}
            ]
        })
        latex = Latex(with_collaboration, 'latex_eu')

        expected = u'  A.~G.~Riess {{\\it et al.}} [Supernova Search Team Collaboration],\n'
        result = latex._format_output_row('author', [
            'A.~G.~Riess', 'A.~V.~Filippenko', 'P.~Challis', 'A.~Clocchiattia',
            'A.~Diercks', 'P.~M.~Garnavich', 'R.~L.~Gilliland', 'C.~J.~Hogan',
            'S.~Jha', 'R.~P.~Kirshner', 'B.~Leibundgut', 'M.~M.~Phillips',
            'D.~Reiss', 'B.~P.~Schmidt', 'R.~A.~Schommer', 'R.~C.~Smith',
            'J.~Spyromilio', 'C.~Stubbs', 'N.~B.~Suntzeff', 'J.~Tonry'
        ])

        self.assertEqual(expected, result)

    def test_format_output_row_more_than_eight_authors_collaboration_in_collaboration(self):
        collaboration_in_collaboration = Record({
            'collaboration': [
                {'value': 'The ATLAS Collaboration'}
            ]
        })
        latex = Latex(collaboration_in_collaboration, 'latex_eu')

        expected = u'  G.~Aad {{\it et al.}} [The ATLAS Collaboration],\n'
        result = latex._format_output_row('author', [
            'G.~Aad', 'B.~Abbott', 'J.~Abdallah', 'O.~Abdinov', 'B.~Abeloos',
            'R.~Aben', 'M.~Abolins', 'O.~AbouZeid', 'H.~Abramowicz'
        ])

        self.assertEqual(expected, result)

    def test_format_output_row_more_than_eight_authors_no_collaboration(self):
        without_collaboration = Record({})
        latex = Latex(without_collaboration, 'latex_eu')

        expected = u'  L.~Cadamuro {\it et al.},\n'
        result = latex._format_output_row('author', [
            'L.~Cadamuro', 'M.~Calvi', 'L.~Cassina', 'A.~Giachero', 'C.~Gotti',
            'B.~Khanji', 'M.~Maino', 'C.~Matteuzzi', 'G.~Pessina'
        ])

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_format_output_row_more_than_eight_authors_collaboration_an_empty_list(self):
        collaboration_an_empty_list = Record({'collaboration': []})
        latex = Latex(collaboration_an_empty_list, 'latex_eu')

        expected = '  0 {\\it et al.}'
        result = latex._format_output_row('author', [str(i) for i in range(9)])

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_format_output_row_title(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u"  %``Partial Symmetries of Weak Interactions,''\n"
        result = latex._format_output_row('title', 'Partial Symmetries of Weak Interactions')

        self.assertEqual(expected, result)

    def test_format_output_row_publi_info_not_a_list(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'  Phys. Lett. 12 (1964) 132-133.\n'
        result = latex._format_output_row('publi_info', 'Phys. Lett. 12 (1964) 132-133')

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_format_output_row_publi_info_an_empty_list(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        latex._format_output_row('publi_info', [])

    def test_format_output_row_publi_info_a_list_with_one_element(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'  Phys.\\ Rev.\\ D {\\bf 73} (2006) 014022\n'
        result = latex._format_output_row('publi_info', [
            'Phys.\\ Rev.\\ D {\\bf 73} (2006) 014022'
        ])

        self.assertEqual(expected, result)

    def test_format_output_row_publi_info_a_list_with_two_elelemts(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'''  Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113
    [Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]
'''
        result = latex._format_output_row('publi_info', [
            'Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113',
            '[Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]'
        ])

        self.assertEqual(expected, result)

    def test_format_output_row_arxiv_with_publi_info(self):
        with_publi_info = Record({
            'publication_info': [
                {'journal_title': ''}
            ]
        })
        latex = Latex(with_publi_info, 'latex_eu')

        expected = u'  [arXiv:1512.01381 [hep-th]].\n'
        result = latex._format_output_row('arxiv', 'arXiv:1512.01381 [hep-th]')

        self.assertEqual(expected, result)

    def test_format_output_row_arxiv_without_publi_info(self):
        without_publi_info = Record({})
        latex = Latex(without_publi_info, 'latex_eu')

        expected = u'  arXiv:1512.01296 [hep-th].\n'
        result = latex._format_output_row('arxiv', 'arXiv:1512.01296 [hep-th]')

        self.assertEqual(expected, result)

    def test_format_output_row_report_number(self):
        record = Record({})
        latex = Latex(record, 'latex_eu')

        expected = u'  CMS-PAS-TOP-13-007.\n'
        result = latex._format_output_row('report_number', 'CMS-PAS-TOP-13-007')

        self.assertEqual(expected, result)

    def test_get_author_from_authors_an_empty_list(self):
        authors_an_empty_list = Record({'authors': []})
        latex = Latex(authors_an_empty_list, 'latex_eu')

        expected = []
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_authors_a_list_with_one_element(self):
        authors_a_list_with_one_element = Record({
            'authors': [
                {'full_name': 'Glashow, S.L.'}
            ]
        })
        latex = Latex(authors_a_list_with_one_element, 'latex_eu')

        expected = ['S.~L.~Glashow']
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_authors_a_list_with_two_elements(self):
        authors_a_list_with_two_elements = Record({
            'authors': [
                {'full_name': 'Englert, F.'},
                {'full_name': 'Brout, R.'}
            ]
        })
        latex = Latex(authors_a_list_with_two_elements, 'latex_eu')

        expected = ['F.~Englert', 'R.~Brout']
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_authors_one_author_with_an_empty_list_of_full_names(self):
        one_author_with_an_empty_list_of_full_names = Record({
            'authors': [
                {'full_name': []}
            ]
        })
        latex = Latex(one_author_with_an_empty_list_of_full_names, 'latex_eu')

        expected = []
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_authors_one_author_with_a_list_of_one_full_name(self):
        one_author_with_a_list_of_one_full_name = Record({
            'authors': [
                {'full_name': ['Glashow, S.L.']}
            ]
        })
        latex = Latex(one_author_with_a_list_of_one_full_name, 'latex_eu')

        expected = ['S.~L.~Glashow']
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_authors_one_author_with_a_list_of_two_full_names(self):
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
        latex = Latex(one_author_with_a_list_of_two_full_names, 'latex_eu')

        expected = ['F.~B.~Englert, R.']
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_author_from_corporate_author_an_empty_list(self):
        corporate_author_an_empty_list = Record({'corporate_author': []})
        latex = Latex(corporate_author_an_empty_list, 'latex_eu')

        expected = []
        result = latex._get_author()

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_get_author_from_corporate_author_a_list_with_one_element(self):
        corporate_author_a_list_of_one_element = Record({
            'corporate_author': [
                'CMS Collaboration'
            ]
        })
        latex = Latex(corporate_author_a_list_of_one_element, 'latex_eu')

        expected = ['CMS Collaboration']
        result = latex._get_author()

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_get_author_from_corporate_author_a_list_with_two_elements(self):
        corporate_author_a_list_of_two_elements = Record({
            'corporate_author': [
                'CMS Collaboration',
                'The ATLAS Collaboration'
            ]
        })
        latex = Latex(corporate_author_a_list_of_two_elements, 'latex_eu')

        expected = ['CMS Collaboration', 'The ATLAS Collaboration']
        result = latex._get_author()

        self.assertEqual(expected, result)

    def test_get_title_no_titles(self):
        no_titles = Record({})
        latex = Latex(no_titles, 'latex_eu')

        expected = ''
        result = latex._get_title()

        self.assertEqual(expected, result)

    def test_get_title_from_titles_an_empty_list(self):
        titles_an_empty_list = Record({'titles': []})
        latex = Latex(titles_an_empty_list, 'latex_eu')

        expected = ''
        result = latex._get_title()

        self.assertEqual(expected, result)

    def test_get_title_from_titles_a_list_with_one_element(self):
        titles_a_list_with_one_element = Record({
            'titles': [
                {'title': 'Partial Symmetries of Weak Interactions'}
            ]
        })
        latex = Latex(titles_a_list_with_one_element, 'latex_eu')

        expected = 'Partial Symmetries of Weak Interactions'
        result = latex._get_title()

        self.assertEqual(expected, result)

    def test_get_title_from_titles_a_list_with_two_elements(self):
        titles_a_list_with_two_elements = Record({
            'titles': [
                {'title': 'Broken Symmetries and the Masses of Gauge Bosons'},
                {'title': 'BROKEN SYMMETRIES AND THE MASSES OF GAUGE BOSONS.'}
            ]
        })
        latex = Latex(titles_a_list_with_two_elements, 'latex_eu')

        expected = 'Broken Symmetries and the Masses of Gauge Bosons'
        result = latex._get_title()

        self.assertEqual(expected, result)

    def test_get_title_from_titles_not_a_list(self):
        titles_not_a_list = Record({
            'titles': {
                'title': 'Partial Symmetries of Weak Interactions'
            }
        })
        latex = Latex(titles_not_a_list, 'latex_eu')

        expected = 'Partial Symmetries of Weak Interactions'
        result = latex._get_title()

        self.assertEqual(expected, result)

    def test_get_publi_info_no_publication_info(self):
        no_publication_info = Record({})
        latex = Latex(no_publication_info, 'latex_eu')

        self.assertIsNone(latex._get_publi_info())

    def test_get_publi_info_from_publication_info_an_empty_list(self):
        publication_info_an_empty_list = Record({'publication_info': []})
        latex = Latex(publication_info_an_empty_list, 'latex_eu')

        expected = []
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_title_not_a_list(self):
        journal_title_not_a_list = Record({
            'publication_info': [
                {'journal_title': 'Nucl.Phys.'}
            ]
        })
        latex = Latex(journal_title_not_a_list, 'latex_eu')

        expected = ['Nucl.\\ Phys.\\ ']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_get_publi_info_from_publication_info_with_journal_title_an_empty_list(self):
        journal_title_an_empty_list = Record({
            'publication_info': [
                {'journal_title': []}
            ]
        })
        latex = Latex(journal_title_an_empty_list, 'latex_eu')

        expected = []
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_one_element(self):
        journal_title_a_list_of_one_element = Record({
            'publication_info': [
                {'journal_title': ['foo']}
            ]
        })
        latex = Latex(journal_title_a_list_of_one_element, 'latex_eu')

        expected = ['foo']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_title_a_list_of_two_elements(self):
        journal_title_a_list_of_two_elements = Record({
            'publication_info': [
                {'journal_title': ['foo', 'bar']}
            ]
        })
        latex = Latex(journal_title_a_list_of_two_elements, 'latex_eu')

        expected = ['bar']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_volume(self):
        journal_volume = Record({
            'publication_info': [
                {
                    'journal_title': 'eConf',
                    'journal_volume': 'C050318'
                }
            ]
        })
        latex = Latex(journal_volume, 'latex_eu')

        expected = ['eConf C {\\bf 050318}']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_volume_with_letter(self):
        journal_volume_with_letter = Record({
            'publication_info': [
                {
                    'journal_title': 'Eur.Phys.J.',
                    'journal_volume': 'C73'
                }
            ]
        })
        latex = Latex(journal_volume_with_letter, 'latex_eu')

        expected = ['Eur.\\ Phys.\\ J.\\ C {\\bf 73}']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_year_not_a_list(self):
        year_not_a_list = Record({
            'publication_info': [
                {
                    'journal_title': 'Phys.Lett.',
                    'year': '1999'
                }
            ]
        })
        latex = Latex(year_not_a_list, 'latex_eu')

        expected = ['Phys.\\ Lett.\\  (1999)']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    @pytest.mark.xfail
    def test_get_publi_info_from_publication_info_with_year_an_empty_list(self):
        year_an_empty_list = Record({
            'publication_info': [
                {
                    'journal_title': 'Phys.Rev.',
                    'year': []
                }
            ]
        })
        latex = Latex(year_an_empty_list, 'latex_eu')

        expected = ['Phys.\\ Rev.\\ ']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_year_a_list_of_one_element(self):
        year_a_list_of_one_element = Record({
            'publication_info': [
                {
                    'journal_title': 'JHEP',
                    'year': ['1999']
                }
            ]
        })
        latex = Latex(year_a_list_of_one_element, 'latex_eu')

        expected = ['JHEP (1999)']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_year_a_list_of_two_elements(self):
        year_a_list_of_two_elements = Record({
            'publication_info': [
                {
                    'journal_title': 'Phys.Rev.Lett.',
                    'year': ['1999', '2000']
                }
            ]
        })
        latex = Latex(year_a_list_of_two_elements, 'latex_eu')

        expected = ['Phys.\\ Rev.\\ Lett.\\  (2000)']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_issue_latex_eu(self):
        journal_issue = Record({
            'publication_info': [
                {
                    'journal_title': 'Int.J.Mod.Phys.',
                    'journal_issue': '29'
                }
            ]
        })
        latex_eu = Latex(journal_issue, 'latex_eu')

        expected = ['Int.\\ J.\\ Mod.\\ Phys.\\  29, ']
        result = latex_eu._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_journal_issue_latex_us(self):
        journal_issue = Record({
            'publication_info': [
                {
                    'journal_title': 'Class.Quant.Grav.',
                    'journal_issue': '10'
                }
            ]
        })
        latex_us = Latex(journal_issue, 'latex_us')

        expected = ['Class.\\ Quant.\\ Grav.\\ , no. 10']
        result = latex_us._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_page_artid_not_a_list(self):
        page_artid_not_a_list = Record({
            'publication_info': [
                {
                    'journal_title': 'JHEP',
                    'page_artid': '190'
                }
            ]
        })
        latex = Latex(page_artid_not_a_list, 'latex_eu')

        expected = ['JHEP 190']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_page_artid_an_empty_list(self):
        page_artid_an_empty_list = Record({
            'publication_info': [
                {
                    'journal_title': 'Phys.Lett.',
                    'page_artid': []
                }
            ]
        })
        latex = Latex(page_artid_an_empty_list, 'latex_eu')

        expected = ['Phys.\\ Lett.\\ ']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_page_artid_a_list_of_one_element(self):
        page_artid_a_list_of_one_element = Record({
            'publication_info': [
                {
                    'journal_title': 'Eur.Phys.J.',
                    'page_artid': ['2466']
                }
            ]
        })
        latex = Latex(page_artid_a_list_of_one_element, 'latex_eu')

        expected = ['Eur.\\ Phys.\\ J.\\  2466']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_with_page_artid_a_list_of_two_elements(self):
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
        latex = Latex(page_artid_a_list_of_two_elements, 'latex_eu')

        expected = ['Phys.\\ Rev.\\ Lett.\\  1']
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_pubinfo_freetext(self):
        pubinfo_freetext = Record({
            'publication_info': [
                {'pubinfo_freetext': 'Phys. Lett. 12 (1964) 132-133'}
            ]
        })
        latex = Latex(pubinfo_freetext, 'latex_eu')

        expected = 'Phys. Lett. 12 (1964) 132-133'
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    def test_get_publi_info_from_publication_info_a_list_of_two_elements(self):
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
        latex = Latex(publication_info_a_list_of_two_elements, 'latex_eu')

        expected = [
            'Int.\\ J.\\ Theor.\\ Phys.\\  {\\bf 38} (1999) 1113',
            '[Adv.\\ Theor.\\ Math.\\ Phys.\\  {\\bf 2} (1998) 231]'
        ]
        result = latex._get_publi_info()

        self.assertEqual(expected, result)

    @mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
    @mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
    def test_get_report_number_no_publi_info_yes_arxiv(self, g_a, g_p_i):
        g_a.return_value = False
        g_p_i.return_value = True

        record = Record({})
        latex = Latex(record, 'latex_eu')

        self.assertIsNone(latex._get_report_number())

    @mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
    @mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
    def test_get_report_number_yes_publi_info_no_arxiv(self, g_a, g_p_i):
        g_a.return_value = True
        g_p_i.return_value = False

        record = Record({})
        latex = Latex(record, 'latex_eu')

        self.assertIsNone(latex._get_report_number())

    @mock.patch('inspirehep.utils.latex.Latex._get_publi_info')
    @mock.patch('inspirehep.utils.latex.Latex._get_arxiv')
    def test_get_report_number_yes_publi_info_yes_arxiv(self, g_a, g_p_i):
        g_a.return_value = True
        g_p_i.return_value = True

        record = Record({})
        latex = Latex(record, 'latex_eu')

        self.assertIsNone(latex._get_report_number())
