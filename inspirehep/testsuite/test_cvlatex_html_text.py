# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

import os

from dojson.contrib.marc21.utils import create_record

from inspire.dojson.hep import hep

from invenio.base.wrappers import lazy_import

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

import pkg_resources


Cv_latex_html_text = lazy_import('inspire.utils.cv_latex_html_text.Cv_latex_html_text')


class CvLatexHtmlTextTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspire.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        record = create_record(self.marcxml)

        self.hep_record = hep.do(record)

        self.sample_cv_latex_html = {
            'title': '\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n',
            'author': 'Georges Aad',
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'doi': '10.1140/epjc/s10052-015-3661-9, 10.1140/epjc/s10052-015-3518-2',
            'publi_info': ['Eur.Phys.J. C75 (2015) 7, 318', 'Eur.Phys.J. C75 (2015) 10, 463']

        }

        self.sample_cv_latex_text = {
            'title': '\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n',
            'author': 'Georges Aad',
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'doi': '10.1140/epjc/s10052-015-3661-9, 10.1140/epjc/s10052-015-3518-2',
            'publi_info': ['Eur.Phys.J. C75 (2015) 7, 318', 'Eur.Phys.J. C75 (2015) 10, 463']

        }

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.sample_cv_latex_html['title'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_html', "<br/>").
                         _get_title())

        self.assertEqual(self.sample_cv_latex_text['title'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_text', "\n").
                         _get_title())

    def test_author(self):
        """Test if author is created correctly"""
        self.assertEqual(self.sample_cv_latex_html['author'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_html', "<br/>").
                         _get_author()[0])

        self.assertEqual(self.sample_cv_latex_text['author'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_text', "\n").
                         _get_author()[0])

    def test_arxiv(self):
        """Test if arxiv is created correctly"""
        self.assertEqual(self.sample_cv_latex_html['arxiv'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_html', "<br/>").
                         _get_arxiv())

        self.assertEqual(self.sample_cv_latex_text['arxiv'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_text', "\n").
                         _get_arxiv())

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(self.sample_cv_latex_html['doi'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_html', "<br/>").
                         _get_doi())

        self.assertEqual(self.sample_cv_latex_text['doi'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_text', "\n").
                         _get_doi())

    def test_publi_info(self):
        """Test if publication info is created correctly"""
        self.assertEqual(self.sample_cv_latex_html['publi_info'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_html', "<br/>").
                         _get_publi_info())

        self.assertEqual(self.sample_cv_latex_text['publi_info'],
                         Cv_latex_html_text(self.hep_record, 'cv_latex_text', "\n").
                         _get_publi_info())
TEST_SUITE = make_test_suite(CvLatexHtmlTextTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
