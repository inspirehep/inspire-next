# -*- coding: utf-8 -*-
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for author records."""

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class AuthorRecordTestCase(InvenioTestCase):

    """Base class for author_base records test."""

    def setUp(self):
        """Preparing evironment for tests."""
        self.import_context()

    def import_context(self):
        """Import the Invenio classes here.

        Makes sure the testing context is valid.
        """
        from invenio_records.api import Record
        self.Record = Record

    def create_record_from_json(self, json_dict):
        """Return record created from json dictionary.

        :param json_dict: The dictionary in JSON from with author content
        :return: an author base record
        """
        return self.Record.create(json_dict, 'json', model='author')

    def create_record_from_marc(self, xml_string):
        """Return record created from MARCxml string.

        :param xml_string: The string representing MARCxml of an author
        :return: an author base record
        """
        return self.Record.create(xml_string, 'marc', model='author')


class AuthorRecordRequiredFieldsTestCase(AuthorRecordTestCase):

    """Tests for required fields from author_base records."""

    def test_marc_correct_date_split(self):
        """Here the date split should produce two yearly integers."""
        xml_string = '''<collection><record>
            <datafield tag="035" ind1="" ind2="">
            <subfield code="9">authorid</subfield>
            <subfield code="a">0000-0002-0003-2345</subfield></datafield>
            <datafield tag="900" ind1="" ind2="">
            <subfield code="a">9</subfield></datafield>
            <datafield tag="100" ind1="" ind2="">
            <subfield code="a">van der Nvenio, I.</subfield>
            <subfield code="d">1962-1999</subfield></datafield>
            </record></collection>'''

        record = self.create_record_from_marc(xml_string)

        self.assertEqual(record['dates']['birth'], 1962)
        self.assertEqual(record['dates']['death'], 1999)

        validation = record.validate()
        self.assertEqual(validation, {})

    def test_marc_first_date_available(self):
        """Here the date split should produce one yearly integer."""
        xml_string = '''<collection><record>
            <datafield tag="035" ind1="" ind2="">
            <subfield code="9">authorid</subfield>
            <subfield code="a">0000-0002-0003-2345</subfield></datafield>
            <datafield tag="900" ind1="" ind2="">
            <subfield code="a">9</subfield></datafield>
            <datafield tag="100" ind1="" ind2="">
            <subfield code="a">van der Nvenio, I.</subfield>
            <subfield code="d">1992-</subfield></datafield>
            </record></collection>'''

        record = self.create_record_from_marc(xml_string)

        self.assertEqual(record['dates']['birth'], 1992)
        self.assertIsNone(record['dates']['death'])

        validation = record.validate()
        self.assertEqual(validation, {})

    def test_marc_second_date_available(self):
        """It is possible to set only the date of death.

        It can be done by including a hyphen before the year in MARC.
        """
        xml_string = '''<collection><record>
            <datafield tag="035" ind1="" ind2="">
            <subfield code="9">authorid</subfield>
            <subfield code="a">0000-0002-0003-2345</subfield></datafield>
            <datafield tag="900" ind1="" ind2="">
            <subfield code="a">9</subfield>
            </datafield><datafield tag="100" ind1="" ind2="">
            <subfield code="a">van der Nvenio, I.</subfield>
            <subfield code="d">-1992</subfield></datafield>
            </record></collection>'''

        record = self.create_record_from_marc(xml_string)

        self.assertIsNone(record['dates']['birth'])
        self.assertEqual(record['dates']['death'], 1992)

        validation = record.validate()
        self.assertEqual(validation, {})

    def test_marc_date_silent_fall(self):
        """Fall silently if the dates provided are in wrong format."""
        xml_string = '''<collection><record>
            <datafield tag="035" ind1="" ind2="">
            <subfield code="9">authorid</subfield>
            <subfield code="a">0000-0002-0003-2345</subfield></datafield>
            <datafield tag="900" ind1="" ind2="">
            <subfield code="a">9</subfield></datafield>
            <datafield tag="100" ind1="" ind2="">
            <subfield code="a">van der Nvenio, I.</subfield>
            <subfield code="d">I like trains</subfield></datafield>
            </record></collection>'''

        record = self.create_record_from_marc(xml_string)

        self.assertIsNone(record['dates']['birth'])
        self.assertIsNone(record['dates']['death'])

        validation = record.validate()
        self.assertEqual(validation, {})

    def test_inspire_identificators_types(self):
        """Allow for ids from ORCID."""
        json = {'ids': [{'type': 'orcid', 'value': '15783'},
                {'type': 'authorid', 'value': 'somename'}],
                'name': {'first': 'I.', 'last': 'Nvenio'},
                'publications_list': [9]}

        record = self.create_record_from_json(json)

        validation = record.validate()
        self.assertEqual(validation, {})

    def test_inspire_wrong_identification_type(self):
        """Don't allow unknown id types."""
        json = {'ids': [{'type': 'sern', 'value': '15783'},
                {'type': 'authorid', 'value': 'somename'}],
                'name': {'first': 'I.', 'last': 'Nvenio'},
                'publications_list': [9]}

        record = self.create_record_from_json(json)

        validation = record.validate()
        self.assertTrue('type' in validation)


