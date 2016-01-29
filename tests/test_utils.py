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

"""Tests for utilities."""

from __future__ import print_function, absolute_import

from werkzeug.datastructures import CombinedMultiDict, ImmutableMultiDict

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class UtilsTests(InvenioTestCase):

    """Test the utility functions."""

    def test_wash_urlargd(self):
        """
        Test invenio_utils wash_urlargd function.

        It should deal properly with boolean values.
        """
        from invenio_utils.washers import wash_urlargd
        form = CombinedMultiDict(
            [ImmutableMultiDict([('approved', u'False'), ('objectid', u'85')]),
                ImmutableMultiDict([])]
        )
        content = {
            'ticket': (bool, False),
            'approved': (bool, False),
            'objectid': (int, 0)
        }
        expected_dict = {'approved': False, 'objectid': 85, 'ticket': False}
        self.assertEqual(wash_urlargd(form, content), expected_dict)


TEST_SUITE = make_test_suite(UtilsTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
