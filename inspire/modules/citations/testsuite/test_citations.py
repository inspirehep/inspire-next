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

from __future__ import absolute_import, print_function

import httpretty

from inspire.modules.citations.models import Citation, Citation_Log

from invenio_base.globals import cfg

from invenio.testsuite import InvenioTestCase


class CitationsTests(InvenioTestCase):

    """Test citations connection."""

    setup_flag = True
    citations_dump = None
    citations_log_dump = None

    @httpretty.activate
    def setUp(self):
        """ Initialises test by adding dummy log entries """
        from inspire.modules.citations.tasks import update_citations_log
        data = u'[[1, 2, 1, "added", "2013-04-25 04:20:30"],[2, 3, 1, "added", "2013-04-25 04:20:30"],[3, 5, 1, "added", "2013-04-25 04:20:30"],[4, 4, 2, "added", "2013-04-25 04:20:30"],[5, 5, 2, "added", "2013-04-25 04:20:30"],[6, 6, 2, "added", "2013-04-25 04:20:30"],[7, 10, 4, "added", "2013-04-25 04:20:30"],[8, 5, 1, "removed", "2013-04-25 04:20:30"],[9, 5, 4, "added", "2013-04-25 04:20:30"],[10, 6, 4, "added", "2013-04-25 04:20:30"],[11, 3, 4, "added", "2013-04-25 04:20:31"],[12, 8, 5, "added", "2013-04-25 04:20:31"],[13, 10, 4, "removed", "2013-04-25 04:20:31"],[14, 7, 6, "added", "2013-04-25 04:20:31"],[15, 9, 6, "added", "2013-04-25 04:20:31"],[16, 10, 6, "added", "2013-04-25 04:20:31"],[17, 1, 7, "added", "2013-04-25 04:20:31"],[18, 8, 7, "added", "2013-04-25 04:20:31"],[19, 10, 7, "added", "2013-04-25 04:20:31"],[20, 3, 8, "added", "2013-04-25 04:20:31"],[21, 10, 9, "added", "2013-04-25 04:20:31"],[22, 3, 9, "added", "2013-04-25 04:20:31"],[23, 3, 8, "removed", "2013-04-25 04:20:31"],[24, 1, 10, "added", "2013-04-25 04:20:31"],[25, 2, 10, "added", "2013-04-25 04:20:31"],[26, 3, 10, "added", "2013-04-25 04:20:31"]]'
        # Mocks two responses. The first one contains the dummy data and the second an empty list
        # to force update_citations_log() to terminate.
        httpretty.register_uri(
            httpretty.GET,
            cfg.get("CITATIONS_FETCH_LEGACY_URL"),
            responses=[
                httpretty.Response(body=data, status=200),
                httpretty.Response(body='[]', status=200),
            ]
        )
        if self.setup_flag:
            self.citations_dump = Citation.query.all()
            self.citations_log_dump = Citation_Log.query.all()
            self.setup_flag = False
        Citation.query.delete()
        Citation_Log.query.delete()
        update_citations_log()

    def tearDown(self):
        """Deletes all data used for testing"""
        Citation.query.delete()
        Citation_Log.query.delete()
        for cit in self.citations_log_dump:
            cit.save
        for cit in self.citations_dump:
            cit.save()

    def test_citations_rnkCITATIONDICT(self):
        """Test if rnkCITATIONDICT(Citations) is populated corectly"""
        citations = Citation.query.all()
        self.assertEqual(len(citations), 20)

    def test_citations_rnkCITATIONLOG(self):
        """Test if rnkCITATIONLOG(Citations_Log) is populated corectly"""
        citations_log = Citation_Log.query.all()
        self.assertEqual(len(citations_log), 26)

    def test_citations_references_updated(self):
        """Test if record is populated corectly with new citations"""
        from invenio_records.api import get_record
        rec1 = get_record(1)
        self.assertEqual(rec1.get("references_id"), [2, 3])

    def test_citations_references_nonexistant(self):
        """Test if record is working corectly without any citations"""
        from invenio_records.api import get_record
        rec3 = get_record(3)
        self.assertEqual(rec3.get("references_id"), None)

    def test_citations_references_empty(self):
        """Test if record is working corectly when all citations are deleted"""
        from invenio_records.api import get_record
        rec8 = get_record(8)
        self.assertEqual(rec8.get("references_id"), [])
