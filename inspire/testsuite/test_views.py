# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

"""Tests for views"""

from invenio.testsuite import InvenioTestCase


class ViewsTests(InvenioTestCase):
    """Tests views."""

    def test_detailed_records(self):
        """Test visiting each detailed record returns 200"""
        from invenio_records.models import Record
        failing_recids = []
        for recid in Record.allids():
            try:
                if self.client.get("/record/{recid}".format(recid=recid)).status_code != 200:
                    failing_recids.append(recid)
            except Exception:
                failing_recids.append(recid)
        self.failIf(failing_recids)