class AuthorRecordOptionalFieldsTestCase(AuthorRecordTestCase):

    """Tests for optional fields from author_base records."""

    def test_optionality_of_fields(self):
        """Some fields should not appear in the record.

        It should happen when they were not provided in the input.
        """
        json = {'ids': [{'type': 'authorid', 'value': '15783'},
                {'type': 'authorid', 'value': 'somename'}],
                'name': {'first': 'I.', 'last': 'Nvenio'},
                'publications_list': [9]}

        record = self.create_record_from_json(json)

        keys = list(record.keys())
        # Optional fields
        self.assertFalse('emails' in keys)
        self.assertFalse('other_names' in keys)
        self.assertFalse('positions' in keys)
        self.assertFalse('field_categories' in keys)
        self.assertFalse('curators_note' in keys)
        self.assertFalse('prizes' in keys)
        self.assertFalse('experiments' in keys)
        self.assertFalse('phd_advisors' in keys)
        self.assertFalse('conferences' in keys)
        self.assertFalse('urls' in keys)
        self.assertFalse('native_name' in keys)
        self.assertFalse('date_added' in keys)
        self.assertFalse('date_updated' in keys)

        # This is a side effect of JSONAlchemy.
        # Test it, so when behaviour changes sb is forced to check it.
        self.assertTrue('dates' in keys)
        self.assertTrue('source' in keys)

        # Required fields
        self.assertTrue('name' in keys)
        self.assertTrue('ids' in keys)
        self.assertTrue('publications_list' in keys)

    def test_no_string_in_url_field(self):
        """The value in the urls subfield has to be provided.

        An url containing only description is invalid.
        """
        json = {'ids': [{'type': 'authorid', 'value': '15783'},
                {'type': 'authorid', 'value': 'somename'}],
                'name': {'first': 'I.', 'last': 'Nvenio'},
                'publications_list': [9],
                'urls': [{'description': 'twitter'}]}

        record = self.create_record_from_json(json)

        validation = record.validate()
        self.assertTrue('value' in validation)

    def test_wrong_date_added(self):
        """Only one date format should be accepted."""
        json = {'ids': [{'type': 'authorid', 'value': '15783'}],
                'name': {'first': 'I.', 'last': 'Nvenio'},
                'publications_list': [9],
                'date_added': '2013/12/02'}

        record = self.create_record_from_json(json)

        validation = record.validate()

        self.assertTrue('date_added' in validation)


TEST_SUITE = make_test_suite(AuthorRecordRequiredFieldsTestCase,
                             AuthorRecordOptionalFieldsTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
