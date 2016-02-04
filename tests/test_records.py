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

    def setUp(self):
        from invenio_records.api import Record
        self.test_recid = 1402176
        self.original_record = dict(Record.get_record(self.test_recid))

    def tearDown(self):
        from invenio_ext.sqlalchemy import db
        from invenio_records.api import Record

        rec = Record.get_record(self.test_recid)
        rec.model.json = self.original_record
        db.session.commit()

    def test_update_record(self):
        """Test updating record."""
        from invenio_ext.sqlalchemy import db
        from invenio_records.api import Record

        rec = Record.get_record(self.test_recid)
        assert rec["languages"] == ["Croatian"]

        # 1. Need to make a new clean dict and update it
        new_dict = dict(rec)
        new_dict["languages"] = ["Norwegian"]

        # 2. Create new instance with updated dict, but same model (recid etc.)
        rec = Record(new_dict, model=rec.model)
        rec.commit()
        db.session.commit()

        rec = Record.get_record(self.test_recid)
        assert rec["languages"] == ["Norwegian"]

    def test_doted_author_search(self):
        from invenio_search.api import Query
        query_1_results = Query('find a storaci b').search().recids
        query_2_results = Query('find a storaci b.').search().recids
        self.assertEqual(query_1_results, query_2_results)

    def test_update_record_again(self):
        """Test updating record again to make sure tearDown does the right thing."""
        self.test_update_record()
