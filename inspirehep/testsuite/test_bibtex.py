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
from inspirehep.dojson.hep import hep
from invenio.base.wrappers import lazy_import
Bibtex = lazy_import('inspirehep.utils.bibtex.Bibtex')


class BibtexTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspirehep.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        record = create_record(self.marcxml)

        self.hep_record = hep.do(record)

        self.bibtex = Bibtex(self.hep_record)

        self.sample_bibtex = {
            'collections': ('article', 'article'),
            'citation_key': 'Aad:2015wqa',
            'author': 'Aad, Georges',
            'title': '\nSearch for supersymmetry in events containing a same-flavour opposite-sign dilepton pair, jets, and large missing transverse momentum in $\sqrt{s}=8$ TeV $pp$ collisions with the ATLAS detector\n',
            'collaboration': 'ATLAS',
            'journal': 'Eur. Phys. J.',
            'volume': 'C75',
            'year': 2015,
            'number': '7',
            'pages': '318',
            'doi': '10.1140/epjc/s10052-015-3661-9, 10.1140/epjc/s10052-015-3518-2',
            'note': '[Erratum: Eur. Phys. J.C75,no.10,463(2015)]',
            'eprint': '1503.03290',
            'archivePrefix': 'arXiv',
            'primaryClass': 'hep-ex',
            'reportNumber': 'CERN-PH-EP-2015-038',
            'SLACcitation': '%%CITATION = ARXIV:1503.03290;%%',

        }

    def test_entry_type(self):
        """Test if entry type is created correctly"""
        self.assertEqual(self.sample_bibtex['collections'],
                         self.bibtex._get_entry_type())

    def test_citation_key(self):
        """Test if citation key is created correctly"""
        self.assertEqual(self.sample_bibtex['citation_key'],
                         self.bibtex._get_citation_key())

    def test_author(self):
        """Test if author is created correctly"""
        self.assertEqual(self.sample_bibtex['author'],
                         self.bibtex._get_author()[0])

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.sample_bibtex['title'],
                         self.bibtex._get_title())

    def test_collaboration(self):
        """Test if collaboration is created correctly"""
        self.assertEqual(self.sample_bibtex['collaboration'],
                         self.bibtex._get_collaboration())

    def test_journal(self):
        """Test if journal is created correctly"""
        self.assertEqual(self.sample_bibtex['journal'],
                         self.bibtex._get_journal())

    def test_volume(self):
        """Test if volume is created correctly"""
        self.assertEqual(self.sample_bibtex['volume'],
                         self.bibtex._get_volume())

    def test_year(self):
        """Test if year is created correctly"""
        self.assertEqual(self.sample_bibtex['year'],
                         self.bibtex._get_year())

    def test_number(self):
        """Test if number is created correctly"""
        self.assertEqual(self.sample_bibtex['number'],
                         self.bibtex._get_number())

    def test_pages(self):
        """Test if pages is created correctly"""
        self.assertEqual(self.sample_bibtex['pages'],
                         self.bibtex._get_pages())

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(self.sample_bibtex['doi'],
                         self.bibtex._get_doi())

    def test_note(self):
        """Test if note is created correctly"""
        self.assertEqual(self.sample_bibtex['note'],
                         self.bibtex._get_note())

    def test_eprint(self):
        """Test if eprint is created correctly"""
        self.assertEqual(self.sample_bibtex['eprint'],
                         self.bibtex._get_eprint())

    def test_archivePrefix(self):
        """Test if archive prefix is created correctly"""
        self.assertEqual(self.sample_bibtex['archivePrefix'],
                         self.bibtex._get_archive_prefix())

    def test_primary_class(self):
        """Test if primary class is created correctly"""
        self.assertEqual(self.sample_bibtex['primaryClass'],
                         self.bibtex._get_primary_class())

    def test_report_number(self):
        """Test if report number is created correctly"""
        self.assertEqual(self.sample_bibtex['reportNumber'],
                         self.bibtex._get_report_number())

    def test_slac_citations(self):
        """Test if slac citation is created correctly"""
        self.assertEqual(self.sample_bibtex['SLACcitation'],
                         self.bibtex._get_slac_citation())
TEST_SUITE = make_test_suite(BibtexTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
