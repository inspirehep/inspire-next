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

import pkg_resources
import os

from dojson.contrib.marc21.utils import create_record

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite
from inspirehep.dojson.hepnames import hepnames2marc, hepnames


class HepNamesRecordsTests(InvenioTestCase):

    def setUp(self):
        self.marcxml = pkg_resources.resource_string('tests',
                                                     os.path.join(
                                                         'fixtures',
                                                         'test_hepnames_record.xml')
                                                     )
        record = create_record(self.marcxml)
        self.marcxml_to_json = hepnames.do(record)
        self.json_to_marc = hepnames2marc.do(self.marcxml_to_json)

    def test_acquisition_source(self):
        """Test if acquisition_source is created correctly."""
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['source'],
                         self.json_to_marc['541'][0]['a'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['email'],
                         self.json_to_marc['541'][0]['b'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['method'],
                         self.json_to_marc['541'][0]['c'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['date'],
                         self.json_to_marc['541'][0]['d'])
        self.assertEqual(self.marcxml_to_json['acquisition_source'][0]['submission_number'],
                         self.json_to_marc['541'][0]['e'])

    def test_dates(self):
        """Test if dates is created correctly."""
        #TODO fix dojson to take dates from 100__d
        pass

    def test_experiments(self):
        """Test if experiments is created correctly."""
        self.assertEqual(self.marcxml_to_json['experiments'][1]['name'],
                         self.json_to_marc['693'][1]['e'])
        self.assertEqual(self.marcxml_to_json['experiments'][1]['start_year'],
                         self.json_to_marc['693'][1]['s'])
        self.assertEqual(self.marcxml_to_json['experiments'][1]['end_year'],
                         self.json_to_marc['693'][1]['d'])
        self.assertEqual(self.marcxml_to_json['experiments'][1]['status'],
                         self.json_to_marc['693'][1]['z'])

    def test_field_categories(self):
        """Test if field_categories is created correctly."""
        self.assertEqual(self.marcxml_to_json['field_categories'][0],
                         self.json_to_marc['65017'][0]['a'])
        self.assertEqual(self.marcxml_to_json['field_categories'][1],
                         self.json_to_marc['65017'][1]['a'])
        self.assertEqual(self.json_to_marc['65017'][1]['2'], 'INSPIRE')

    def test_ids(self):
        """Test if ids is created correctly."""
        self.assertEqual(self.marcxml_to_json['ids'][0]['value'],
                         self.json_to_marc['035'][0]['a'])
        self.assertEqual(self.marcxml_to_json['ids'][0]['type'],
                         self.json_to_marc['035'][0]['9'])
        self.assertEqual(self.marcxml_to_json['ids'][1]['value'],
                         self.json_to_marc['035'][1]['a'])
        self.assertEqual(self.marcxml_to_json['ids'][1]['type'],
                         self.json_to_marc['035'][1]['9'])

    def test_name(self):
        """Test if name is created correctly."""
        self.assertEqual(self.marcxml_to_json['name']['value'],
                         self.json_to_marc['100']['a'])
        self.assertEqual(self.marcxml_to_json['name']['numeration'],
                         self.json_to_marc['100']['b'])
        self.assertEqual(self.marcxml_to_json['name']['title'],
                         self.json_to_marc['100']['c'])
        self.assertEqual(self.marcxml_to_json['name']['status'],
                         self.json_to_marc['100']['g'])
        self.assertEqual(self.marcxml_to_json['name']['preferred_name'],
                         self.json_to_marc['100']['q'])

    def test_native_name(self):
        """Test if native_name is created correctly."""
        self.assertEqual(self.marcxml_to_json['native_name'],
                         self.json_to_marc['880']['a'])

    def test_other_names(self):
        """Test if other_names is created correctly."""
        self.assertEqual(self.marcxml_to_json['other_names'][0],
                         self.json_to_marc['400'][0]['a'])
        self.assertEqual(self.marcxml_to_json['other_names'][1],
                         self.json_to_marc['400'][1]['a'])

    def test_phd_advisors(self):
        """Test if phd_advisors is created correctly."""
        self.assertEqual(self.marcxml_to_json['phd_advisors'][0]['id'],
                         self.json_to_marc['701'][0]['i'])
        self.assertEqual(self.marcxml_to_json['phd_advisors'][0]['name'],
                         self.json_to_marc['701'][0]['a'])
        self.assertEqual(self.marcxml_to_json['phd_advisors'][0]['degree_type'],
                         self.json_to_marc['701'][0]['g'])

    def test_positions(self):
        """Test if positions is created correctly."""
        self.assertEqual(self.marcxml_to_json['positions'][0]['institution']['name'],
                         self.json_to_marc['371'][0]['a'])
        self.assertEqual(self.marcxml_to_json['positions'][0]['rank'],
                         self.json_to_marc['371'][0]['r'])
        self.assertEqual(self.marcxml_to_json['positions'][0]['start_date'],
                         self.json_to_marc['371'][0]['s'])
        self.assertEqual(self.marcxml_to_json['positions'][0]['email'],
                         self.json_to_marc['371'][0]['m'])
        self.assertEqual(self.marcxml_to_json['positions'][0]['status'],
                         self.json_to_marc['371'][0]['z'])
        self.assertEqual(self.marcxml_to_json['positions'][1]['end_date'],
                         self.json_to_marc['371'][1]['t'])
        self.assertEqual(self.marcxml_to_json['positions'][2]['old_email'],
                         self.json_to_marc['371'][2]['o'])

    def test_private_current_emails(self):
        """Test if private_current_emails is created correctly."""
        self.assertEqual(self.marcxml_to_json['private_current_emails'][0],
                         self.json_to_marc['595'][1]['m'])

    def test_private_old_emails(self):
        """Test if private_old_emails is created correctly."""
        self.assertEqual(self.marcxml_to_json['private_old_emails'][0],
                         self.json_to_marc['595'][0]['o'])

    def test_private_notes(self):
        """Test if private_notes is created correctly."""
        self.assertEqual(self.marcxml_to_json['_private_note'][0],
                         self.json_to_marc['595'][2]['a'])

    def test_prizes(self):
        """Test if prizes is created correctly."""
        self.assertEqual(self.marcxml_to_json['prizes'][0],
                         self.json_to_marc['678'][0]['a'])

    def test_source(self):
        """Test if source is created correctly."""
        self.assertEqual(self.marcxml_to_json['source'][0]['name'],
                         self.json_to_marc['670'][0]['a'])
        self.assertEqual(self.marcxml_to_json['source'][1]['date_verified'],
                         self.json_to_marc['670'][1]['d'])

    def test_urls(self):
        """Test if urls is created correctly."""
        self.assertEqual(self.marcxml_to_json['urls'][0]['value'],
                         self.json_to_marc['8564'][0]['u'])
        self.assertEqual(self.marcxml_to_json['urls'][0]['description'],
                         self.json_to_marc['8564'][0]['y'])

TEST_SUITE = make_test_suite(HepNamesRecordsTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
