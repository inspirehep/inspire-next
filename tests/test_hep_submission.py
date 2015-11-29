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

"""Tests for HEP submission form to doJSON conversion."""

import copy
import json
import os

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

import pkg_resources


class HEPFormToJSONTests(InvenioTestCase):

    def setUp(self):
        from invenio_accounts.models import UserEXT
        from mock import MagicMock

        from inspirehep.modules.deposit.workflows.literature import literature

        UserEXT.query.delete()
        u = UserEXT(
            id="0000-0000-0000",
            method="orcid",
            id_user=1
        )

        self.create_objects([u])
        self.u = u

        self.hepform_json = json.loads(
            pkg_resources.resource_string(
                'tests',
                os.path.join(
                    'fixtures',
                    'hep_submission_form.json'
                )
            )
        )
        self.record = self.hepform_json
        self.hepform_json = copy.deepcopy(self.hepform_json)
        deposition = MagicMock(id=1, user_id=1)
        literature.process_sip_metadata(deposition,
                                        self.record)

    def test_extra_comments(self):
        """Test if extra comments are created correctly."""
        self.assertEqual(
            self.hepform_json['extra_comments'],
            self.record['hidden_notes'][2]['value']
        )
        self.assertEqual(
            self.record['hidden_notes'][2]['source'],
            'submitter'
        )

    def test_conference_name(self):
        """Test if conference info is created correctly."""
        self.assertEqual(
            self.hepform_json['conf_name'],
            self.record['hidden_notes'][0]['value']
        )

    def test_title_arXiv(self):
        """Test if title arXiv is created correctly."""
        self.assertEqual(
            self.hepform_json['title_arXiv'],
            self.record['titles'][1]['title']
        )
        self.assertEqual(
            self.record['titles'][1]['source'],
            'arXiv'
        )

    def test_title(self):
        """Test if title arXiv is created correctly."""
        self.assertEqual(
            self.hepform_json['title'],
            self.record['titles'][0]['title']
        )
        self.assertEqual(
            self.record['titles'][0]['source'],
            'CrossRef'
        )

    def test_arxivid(self):
        """Test if arXiv ID is created correctly."""
        self.assertEqual(
            'arXiv:' + self.hepform_json['arxiv_id'],
            self.record['arxiv_eprints'][0]['value']
        )

    def test_references(self):
        """Test if references are created correctly."""
        self.assertEqual(
            self.hepform_json['references'],
            self.record['references']
        )

    def test_publication_info(self):
        """Test if publication info is created correctly."""
        self.assertEqual(
            self.hepform_json['page_range_article_id'],
            self.record['publication_info'][0]['page_artid']
        )
        self.assertEqual(
            self.hepform_json['journal_title'],
            self.record['publication_info'][0]['journal_title']
        )
        self.assertEqual(
            self.hepform_json['conference_id'],
            self.record['publication_info'][0]['cnum']
        )
        self.assertEqual(
            self.hepform_json['volume'],
            self.record['publication_info'][0]['journal_volume']
        )
        self.assertEqual(
            self.hepform_json['year'],
            self.record['publication_info'][0]['year']
        )
        self.assertEqual(
            self.hepform_json['issue'],
            self.record['publication_info'][0]['journal_issue']
        )

    def test_abstract(self):
        """Test if abstract is created correctly."""
        self.assertEqual(
            self.hepform_json['abstract'],
            self.record['abstracts'][0]['value']
        )

    def test_experiment(self):
        """Test if abstract is created correctly."""
        self.assertEqual(
            self.hepform_json['experiment'],
            self.record['accelerator_experiments'][0]['experiment']
        )

    def test_preprint_created(self):
        """Test if preprint date created correctly."""
        self.assertEqual(
            self.hepform_json['preprint_created'],
            self.record['imprints'][0]['date']
        )

    def test_collaboration(self):
        """Test if collaboration is created correctly."""
        self.assertEqual(
            self.hepform_json['collaboration'],
            self.record['collaboration']
        )

    def test_user_subjects(self):
        """Test if user subjects are created correctly."""
        user_subjects = [subject for subject in
                         self.record['subject_terms']
                         if subject['scheme'] == 'INSPIRE']
        self.assertEqual(
            self.hepform_json['subject_term'][0],
            user_subjects[0]['term']
        )
        self.assertEqual(
            'submitter',
            user_subjects[0]['source']
        )
        self.assertEqual(
            'INSPIRE',
            user_subjects[0]['scheme']
        )

    def test_url(self):
        """Test if url is created correctly."""
        self.assertEqual(
            self.hepform_json['url'],
            self.record['urls'][1]['url']
        )

    def test_additional_url(self):
        """Test if additional url is created correctly."""
        self.assertEqual(
            self.hepform_json['additional_url'],
            self.record['urls'][0]['url']
        )

    def test_authors(self):
        """Test if authors are created correctly."""
        self.assertEqual(
            self.hepform_json['authors'][0]['full_name'],
            self.record['authors'][0]['full_name']
        )
        self.assertEqual(
            self.hepform_json['authors'][1]['full_name'],
            self.record['authors'][1]['full_name']
        )
        self.assertEqual(
            self.hepform_json['authors'][0]['affiliation'],
            self.record['authors'][0]['affiliations'][0]['value']
        )
        self.assertEqual(
            self.hepform_json['authors'][1]['affiliation'],
            self.record['authors'][1]['affiliations'][0]['value']
        )

    def test_arXiv_categories(self):
        """Test if arXiv categories are created correctly."""
        form_categories = self.hepform_json['categories'].split()
        record_categories = [category['term'] for category in
                             self.record['subject_terms']
                             if category['scheme'] == 'arXiv']
        self.assertEqual(
            form_categories,
            record_categories
        )

    def test_doi(self):
        """Test if arXiv categories are created correctly."""
        self.assertEqual(
            self.hepform_json['doi'],
            self.record['dois'][0]['value']
        )

    def test_languages(self):
        """Test if languages is created correctly."""
        self.assertEqual(
            self.hepform_json['other_language'],
            self.record['languages'][0]
        )

    def test_report_numbers(self):
        """Test if language is created correctly."""
        self.assertEqual(
            self.hepform_json['report_numbers'][0]['report_number'],
            self.record['report_numbers'][0]['value'],
        )

        self.assertEqual(
            self.hepform_json['report_numbers'][1]['report_number'],
            self.record['report_numbers'][1]['value'],
        )

    def test_license_url(self):
        """Test if license is created correctly."""
        self.assertEqual(
            self.hepform_json['license_url'],
            self.record['license']['url'],
        )

    def test_title_translation(self):
        """Test if title_translation is created correctly."""
        self.assertEqual(
            self.hepform_json['title_translation'],
            self.record['title_translation'][0]['title']
        )

    def test_thesis(self):
        """Test if thesis is created correctly."""
        self.assertEqual(
            self.hepform_json['institution'],
            self.record['thesis']['university']
        )
        self.assertEqual(
            self.hepform_json['thesis_date'],
            self.record['thesis']['date']
        )
        self.assertEqual(
            self.hepform_json['defense_date'],
            self.record['thesis']['defense_date']
        )

        self.assertEqual(
            self.hepform_json['degree_type'],
            self.record['thesis']['degree_type']
        )

    def test_proceedings(self):
        """Test if proceedings are created correctly."""
        self.assertEqual(
            self.hepform_json['nonpublic_note'],
            self.record['hidden_notes'][1]['value']
        )

    def test_arXiv_comments(self):
        """Test if arXiv comments are created correctly."""
        self.assertEqual(
            self.hepform_json['note'],
            self.record['public_notes'][0]['value']
        )

    def test_acquisition_source(self):
        """Test if acquisition source is created correctly."""
        self.assertEqual(
            self.record['acquisition_source'],
            {
                "source": "orcid:0000-0000-0000",
                "method": "submission",
                "email": "info@invenio-software.org",
                "submission_number": 1
            }
        )

    def test_collections(self):
        """Test if collections are created correctly."""
        collections = [collection['primary']
                       for collection in self.record['collections']]
        self.assertEqual(
            collections,
            ['HEP', 'arXiv', 'Citeable', 'Published', 'ConferencePaper']
        )

    def test_external_system_number(self):
        """Test if external system number is created correctly."""
        self.assertEqual(
            self.record['external_system_numbers'][0],
            {
                "institute": "arXiv",
                "value": "oai:arXiv.org:1510.04400"
            }
        )

    def test_page_nr(self):
        """Test if page number is created correctly."""
        self.assertEqual(
            self.record['page_nr'],
            5
        )

    def tearDown(self):
        self.delete_objects([self.u])


TEST_SUITE = make_test_suite(HEPFormToJSONTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
