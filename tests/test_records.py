# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

"""Tests for the Records."""

from invenio_testing import InvenioTestCase


class RecordsTest(InvenioTestCase):

    """Tests for the Records."""

    def test_update_record(self):
        """Test updating record."""
        from invenio_ext.sqlalchemy import db
        from invenio_records.api import Record

        # This demo record has {"languages": ["Croatian"], ..}
        rec = Record.get_record(1402176)

        # 1. Need to make a new clean dict and update it
        new_dict = dict(rec)
        new_dict["languages"] = ["Norwegian"]

        # 2. Create new instance with updated dict, but same model (recid etc.)
        rec = Record(new_dict, model=rec.model)
        rec.commit()
        db.session.commit()

        rec = Record.get_record(1402176)
        assert rec["languages"] == ["Norwegian"]

    def test_doted_author_search(self):
        from invenio_search.api import Query
        query_1 = Query('find a storaci b').search().records()
        query_1_results = []
        for record in query_1:
            query_1_results.append(record.get("control_number"))
        query_2 = Query('find a storaci b.').search().records()
        query_2_results = []
        for record in query_2:
            query_2_results.append(record.get("control_number"))
        self.assertEqual(query_1_results, query_2_results)
