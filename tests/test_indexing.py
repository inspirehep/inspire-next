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

"""Tests indexing of records."""

import time

from invenio.testsuite import InvenioTestCase


NUM_HEP_DEMO_RECORDS = 426
NUM_DEMO_RECORDS = 427


class IndexingTests(InvenioTestCase):

    def test_reindexing(self):
        """Test that all records are indexed"""
        from invenio_search.api import Query
        # Note that the number might change if new demo records are
        # introduced.
        self.assertEqual(len(Query("").search()), NUM_DEMO_RECORDS)

    def test_recids(self):
        """Test that recids API works"""
        from invenio_search.api import Query
        # Note that the number might change if new demo records are
        # introduced.
        self.assertEqual(len(Query("").search().recids), NUM_DEMO_RECORDS)

    def test_recids_collection(self):
        """Test that recids API works"""
        from invenio_search.api import Query
        # Note that the number might change if new demo records are
        # introduced.
        self.assertEqual(len(Query("").search(collection='HEP').recids), NUM_HEP_DEMO_RECORDS)

    def test_recids_restricted_collection(self):
        """Test that recids API works"""
        from invenio_ext.sqlalchemy import db
        from invenio_search.api import Query
        from invenio_records.api import Record

        # FIXME All of this needs rewrite on Invenio 3.

        self.assertEqual(len(Query("").search(collection='CDF Internal Notes').recids), 0)

        # Adds special user info to allow test user to search in restricted collections
        self.assertEqual(len(Query("").search(
            collection='CDF Internal Notes',
            user_info={'precached_permitted_restricted_collections': ['CDF Internal Notes']}
        ).recids), 1)

        test_recid = 1396160
        original_record = dict(Record.get_record(test_recid))

        try:
            rec = Record.get_record(test_recid)
            rec['collections'].append({'primary': 'CDF-INTERNAL-NOTE'})
            rec.commit()

            # Wait for indexing
            time.sleep(10)

            self.assertEqual(len(Query("").search(
                collection='CDF Internal Notes',
                user_info={'precached_permitted_restricted_collections': ['CDF Internal Notes']}
            ).recids), 2)
        finally:
            rec = Record.get_record(test_recid)
            rec.model.json = original_record
            db.session.commit()
