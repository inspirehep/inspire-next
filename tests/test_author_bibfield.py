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


import json
import os

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

import pkg_resources


class AuthorBibFieldToJSONTests(InvenioTestCase):

    def setUp(self):
        from inspirehep.modules.workflows.dojson import author_bibfield

        self.bibfield_json = json.loads(
            pkg_resources.resource_string(
                'tests',
                os.path.join(
                    'fixtures',
                    'test_author_bibfield.json'
                )
            )
        )
        self.record = author_bibfield.do(self.bibfield_json)

    def test_status(self):
        self.assertEqual(
            self.bibfield_json['status'],
            self.record['status']
        )

    def test_phd_advisors(self):
        self.assertEqual(
            self.bibfield_json['phd_advisors'][0]['degree_type'],
            self.record['phd_advisors'][0]['degree_type']
        )

    def test_name(self):
        self.assertEqual(
            self.bibfield_json['name']['last'] + ', ' +
            self.bibfield_json['name']['first'],
            self.record['name']['value']
        )
        self.assertEqual(
            self.bibfield_json['name']['status'],
            self.record['name']['status']
        )
        self.assertEqual(
            self.bibfield_json['name']['preferred_name'],
            self.record['name']['preferred_name']
        )

    def test_native_name(self):
        self.assertEqual(
            self.bibfield_json['native_name'],
            self.record['native_name']
        )

    def test_positions(self):
        self.assertEqual(
            self.bibfield_json['positions'][0]['institution'],
            self.record['positions'][0]['institution']['name']
        )
        self.assertEqual(
            self.bibfield_json['positions'][0]['rank'],
            self.record['positions'][0]['rank']
        )
        self.assertEqual(
            self.bibfield_json['positions'][0]['start_date'],
            self.record['positions'][0]['start_date']
        )
        self.assertEqual(
            self.bibfield_json['positions'][0]['end_date'],
            self.record['positions'][0]['end_date']
        )
        self.assertEqual(
            self.bibfield_json['positions'][0]['status'],
            self.record['positions'][0]['status']
        )

    def test_experiments(self):
        self.assertEqual(
            self.bibfield_json['experiments'][0]['status'],
            self.record['experiments'][0]['status']
        )
        self.assertEqual(
            self.bibfield_json['experiments'][0]['start_year'],
            self.record['experiments'][0]['start_year']
        )
        self.assertEqual(
            self.bibfield_json['experiments'][0]['end_year'],
            self.record['experiments'][0]['end_year']
        )
        self.assertEqual(
            self.bibfield_json['experiments'][0]['name'],
            self.record['experiments'][0]['name']
        )


    def test_acquisition_source(self):
        self.assertEqual(
            self.bibfield_json['acquisition_source']['date'],
            self.record['acquisition_source']['date']
        )
        self.assertEqual(
            self.bibfield_json['acquisition_source']['method'],
            self.record['acquisition_source']['method']
        )
        self.assertEqual(
            self.bibfield_json['acquisition_source']['email'],
            self.record['acquisition_source']['email']
        )
        self.assertEqual(
            self.bibfield_json['acquisition_source']['submission_number'],
            self.record['acquisition_source']['submission_number']
        )
        self.assertEqual(
            self.bibfield_json['acquisition_source']['source'][0],
            self.record['acquisition_source']['source']
        )

    def test_ids(self):
        self.assertEqual(
            self.bibfield_json['ids'][0]['type'],
            self.record['ids'][0]['type']
        )
        self.assertEqual(
            self.bibfield_json['ids'][0]['value'],
            self.record['ids'][0]['value']
        )

    def test_field_categories(self):
        self.assertEqual(
            self.bibfield_json['field_categories'][0]['name'],
            self.record['field_categories'][0]
        )

    def test_urls(self):
        self.assertEqual(
            self.bibfield_json['urls'][0]['value'],
            self.record['urls'][0]['value']
        )
        self.assertEqual(
            self.bibfield_json['urls'][0]['description'],
            self.record['urls'][0]['description']
        )

    def test_collections(self):
        self.assertEqual(
            self.bibfield_json['collections']['primary'],
            self.record['collections'][0]['primary']
        )
        self.assertEqual(
            self.bibfield_json['urls'][0]['description'],
            self.record['urls'][0]['description']
        )


TEST_SUITE = make_test_suite(AuthorBibFieldToJSONTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
