# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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
import time
Export = lazy_import('inspirehep.utils.export.Export')


class ExportTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('tests',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_formats.xml')
                                                     )
        self.marcxml_for_citations = pkg_resources.resource_string('tests',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_citation_line.xml')
                                                     )
        record = create_record(self.marcxml)

        record_for_citation = create_record(self.marcxml_for_citations)

        self.hep_record = hep.do(record)

        self.hep_record_citation = hep.do(record_for_citation)

        self.export = Export(self.hep_record)

        self.export_citation = Export(self.hep_record_citation)

        self.sample_export_good = {
            'citation_key': 'Aad:2015wqa',
            'doi': '10.1140/epjc/s10052-015-3661-9, 10.1140/epjc/s10052-015-3518-2',
            'arxiv_field': {u'categories': [u'hep-ex'], u'value': u'arXiv:1503.03290'},
            'arxiv': 'arXiv:1503.03290 [hep-ex]',
            'reportNumber': 'CERN-PH-EP-2015-038',
            'SLACcitation': '%%CITATION = ARXIV:1503.03290;%%',
        }

        self.sample_export_good_citation_line = {
            'citation_count': '2 citations counted in INSPIRE as of ' +
            time.strftime("%d %b %Y")
        }

    def test_citation_key(self):
        """Test if citation key is created correctly"""
        self.assertEqual(self.sample_export_good['citation_key'],
                         self.export._get_citation_key())

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(self.sample_export_good['doi'],
                         self.export._get_doi())

    def test_arxiv_field(self):
        """Test if arxiv_field is created correctly"""
        self.assertEqual(self.sample_export_good['arxiv_field']['value'],
                         self.export.arxiv_field['value'])
        self.assertTrue(len(self.export.arxiv_field['categories']) == 1)
        self.assertEqual(self.sample_export_good['arxiv_field']['categories'][0],
                         self.export.arxiv_field['categories'][0])

    def test_arxiv(self):
        """Test if arxiv is created correctly"""
        self.assertEqual(self.sample_export_good['arxiv'],
                         self.export._get_arxiv())

    def test_report_number(self):
        """Test if report number is created correctly"""
        self.assertEqual(self.sample_export_good['reportNumber'],
                         self.export._get_report_number())

    def test_slac_citations(self):
        """Test if slac citation is created correctly"""
        self.assertEqual(self.sample_export_good['SLACcitation'],
                         self.export._get_slac_citation())

    def test_citation_count(self):
        self.assertEqual(self.sample_export_good_citation_line[
                         'citation_count'],
                         self.export_citation._get_citation_number())

TEST_SUITE = make_test_suite(ExportTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
