# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite
from flask import current_app


class PubInfoTests(InvenioTestCase):

    def setUp(self):
        self.pub_info = current_app.jinja_env.filters['publication_info']
        self.pub_info_unique_field = {"publication_info": [{u'journal_volume': u'1503', u'journal_title': u'JCAP', u'page_artid': u'044', u'year': 2015}]
                                      }
        self.pub_info_multiple_fields = {"publication_info": [{u'journal_volume': u'1401', u'journal_title': u'JHEP', u'journal_recid': 1213103,
                                                               u'page_artid': u'163', u'year': 2014}, {u'note': u'Erratum', u'journal_recid': 1213103,
                                                                                                       u'page_artid': u'014', u'journal_title': u'JHEP', u'journal_volume': u'1501', u'year': 2015}]}
        self.pub_info_freetext_field = {u'publication_info': [
            {u'pubinfo_freetext': u'Current Science Vol. 109 (N0. 12, 25 December 2015), 2220-2229\n (2015)'}]}
        self.conf_info_first_case = {"publication_info": [{u'journal_volume': u'C050318', u'journal_title': u'eConf',
                                                           u'page_artid': u'0106', u'year': 2005},
                                                          {u'parent_recid': 706120,
                                                           u'cnum': u'C05-03-18', u'conference_recid': 976391,
                                                           u'confpaper_info': u'To appear in the proceedings of'}]}
        self.conf_info_second_case = {"publication_info": [
            {u'parent_recid': 720114, u'cnum': u'C05-08-14.1', u'confpaper_info': u'Invited talk at'}]}
        self.conf_info_second_case_with_page = {"publication_info": [
            {u'parent_recid': 1402672, u'cnum': u'C15-03-14', u'conference_recid': 1331207, u'page_artid': u'515-518'}]}
        self.conf_info_third_case = {
            "publication_info": [{u'cnum': u'C15-06-29.3', u'conference_recid': 1346335}]}

        self.pub_info_unique = {"pub_info": [u'<i>JCAP</i> 1503 (2015) 044']}
        self.pub_info_and_conf_info = u'Published in <i>eConf</i> C050318 (2005) 0106(<a href="/record/706120">Proceedings</a> of <a href="/record/976391">  2005 International Linear Collider Workshop (LCWS 2005)</a>)'
        self.pub_info_multiple = {
            'pub_info': [u'<i>JHEP</i> 1401 (2014) 163', u'<i>JHEP</i> 1501 (2015) 014']}
        self.pub_info_freetext = {'pub_info': [
            u'Current Science Vol. 109 (N0. 12, 25 December 2015), 2220-2229\n (2015)']}
        self.conf_info_conf_and_par = {
            'conf_info': u'(<a href="/record/706120">Proceedings</a> of <a href="/record/976391">  2005 International Linear Collider Workshop (LCWS 2005)</a>)'}
        self.conf_info_only_par = {
            'conf_info': u'Published in <a href="/record/720114">proceedings</a> of 2005 International Linear Collider Physics and Detector Workshop and 2nd ILC Accelerator Workshop (Snowmass 2005)'}
        self.conf_info_conf_and_par_page = {
            'conf_info': u'Published in <a href="/record/1402672">proceedings</a> of <a href="/record/1331207">50th Rencontres de Moriond on EW Interactions and Unified Theories</a>, pages    515-518'}
        self.conf_info_only_conf = {
            'conf_info': u'Contribution to <a href="/record/1346335">16th conference on Elastic and Diffractive Scattering (EDS 15)</a>'}

    def test_unique_pub_info(self):
        self.assertEqual(self.pub_info_unique['pub_info'],
                         self.pub_info(self.pub_info_unique_field)['pub_info'])

    def test_multiple_pub_info(self):
        self.assertEqual(self.pub_info_multiple['pub_info'],
                         self.pub_info(
            self.pub_info_multiple_fields)['pub_info'])

    def test_pubinfo_freetext(self):
        self.assertEqual(self.pub_info_freetext['pub_info'],
                         self.pub_info(
            self.pub_info_freetext_field)['pub_info'])

    def test_pub_info_and_conf_info(self):
        pub_info = self.pub_info(self.conf_info_first_case)['pub_info'][0]
        conf_info = self.pub_info(
            self.conf_info_first_case)['conf_info'].strip().replace('\n', '')
        self.assertEqual(
            'Published in ' + pub_info +
            conf_info, self.pub_info_and_conf_info)

    def test_conf_info_conf_and_par(self):
        self.assertEqual(self.conf_info_conf_and_par['conf_info'].strip(),
                         self.pub_info(
            self.conf_info_first_case)['conf_info'].strip().replace('\n', ''))

    def test_conf_info_only_par(self):
        self.assertEqual(self.conf_info_only_par['conf_info'].strip(),
                         self.pub_info(
            self.conf_info_second_case)['conf_info']
            .strip().replace('\n', ''))

    def test_conf_info_conf_and_par_page(self):
        self.assertEqual(self.conf_info_conf_and_par_page['conf_info'].strip(),
                         self.pub_info(
            self.conf_info_second_case_with_page)['conf_info']
            .strip().replace('\n', ''))

    def test_conf_info_only_conf(self):
        self.assertEqual(self.conf_info_only_conf['conf_info'].strip(),
                         self.pub_info(
            self.conf_info_third_case)['conf_info']
            .strip().replace('\n', ''))

TEST_SUITE = make_test_suite(PubInfoTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
