# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Tests for the datefilter utility functions."""

from datetime import datetime

from invenio_testing import InvenioTestCase


class DateTests(InvenioTestCase):

    """Test the datefilter utility functions."""

    def test_date_older_than_older_date(self):
        """date_older_than recognizes older dates."""
        from inspirehep.utils.datefilter import date_older_than

        parsed_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        other_parsed_date = datetime.strptime("2015-01-04", "%Y-%m-%d")

        self.assertTrue(date_older_than(parsed_date, other_parsed_date, days=2))

    def test_date_older_than_newer_date(self):
        """date_older_than recognizes newer dates."""
        from inspirehep.utils.datefilter import date_older_than

        parsed_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        other_parsed_date = datetime.strptime("2015-01-04", "%Y-%m-%d")

        self.assertFalse(date_older_than(parsed_date, other_parsed_date, days=6))
