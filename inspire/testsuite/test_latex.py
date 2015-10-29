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

import pkg_resources
import os

from dojson.contrib.marc21.utils import create_record

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite
from inspire.dojson.hep import hep
from invenio.base.wrappers import lazy_import
Latex = lazy_import('inspire.utils.latex.Latex')


class LatexTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspire.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        record = create_record(self.marcxml)

        self.hep_record = hep.do(record)

        self.latex_eu = Latex(self.hep_record, 'latex_eu')

        self.latex_us = Latex(self.hep_record, 'latex_us')

        self.sample_latex_eu = {
            'citation_key': 'Aad:2015wqa',
            'author': 'G.~Aad',
            'title': '\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n',
            'publi_info': ['Eur.\ Phys.\ J.\ C {\\bf 75} (2015) 7,  318', '[Eur.\ Phys.\ J.\ C {\\bf 75} (2015) 10,  463]'],
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'report_number': '',
            'SLACcitation': '%%CITATION = ARXIV:1503.03290;%%',

        }

        self.sample_latex_us = {
            'citation_key': 'Aad:2015wqa',
            'author': 'G.~Aad',
            'title': '\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n',
            'publi_info': ['Eur.\ Phys.\ J.\ C {\\bf 75}, no. 7, 318 (2015)', '[Eur.\ Phys.\ J.\ C {\\bf 75}, no. 10, 463 (2015)]'],
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'report_number': '',
            'SLACcitation': '%%CITATION = ARXIV:1503.03290;%%',

        }

    def test_citation_key(self):
        """Test if citation_key is created correctly"""
        self.assertEqual(self.sample_latex_eu['citation_key'],
                         self.latex_eu._get_citation_key())

        self.assertEqual(self.sample_latex_us['citation_key'],
                         self.latex_us._get_citation_key())

    def test_author(self):
        """Test if author is created correctly"""
        self.assertEqual(self.sample_latex_eu['author'],
                         self.latex_eu._get_author()[0])

        self.assertEqual(self.sample_latex_us['author'],
                         self.latex_us._get_author()[0])

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.sample_latex_eu['title'],
                         self.latex_eu._get_title())

        self.assertEqual(self.sample_latex_us['title'],
                         self.latex_us._get_title())

    def test_publi_info(self):
        """Test if publication info is created correctly"""
        self.assertEqual(self.sample_latex_eu['publi_info'],
                         self.latex_eu._get_publi_info())

        self.assertEqual(self.sample_latex_us['publi_info'],
                         self.latex_us._get_publi_info())

    def test_arxiv(self):
        """Test if arxiv is created correctly"""
        self.assertEqual(self.sample_latex_eu['arxiv'],
                         self.latex_eu._get_arxiv())

        self.assertEqual(self.sample_latex_us['arxiv'],
                         self.latex_us._get_arxiv())

    def test_slac_citation(self):
        """Test if slac citation is created correctly"""
        self.assertEqual(self.sample_latex_eu['SLACcitation'],
                         self.latex_eu._get_slac_citation())

        self.assertEqual(self.sample_latex_us['SLACcitation'],
                         self.latex_us._get_slac_citation())
TEST_SUITE = make_test_suite(LatexTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
