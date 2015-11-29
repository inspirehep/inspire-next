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
from invenio.base.globals import cfg

from dojson.contrib.marc21.utils import create_record

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite
from inspire.dojson.hep import hep
from invenio.base.wrappers import lazy_import
Cv_latex = lazy_import('inspire.utils.cv_latex.Cv_latex')


class CvLatexTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspire.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        record = create_record(self.marcxml)

        self.hep_record = hep.do(record)

        self.sample_cv_latex = {
            'author': 'G.~Aad',
            'title': "{\\bf ``\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n''}",
            'publi_info': ['Eur.\ Phys.\ J.\ C {\\bf 75}, no. 7, 318 (2015)', '[Eur.\ Phys.\ J.\ C {\\bf 75}, no. 10, 463 (2015)]'],
            'url': cfg['CFG_SITE_URL'] + '/record/1351762',
            'date': 'Mar 11, 2015'
        }

    def test_author(self):
        """Test if author is created correctly"""
        self.assertEqual(self.sample_cv_latex['author'],
                         Cv_latex(self.hep_record)._get_author()[0])

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.sample_cv_latex['title'],
                         Cv_latex(self.hep_record)._get_title())

    def test_publi_info(self):
        """Test if publication info is created correctly"""
        self.assertEqual(self.sample_cv_latex['publi_info'],
                         Cv_latex(self.hep_record).
                         _get_publi_info())

    def test_url(self):
        """Test if url is created correctly"""
        self.assertEqual(self.sample_cv_latex['url'],
                         Cv_latex(self.hep_record).
                         _get_url())

    def test_date(self):
        """Test if date is created correctly"""
        self.assertEqual(self.sample_cv_latex['date'],
                         Cv_latex(self.hep_record).
                         _get_date())

TEST_SUITE = make_test_suite(CvLatexTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
