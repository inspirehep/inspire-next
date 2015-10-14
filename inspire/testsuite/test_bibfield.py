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

"""Tests for Bibfield to doJSON conversion."""

import json
import os

from inspire.modules.workflows.dojson import bibfield

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

import pkg_resources


class BibFieldToJSONTests(InvenioTestCase):

    def setUp(self):
        self.bibfield_json = json.loads(
            pkg_resources.resource_string(
                'inspire.testsuite',
                os.path.join(
                    'fixtures',
                    'test_bibfield_record.json'
                )
            )
        )
        self.record = bibfield.do(self.bibfield_json)

    def test_abstract(self):
        """Test if abstract is created correctly"""
        self.assertEqual(
            self.bibfield_json['abstract']['summary'],
            self.record['abstracts'][0]['value']
        )

    def test_system_number_external(self):
        """Test if system_number_external is created correctly"""
        self.assertEqual(
            self.bibfield_json['system_number_external'],
            self.record['external_system_numbers'][0]
        )

    def test_subject_term(self):
        """Test if subject_term is created correctly"""
        self.assertEqual(
            self.bibfield_json['subject_term'],
            self.record['subject_terms']
        )

    def test_acquisition_source(self):
        """Test if acquisition_source is created correctly"""
        self.assertEqual(
            self.bibfield_json['acquisition_source'],
            self.record['acquisition_source']
        )

    def test_collections(self):
        """Test if collections is created correctly"""
        self.assertEqual(
            self.bibfield_json['collections'],
            self.record['collections']
        )

    def test_fft(self):
        """Test if fft is created correctly"""
        self.assertEqual(
            self.bibfield_json['fft'],
            self.record['fft']
        )

    def test_license(self):
        """Test if license is created correctly"""
        self.assertEqual(
            self.bibfield_json['license'],
            self.record['license']
        )

    def test_page_nr(self):
        """Test if page_nr is created correctly"""
        self.assertEqual(
            self.bibfield_json['page_nr'],
            self.record['page_nr']
        )

    def test_references(self):
        """Test if references is created correctly"""
        self.assertEqual(
            self.bibfield_json['reference'],
            self.record['references']
        )

    def test_edition(self):
        """Test if edition is created correctly"""
        self.assertEqual(
            self.bibfield_json['edition'],
            self.record['edition']
        )

    def test_report_numbers(self):
        """Test if report_numbers is created correctly"""
        self.assertEqual(
            self.bibfield_json['report_number'][0]['primary'],
            self.record['report_numbers'][0]['value']
        )
        self.assertEqual(
            self.bibfield_json['report_number'][0]['source'],
            self.record['report_numbers'][0]['source']
        )

    def test_refextract(self):
        """Test if refextract is created correctly"""
        self.assertEqual(
            self.bibfield_json['refextract'],
            self.record['refextract']
        )

    def test_doi(self):
        """Test if doi is created correctly"""
        self.assertEqual(
            self.bibfield_json['doi'],
            self.record['dois'][0]['value']
        )

    def test_subject_terms(self):
        """Test if subject_terms is created correctly"""
        self.assertEqual(
            self.bibfield_json['subject_term'],
            self.record['subject_terms']
        )

    def test_breadcrumb_title(self):
        """Test if breadcrumb_title is created correctly"""
        self.assertEqual(
            self.bibfield_json['title']['title'],
            self.record['breadcrumb_title']
        )

    def test_corporate_author(self):
        """Test if corporate_author is created correctly"""
        self.assertEqual(
            self.bibfield_json['corporate_author'],
            self.record['corporate_author'][0]
        )

    def test_collaboration(self):
        """Test if collaboration is created correctly"""
        self.assertEqual(
            self.bibfield_json['collaboration'],
            self.record['collaboration'][0]
        )

    def test_preprint_date(self):
        """Test if preprint_date is created correctly"""
        self.assertEqual(
            self.bibfield_json['preprint_info']['date'],
            self.record['preprint_date']
        )

    def test_hidden_notes(self):
        """Test if hidden_notes is created correctly"""
        self.assertEqual(
            self.bibfield_json['hidden_note'][0]['value'],
            self.record['hidden_notes'][0]['value']
        )
        self.assertEqual(
            self.bibfield_json['hidden_note'][0]['source'],
            self.record['hidden_notes'][0]['source']
        )

    def test_public_notes(self):
        """Test if public_notes is created correctly"""
        self.assertEqual(
            self.bibfield_json['note'],
            self.record['public_notes']
        )

    def test_imprints(self):
        """Test if imprints is created correctly"""
        self.assertEqual(
            self.bibfield_json['imprint'],
            self.record['imprints'][0]
        )

    def test_oai_pmh(self):
        """Test if oai_pmh is created correctly"""
        self.assertEqual(
            self.bibfield_json['oai_pmh'],
            self.record['oai_pmh']
        )

    def test_thesis(self):
        """Test if thesis is created correctly"""
        self.assertEqual(
            self.bibfield_json['thesis'],
            self.record['thesis']
        )

    def test_isbn(self):
        """Test if isbn is created correctly"""
        self.assertEqual(
            self.bibfield_json['isbn'],
            self.record['isbns']
        )

    def test_url(self):
        """Test if url is created correctly"""
        self.assertEqual(
            self.bibfield_json['url'],
            self.record['url'][0]
        )

    def test_publication_info(self):
        """Test if publication_info is created correctly"""
        self.assertEqual(
            self.bibfield_json['publication_info'],
            self.record['publication_info'][0]
        )

    def test_free_keywords(self):
        """Test if free_keywords is created correctly"""
        self.assertEqual(
            self.bibfield_json['free_keyword'],
            self.record['free_keywords']
        )

    def test_language(self):
        """Test if language is created correctly"""
        self.assertEqual(
            self.bibfield_json['language'],
            self.record['language']
        )

    def test_titles_old(self):
        """Test if titles_old is created correctly"""
        self.assertEqual(
            self.bibfield_json['title_old']['main'],
            self.record['titles_old'][0]['title']
        )
        self.assertEqual(
            self.bibfield_json['title_old']['subtitle'],
            self.record['titles_old'][0]['subtitle']
        )

    def test_thesaurus_terms(self):
        """Test if thesaurus_terms is created correctly"""
        self.assertEqual(
            self.bibfield_json['thesaurus_terms'][0]['keyword'],
            self.record['thesaurus_terms'][0]['keyword']
        )
        self.assertEqual(
            self.bibfield_json['thesaurus_terms'][0]['classification_scheme'],
            self.record['thesaurus_terms'][0]['scheme']
        )

    def test_thesis_supervisor(self):
        """Test if thesis_supervisor is created correctly"""
        self.assertEqual(
            self.bibfield_json['thesis_supervisor']['full_name'],
            self.record['thesis_supervisor'][0]['full_name']
        )
        self.assertEqual(
            self.bibfield_json['thesis_supervisor']['affiliation'],
            self.record['thesis_supervisor'][0]['affiliation']['value']
        )

    def test_spires_sysnos(self):
        """Test if spires_sysnos is created correctly"""
        self.assertEqual(
            self.bibfield_json['spires_sysno']['value'],
            self.record['spires_sysnos'][0]
        )

    def test_title_translation(self):
        """Test if title_translation is created correctly"""
        self.assertEqual(
            self.bibfield_json['title_translation']['value'],
            self.record['title_translation'][0]['title']
        )
        self.assertEqual(
            self.bibfield_json['title_translation']['subtitle'],
            self.record['title_translation'][0]['subtitle']
        )

    def test_copyright(self):
        """Test if copyright is created correctly"""
        self.assertEqual(
            self.bibfield_json['coyright'],
            self.record['copyright']
        )

    def test_accelerator_experiments(self):
        """Test if caccelerator_experiments is created correctly"""
        self.assertEqual(
            self.bibfield_json['accelerator_experiment'],
            self.record['accelerator_experiments'][0]
        )

    def test_arxiv_eprints_and_system_numbers(self):
        """Test if arxiv_eprints is created correctly"""
        self.assertEqual(
            self.bibfield_json['system_number_external']['value'],
            self.record['arxiv_eprints'][0]['value']
        )

        self.assertEqual(
            self.bibfield_json['system_number_external']['value'],
            self.record['external_system_numbers'][0]['value']
        )

    def test_title(self):
        """Test if title is created correctly"""
        self.assertEqual(
            self.bibfield_json['title']['title'],
            self.record['titles'][0]['title']
        )
        self.assertEqual(
            self.bibfield_json['title']['subtitle'],
            self.record['titles'][0]['subtitle']
        )
        self.assertEqual(
            self.bibfield_json['title']['source'],
            self.record['titles'][0]['source']
        )

    def test_authors(self):
        """Test if authors is created correctly"""
        self.assertEqual(
            self.bibfield_json['authors'][0]['full_name'],
            self.record['authors'][0]['full_name']
        )
        self.assertEqual(
            self.bibfield_json['authors'][0]['affiliation'],
            self.record['authors'][0]['affiliations'][0]['value']
        )
        self.assertEqual(
            self.bibfield_json['authors'][1]['relator_term'],
            self.record['authors'][1]['role']
        )
        self.assertEqual(
            self.bibfield_json['authors'][1]['INSPIRE_id'],
            self.record['authors'][1]['inspire_id']
        )
        self.assertEqual(len(self.bibfield_json['authors']),
                         len(self.record['authors']))


TEST_SUITE = make_test_suite(BibFieldToJSONTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
