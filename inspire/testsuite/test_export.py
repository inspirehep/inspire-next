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
Export = lazy_import('inspire.utils.export.Export')


class ExportTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspire.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        record = create_record(self.marcxml)

        self.hep_record = hep.do(record)

        self.sample_export_good = {
            'citation_key': 'Aad:2015wqa',
            'doi': '10.1140/epjc/s10052-015-3661-9, 10.1140/epjc/s10052-015-3518-2',
            'arxiv_field': {u'categories': [u'hep-ex'], u'value': u'arXiv:1503.03290'},
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'reportNumber': 'CERN-PH-EP-2015-038',
            'SLACcitation': '%%CITATION = ARXIV:1503.03290;%%',
        }

    def test_citation_key(self):
        """Test if citation key is created correctly"""
        self.assertEqual(self.sample_export_good['citation_key'],
                         Export(self.hep_record)._get_citation_key())

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(self.sample_export_good['doi'],
                         Export(self.hep_record)._get_doi())

    def test_arxiv_field(self):
        """Test if arxiv_field is created correctly"""
        self.assertEqual(self.sample_export_good['arxiv_field'],
                         Export(self.hep_record).arxiv_field)

    def test_arxiv(self):
        """Test if arxiv is created correctly"""
        self.assertEqual(self.sample_export_good['arxiv'],
                         Export(self.hep_record)._get_arxiv())

    def test_report_number(self):
        """Test if report number is created correctly"""
        self.assertEqual(self.sample_export_good['reportNumber'],
                         Export(self.hep_record)._get_report_number())

    def test_slac_citations(self):
        """Test if slac citation is created correctly"""
        self.assertEqual(self.sample_export_good['SLACcitation'],
                         Export(self.hep_record)._get_slac_citation())

TEST_SUITE = make_test_suite(ExportTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
