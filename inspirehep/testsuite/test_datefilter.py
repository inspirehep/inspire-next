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

"""Tests for text utls."""

from __future__ import print_function, absolute_import

from datetime import datetime

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class DateTests(InvenioTestCase):

    """Test the datefilter functions."""

    def test_older_date(self):
        """Test proper handling when bad MARCXML is sent."""
        from inspirehep.utils.datefilter import date_older_than
        parsed_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        other_parsed_date = datetime.strptime("2015-01-04", "%Y-%m-%d")

        self.assertTrue(date_older_than(parsed_date, other_parsed_date, days=2))

    def test_newer_date(self):
        """Test proper handling when bad MARCXML is sent."""
        from inspirehep.utils.datefilter import date_older_than
        parsed_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        other_parsed_date = datetime.strptime("2015-01-04", "%Y-%m-%d")

        self.assertFalse(date_older_than(parsed_date, other_parsed_date, days=6))

TEST_SUITE = make_test_suite(DateTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
