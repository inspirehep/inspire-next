# -*- coding: utf-8 -*-
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

"""Tests for helper functions used in the author records."""

from ..recordext.functions.sum_emails import sum_emails
from ..recordext.functions.sum_notes import sum_notes
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class AuthorRecordFunctionsTestSumNotes(InvenioTestCase):

    def test_sum_notes_empty(self):
        record = {}
        result = sum_notes(record, 'pu', 'pr', 'cu')
        self.assertEqual(result, {})

    def test_sum_notes_public(self):
        record = {'pu': 'Note'}
        result = sum_notes(record, 'pu', 'pr', 'cu')
        self.assertIn('public', result)
        self.assertEqual(result['public'], 'Note')
        self.assertNotIn('private', result)
        self.assertNotIn('curators', result)


class AuthorRecordFunctionsTestSumEmails(InvenioTestCase):

    def test_sum_emails_empty(self):
        record = {}
        result = sum_emails(record, 'pu', 'pr', 'ol')
        self.assertEqual(result, [])

    def test_sum_emails_public(self):
        record = {'pu': [{'value': 'mail@mail.com', 'current': 'current'}]}
        result = sum_emails(record, 'pu', 'pr', 'ol')
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]['private'])

    def test_sum_emails_private_current(self):
        record = {'pr': [{'value': 'mail@mail.com'}]}
        result = sum_emails(record, 'pu', 'pr', 'ol')
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['private'])
        self.assertEqual(result[0]['current'], 'current')

    def test_sum_emails_private_old(self):
        record = {'ol': [{'value': 'mail@mail.com'}]}
        result = sum_emails(record, 'pu', 'pr', 'ol')
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['private'])
        self.assertNotIn('current', result[0])


TEST_SUITE = make_test_suite(AuthorRecordFunctionsTestSumNotes,
                             AuthorRecordFunctionsTestSumEmails)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
