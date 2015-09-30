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

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
from inspire.dojson.hep import hep2marc, hep
from dojson.contrib.marc21.utils import create_record
import pkg_resources
import os


class HepRecordsTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('inspire.testsuite',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_record.xml')
                                                     )
        record = create_record(self.marcxml)

        self.marcxml_to_json = hep.do(record)
        self.json_to_marc = hep2marc.do(self.marcxml_to_json)

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(self.marcxml_to_json['doi'][0]['doi'],
                         self.json_to_marc['024'][0]['a'])

    def test_authors(self):
        """Test if authors are created correctly"""
        self.assertEqual(self.marcxml_to_json['authors'][0]['full_name'],
                         self.json_to_marc['100']['a'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['relator_term'],
                         self.json_to_marc['100']['e'])
        self.assertEqual(self.marcxml_to_json['authors']
                         [0]['alternative_name'],
                         self.json_to_marc['100']['q'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['INSPIRE_id'],
                         self.json_to_marc['100']['i'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['external_id'],
                         self.json_to_marc['100']['j'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['e_mail'],
                         self.json_to_marc['100']['m'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['affiliation'],
                         self.json_to_marc['100']['u'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['profile'],
                         self.json_to_marc['100']['x'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['claimed'],
                         self.json_to_marc['100']['y'])

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.marcxml_to_json['title'][0]['title'],
                         self.json_to_marc['245'][0]['a'])

    def test_subject_term(self):
        """Test if subject term is created correctly"""
        self.assertEqual(self.marcxml_to_json['subject_term'][0]['scheme'],
                         self.json_to_marc['65017'][0]['2'])
        self.assertEqual(self.marcxml_to_json['subject_term'][0]['value'],
                         self.json_to_marc['65017'][0]['a'])

    def test_publication_info(self):
        """Test if publication info is created correctly"""
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['page_artid'],
                         self.json_to_marc['773'][0]['c'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['journal_issue'],
                         self.json_to_marc['773'][0]['n'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['journal_title'],
                         self.json_to_marc['773'][0]['p'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['journal_volume'],
                         self.json_to_marc['773'][0]['v'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['year'],
                         self.json_to_marc['773'][0]['y'])

    def test_url(self):
        """Test if url is created correctly"""
        self.assertEqual(self.marcxml_to_json['url'][0]['url'],
                         self.json_to_marc['8564'][0]['u'])
        self.assertEqual(self.marcxml_to_json['url'][0]['size'],
                         self.json_to_marc['8564'][0]['s'])

    def test_oai_pmh(self):
        """Test if oal_pmh is created correctly"""
        self.assertEqual(self.marcxml_to_json['oai_pmh'][0]['id'],
                         self.json_to_marc['909CO'][0]['o'])
        self.assertEqual(self.marcxml_to_json['oai_pmh'][0]['set'],
                         self.json_to_marc['909CO'][0]['p'])

    def test_collections(self):
        for index, val in enumerate(self.marcxml_to_json['collections']):
            if 'primary' in val:
                self.assertEqual(val['primary'],
                                 self.json_to_marc['980'][index]['a'])

    def test_references(self):
        """Test if references are created correctly"""
        for index, val in enumerate(self.marcxml_to_json['references']):
            if 'recid' in val:
                self.assertEqual(val['recid'],
                                 self.json_to_marc['999C5'][index]['0'])
            if 'texkey' in val:
                self.assertEqual(val['texkey'],
                                 self.json_to_marc['999C5'][index]['1'])
            if 'doi' in val:
                self.assertEqual(val['doi'],
                                 self.json_to_marc['999C5'][index]['a'])
            if 'collaboration' in val:
                self.assertEqual(val['collaboration'],
                                 self.json_to_marc['999C5'][index]['c'])
            if 'editors' in val:
                self.assertEqual(val['editors'],
                                 self.json_to_marc['999C5'][index]['e'])
            if 'authors' in val:
                self.assertEqual(val['authors'],
                                 self.json_to_marc['999C5'][index]['h'])
            if 'misc' in val:
                self.assertEqual(val['misc'],
                                 self.json_to_marc['999C5'][index]['m'])
            if 'number' in val:
                self.assertEqual(val['number'],
                                 self.json_to_marc['999C5'][index]['o'])
            if 'isbn' in val:
                self.assertEqual(val['isbn'],
                                 self.json_to_marc['999C5'][index]['i'])
            if 'publisher' in val:
                self.assertEqual(val['publisher'],
                                 self.json_to_marc['999C5'][index]['p'])
            if 'maintitle' in val:
                self.assertEqual(val['maintitle'],
                                 self.json_to_marc['999C5'][index]['q'])
            if 'report_number' in val:
                self.assertEqual(val['report_number'],
                                 self.json_to_marc['999C5'][index]['r'])
            if 'title' in val:
                self.assertEqual(val['title'],
                                 self.json_to_marc['999C5'][index]['t'])
            if 'url' in val:
                self.assertEqual(val['url'],
                                 self.json_to_marc['999C5'][index]['u'])
            if 'journal_pubnote' in val:
                self.assertEqual(val['journal_pubnote'],
                                 self.json_to_marc['999C5'][index]['s'])
            if 'raw_reference' in val:
                self.assertEqual(val['raw_reference'],
                                 self.json_to_marc['999C5'][index]['x'])
            if 'year' in val:
                self.assertEqual(val['year'],
                                 self.json_to_marc['999C5'][index]['y'])

    def test_refextract(self):
        """Test if refextract is created correctly"""
        self.assertEqual(self.marcxml_to_json['refextract'][0]['time'],
                         self.json_to_marc['999C6'][0]['t'])
        self.assertEqual(self.marcxml_to_json['refextract'][0]['version'],
                         self.json_to_marc['999C6'][0]['v'])

    def test_system_control_number(self):
        """Test if system control number is created correctly"""
        self.assertEqual(self.marcxml_to_json['system_control_number']
                         [0]['institute'],
                         self.json_to_marc['035'][0]['9'])
        self.assertEqual(self.marcxml_to_json['system_control_number']
                         [0]['system_control_number'],
                         self.json_to_marc['035'][0]['a'])

    def test_report_number(self):
        """Test if report number is created correctly"""
        self.assertEqual(self.marcxml_to_json['report_number'][0]['source'],
                         self.json_to_marc['037'][1]['9'])
        self.assertEqual(self.marcxml_to_json['report_number'][0]['value'],
                         self.json_to_marc['037'][1]['a'])

    def test_arxiv_eprints(self):
        """Test if arxiv eprints is created correctly"""
        self.assertEqual(self.marcxml_to_json['arxiv_eprints'][0]
                         ['categories'],
                         self.json_to_marc['037'][0]['c'])
        self.assertEqual(self.marcxml_to_json['arxiv_eprints'][0]['value'],
                         self.json_to_marc['037'][0]['a'])

TEST_SUITE = make_test_suite(HepRecordsTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
