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
from inspirehep.dojson.hep import hep2marc, hep


class HepRecordsTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('tests',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hep_record.xml')
                                                     )
        record = create_record(self.marcxml)

        self.marcxml_to_json = hep.do(record)
        self.json_to_marc = hep2marc.do(self.marcxml_to_json)

    def test_isbns(self):
        """Test if isbns is created correctly"""
        self.assertEqual(self.marcxml_to_json['isbns'][0]['value'],
                         self.json_to_marc['020'][0]['a'])
        self.assertEqual(self.marcxml_to_json['isbns'][0]['medium'],
                         self.json_to_marc['020'][0]['b'])

    def test_dois(self):
        """Test if dois is created correctly"""
        self.assertTrue(self.marcxml_to_json['dois'][0]['value'] in
                        [p.get('a') for p in self.json_to_marc['024'] if 'a' in p])

    def test_persistent_identifiers(self):
        """Test if persistent_identifiers is created correctly"""
        self.assertTrue(self.marcxml_to_json['persistent_identifiers'][0]['value'] in
                        [p.get('a') for p in self.json_to_marc['024'] if 'a' in p])

    def test_external_system_numbers(self):
        """Test if system control number is created correctly"""
        self.assertEqual(self.marcxml_to_json['external_system_numbers']
                         [0]['institute'],
                         self.json_to_marc['035'][0]['9'])
        self.assertEqual(self.marcxml_to_json['external_system_numbers']
                         [0]['value'],
                         self.json_to_marc['035'][0]['a'])
        self.assertEqual(self.marcxml_to_json['external_system_numbers']
                         [0]['obsolete'],
                         self.json_to_marc['035'][0]['z'])

    def test_report_numbers(self):
        """Test if report number is created correctly"""
        self.assertTrue(self.marcxml_to_json['report_numbers'][0]['source'] in
                        [a.get('9') for a in self.json_to_marc['037'] if '9' in a])
        self.assertTrue(self.marcxml_to_json['report_numbers'][0]['value'] in
                        [a.get('a') for a in self.json_to_marc['037'] if 'a' in a])

    def test_arxiv_eprints(self):
        """Test if arxiv eprints is created correctly"""
        self.assertEqual(self.marcxml_to_json['arxiv_eprints'][0]
                         ['categories'],
                         [c.get('c')[0] for c in self.json_to_marc['037'] if 'c' in c])
        self.assertTrue(self.marcxml_to_json['arxiv_eprints'][0]['value'] in
                        [a.get('a') for a in self.json_to_marc['037'] if 'a' in a])

    def test_languages(self):
        """Test if languages is created correctly"""
        self.assertEqual(self.marcxml_to_json['languages'][0],
                         self.json_to_marc['041'][0]['a'])

    def test_classification_number(self):
        """Test if classification_number is created correctly"""
        for index, val in enumerate(
                self.marcxml_to_json['classification_number']):
            self.assertEqual(val['classification_number'],
                             self.json_to_marc['084'][index]['a'])
            self.assertEqual(val['source'],
                             self.json_to_marc['084'][index]['9'])
            self.assertEqual(val['standard'],
                             self.json_to_marc['084'][index]['2'])

    def test_authors(self):
        """Test if authors are created correctly"""
        self.assertEqual(self.marcxml_to_json['authors'][0]['full_name'],
                         self.json_to_marc['100']['a'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['role'],
                         self.json_to_marc['100']['e'])
        self.assertEqual(self.marcxml_to_json['authors']
                         [0]['alternative_name'],
                         self.json_to_marc['100']['q'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['inspire_id'],
                         self.json_to_marc['100']['i'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['orcid'],
                         self.json_to_marc['100']['j'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['email'],
                         self.json_to_marc['100']['m'])
        self.assertEqual(self.marcxml_to_json['authors'][0]['affiliations'][0]
                         ['value'],
                         self.json_to_marc['100']['u'][0])
        self.assertEqual(self.marcxml_to_json['authors'][0]['recid'],
                         self.json_to_marc['100']['x'])
        self.assertEqual(self.marcxml_to_json['authors'][0]
                         ['curated_relation'],
                         self.json_to_marc['100']['y'])

    def test_corporate_author(self):
        """Test if corporate_author is created correctly"""
        self.assertEqual(self.marcxml_to_json['corporate_author'][0],
                         self.json_to_marc['110'][0]['a'])

    def test_title_variation(self):
        """Test if title_variation is created correctly"""
        self.assertEqual(self.marcxml_to_json['title_variation']
                         [0],
                         self.json_to_marc['210'][0]['a'])

    def test_title_translation(self):
        """Test if title_translation is created correctly"""
        self.assertEqual(self.marcxml_to_json['title_translation']
                         [0]['title'],
                         self.json_to_marc['242'][0]['a'])
        self.assertEqual(self.marcxml_to_json['title_translation']
                         [0]['subtitle'],
                         self.json_to_marc['242'][0]['b'])

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(self.marcxml_to_json['titles'][0]['title'],
                         self.json_to_marc['245'][0]['a'])

    def test_breadcrumb_title(self):
        """Test if breadcrumb title is created correctly"""
        titles = [d.get('a') for d in self.json_to_marc['245']]
        self.assertTrue(self.marcxml_to_json['breadcrumb_title'] in titles)

    def test_title_arxiv(self):
        """Test if title arxiv is created correctly"""
        def get(key):
            return [d.get(key) for d in self.marcxml_to_json['titles']]

        self.assertTrue(self.json_to_marc['246']['9'] in get('source'))
        self.assertTrue(self.json_to_marc['246']['b'] in get('subtitle'))
        self.assertTrue(self.json_to_marc['246']['a'] in get('title'))

    def test_titles_old(self):
        """Test if titles_old is created correctly"""
        self.assertEqual(self.marcxml_to_json['titles_old'][0]['source'],
                         self.json_to_marc['247'][0]['9'])
        self.assertEqual(self.marcxml_to_json['titles_old'][0]['subtitle'],
                         self.json_to_marc['247'][0]['b'])
        self.assertEqual(self.marcxml_to_json['titles_old'][0]['title'],
                         self.json_to_marc['247'][0]['a'])

    def test_imprints(self):
        """Test if imprints is created correctly"""
        self.assertEqual(self.marcxml_to_json['imprints'][0]['place'],
                         self.json_to_marc['260'][0]['a'])
        self.assertEqual(self.marcxml_to_json['imprints'][0]['publisher'],
                         self.json_to_marc['260'][0]['b'])
        self.assertEqual(self.marcxml_to_json['imprints'][0]['date'],
                         self.json_to_marc['260'][0]['c'])

    def test_preprint_date(self):
        """Test if preprint_date is created correctly"""
        self.assertEqual(self.marcxml_to_json['preprint_date'],
                         self.json_to_marc['269'][0]['c'])

    def test_page_nr(self):
        """Test if page_nr is created correctly"""
        self.assertEqual(self.marcxml_to_json['page_nr'][0],
                         self.json_to_marc['300'][0]['a'])

    def test_book_series(self):
        """Test if book_series is created correctly"""
        self.assertEqual(self.marcxml_to_json['book_series'][0]['value'],
                         self.json_to_marc['490'][0]['a'])
        self.assertEqual(self.marcxml_to_json['book_series'][0]['volume'],
                         self.json_to_marc['490'][0]['v'])

    def test_public_notes(self):
        """Test if public_notes is created correctly"""
        self.assertEqual(self.marcxml_to_json['public_notes'][0]['value'],
                         self.json_to_marc['500'][0]['a'])
        self.assertEqual(self.marcxml_to_json['public_notes'][0]['source'],
                         self.json_to_marc['500'][0]['9'])

    def test_hidden_notes(self):
        """Test if hidden_notes is created correctly"""
        self.assertEqual(self.marcxml_to_json['hidden_notes'][0]['value'],
                         self.json_to_marc['595'][0]['a'])
        self.assertEqual(self.marcxml_to_json['hidden_notes'][0]
                         ['cern_reference'],
                         self.json_to_marc['595'][0]['b'])
        self.assertEqual(self.marcxml_to_json['hidden_notes'][0]['cds'],
                         self.json_to_marc['595'][0]['c'])
        self.assertEqual(self.marcxml_to_json['hidden_notes'][0]['source'],
                         self.json_to_marc['595'][0]['9'])

    def test_thesis(self):
        """Test if thesis is created correctly"""
        self.assertEqual(self.marcxml_to_json['thesis'][0]['degree_type'],
                         self.json_to_marc['502'][0]['b'])
        self.assertEqual(self.marcxml_to_json['thesis'][0]
                         ['university'],
                         self.json_to_marc['502'][0]['c'])
        self.assertEqual(self.marcxml_to_json['thesis'][0]['date'],
                         self.json_to_marc['502'][0]['d'])

    def test_abstract(self):
        """Test if abstract is created correctly"""
        self.assertEqual(self.marcxml_to_json['abstracts'][0]['value'],
                         self.json_to_marc['520'][0]['a'])
        self.assertEqual(self.marcxml_to_json['abstracts'][0]
                         ['source'],
                         self.json_to_marc['520'][0]['9'])

    def test_funding_info(self):
        """Test if funding_info is created correctly"""
        self.assertEqual(self.marcxml_to_json['funding_info'][0]['agency'],
                         self.json_to_marc['536'][0]['a'])
        self.assertEqual(self.marcxml_to_json['funding_info'][0]
                         ['grant_number'],
                         self.json_to_marc['536'][0]['c'])
        self.assertEqual(self.marcxml_to_json['funding_info'][0]
                         ['project_number'],
                         self.json_to_marc['536'][0]['f'])

    def test_licence(self):
        """Test if license is created correctly"""
        self.assertEqual(self.marcxml_to_json['license'][0]['license'],
                         self.json_to_marc['540'][0]['a'])
        self.assertEqual(self.marcxml_to_json['license'][0]['imposing'],
                         self.json_to_marc['540'][0]['b'])
        self.assertEqual(self.marcxml_to_json['license'][0]['url'],
                         self.json_to_marc['540'][0]['u'])
        self.assertEqual(self.marcxml_to_json['license'][0]['material'],
                         self.json_to_marc['540'][0]['3'])

    def test_acquisition_source(self):
        """Test if acquisition_source is created correctly"""
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]
                         ['source'],
                         self.json_to_marc['541'][0]['a'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]
                         ['email'],
                         self.json_to_marc['541'][0]['b'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]
                         ['method'],
                         self.json_to_marc['541'][0]['c'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['date'],
                         self.json_to_marc['541'][0]['d'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]
                         ['submission_number'],
                         self.json_to_marc['541'][0]['e'])

    def test_copyright(self):
        """Test if copyright is created correctly"""
        self.assertEqual(self.marcxml_to_json['copyright'][0]['material'],
                         self.json_to_marc['542'][0]['3'])
        self.assertEqual(self.marcxml_to_json['copyright'][0]['holder'],
                         self.json_to_marc['542'][0]['d'])
        self.assertEqual(self.marcxml_to_json['copyright'][0]['statement'],
                         self.json_to_marc['542'][0]['f'])
        self.assertEqual(self.marcxml_to_json['copyright'][0]['url'],
                         self.json_to_marc['542'][0]['u'])

    def test_subject_terms(self):
        """Test if subject term is created correctly"""
        self.assertEqual(self.marcxml_to_json['subject_terms'][0]['scheme'],
                         self.json_to_marc['65017'][0]['2'])
        self.assertEqual(self.marcxml_to_json['subject_terms'][0]['term'],
                         self.json_to_marc['65017'][0]['a'])
        self.assertEqual(self.marcxml_to_json['subject_terms'][0]['source'],
                         self.json_to_marc['65017'][0]['9'])

    def test_free_keywords(self):
        """Test if free_keywords is created correctly"""
        self.assertEqual(self.marcxml_to_json['free_keywords'][0]['value'],
                         self.json_to_marc['653'][0]['a'])
        self.assertEqual(self.marcxml_to_json['free_keywords'][0]['source'],
                         self.json_to_marc['653'][0]['9'])

    def test_accelerator_experiments(self):
        """Test if accelerator_experiment is created correctly"""
        self.assertEqual(self.marcxml_to_json['accelerator_experiments'][0]
                         ['accelerator'],
                         self.json_to_marc['693'][0]['a'])
        self.assertEqual(self.marcxml_to_json['accelerator_experiments'][0]
                         ['experiment'],
                         self.json_to_marc['693'][0]['e'])

    def test_thesaurus_terms(self):
        """Test if thesaurus_terms is created correctly"""
        self.assertEqual(self.marcxml_to_json['thesaurus_terms'][0]
                         ['classification_scheme'],
                         self.json_to_marc['695'][0]['2'])
        self.assertEqual(self.marcxml_to_json['thesaurus_terms'][0]
                         ['energy_range'],
                         self.json_to_marc['695'][0]['e'])
        self.assertEqual(self.marcxml_to_json['thesaurus_terms'][0]
                         ['keyword'],
                         self.json_to_marc['695'][0]['a'])

    def test_thesis_supervisor(self):
        """Test if thesis_supervisor is created correctly"""
        self.assertEqual(self.marcxml_to_json['thesis_supervisor'][0]
                         ['full_name'],
                         self.json_to_marc['701'][0]['a'])
        self.assertEqual(self.marcxml_to_json['thesis_supervisor'][0]
                         ['INSPIRE_id'],
                         self.json_to_marc['701'][0]['g'])
        self.assertEqual(self.marcxml_to_json['thesis_supervisor'][0]
                         ['external_id'],
                         self.json_to_marc['701'][0]['j'])
        self.assertEqual(self.marcxml_to_json['thesis_supervisor'][0]
                         ['affiliation'],
                         self.json_to_marc['701'][0]['u'])

    def test_collaboration(self):
        """Test if collaboration is created correctly"""
        self.assertEqual(self.marcxml_to_json['collaboration'][0],
                         self.json_to_marc['710'][0]['g'])

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
                         [0]['recid'],
                         self.json_to_marc['773'][0]['0'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['year'],
                         self.json_to_marc['773'][0]['y'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['conf_acronym'],
                         self.json_to_marc['773'][0]['o'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['reportnumber'],
                         self.json_to_marc['773'][0]['r'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['confpaper_info'],
                         self.json_to_marc['773'][0]['t'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['cnum'],
                         self.json_to_marc['773'][0]['w'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['pubinfo_freetext'],
                         self.json_to_marc['773'][0]['x'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['isbn'],
                         self.json_to_marc['773'][0]['z'])
        self.assertEqual(self.marcxml_to_json['publication_info']
                         [0]['note'],
                         self.json_to_marc['773'][0]['m'])

    def test_succeeding_entry(self):
        """Test if succeeding_entry is created correctly"""
        self.assertEqual(self.marcxml_to_json['succeeding_entry']
                         ['relationship_code'],
                         self.json_to_marc['785']['r'])
        self.assertEqual(self.marcxml_to_json['succeeding_entry']['recid'],
                         self.json_to_marc['785']['w'])
        self.assertEqual(self.marcxml_to_json['succeeding_entry']['isbn'],
                         self.json_to_marc['785']['z'])

    def test_url(self):
        """Test if url is created correctly"""
        self.assertEqual(self.marcxml_to_json['urls'][0]['url'],
                         self.json_to_marc['8564'][0]['u'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['size'],
                         self.json_to_marc['8564'][0]['s'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['doc_string'],
                         self.json_to_marc['8564'][0]['w'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['description'],
                         self.json_to_marc['8564'][0]['y'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['material_type'],
                         self.json_to_marc['8564'][0]['3'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['comment'],
                         self.json_to_marc['8564'][0]['z'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['name'],
                         self.json_to_marc['8564'][0]['f'])

    def test_oai_pmh(self):
        """Test if oal_pmh is created correctly"""
        self.assertEqual(self.marcxml_to_json['oai_pmh'][0]['id'],
                         self.json_to_marc['909CO'][0]['o'])
        self.assertEqual(self.marcxml_to_json['oai_pmh'][0]['set'],
                         self.json_to_marc['909CO'][0]['p'])

    def test_collections(self):
        """Test if collections is created correctly"""
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
        self.assertEqual(self.marcxml_to_json['refextract'][0]['comment'],
                         self.json_to_marc['999C6'][0]['c'])
        self.assertEqual(self.marcxml_to_json['refextract'][0]['source'],
                         self.json_to_marc['999C6'][0]['s'])

TEST_SUITE = make_test_suite(HepRecordsTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
