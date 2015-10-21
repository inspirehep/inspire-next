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

"""Tests for robotupload."""

from __future__ import print_function, absolute_import
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

import httpretty
import logging


class DummyObj(object):
    """Dummy workflow object"""
    def __init__(self):
        super(DummyObj, self).__init__()
        self.extra_data = {}
        self.log = logging.getLogger("inspire_tests")


class MatchingTests(InvenioTestCase):

    """Test the robotupload functions."""

    @httpretty.activate
    def test_matching_result(self):
        """Test that good matching results are handled correctly."""
        from invenio_base.globals import cfg
        from inspire.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )

        res = search('035:"oai:arXiv.org:1505.12345"')

        self.assertTrue(res)
        self.assertTrue(res[0] == 1234)

    @httpretty.activate
    def test_empty_matching_result(self):
        """Test that empty matching results are handled correctly."""
        from invenio_base.globals import cfg
        from inspire.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[]",
            content_type="application/json"
        )

        res = search('035:"oai:arXiv.org:1505.12345"')

        self.assertFalse(res)
        self.assertTrue(len(res) == 0)

    @httpretty.activate
    def test_bad_matching_result(self):
        """Test that bad matching results are handled correctly."""
        from invenio_base.globals import cfg
        from inspire.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="<html></html>",
        )

        self.assertRaises(ValueError, search, '035:"oai:arXiv.org:1505.12345"')

    @httpretty.activate
    def test_arxiv_results(self):
        """Test that bad matching results are handled correctly."""
        from invenio_records.api import Record
        from invenio_base.globals import cfg
        from inspire.modules.workflows.tasks.matching import match_by_arxiv_id

        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )

        record = Record({"arxiv_id": "arXiv:1505.12345"})
        res = match_by_arxiv_id(record)
        self.assertTrue(res)

        record = Record({"report_numbers": [
            {
                "value": "arXiv:1505.12345",
                "source": "arXiv",
            }
        ]})
        res = match_by_arxiv_id(record)
        self.assertTrue(res)

    @httpretty.activate
    def test_doi_results(self):
        """Test that bad matching results are handled correctly."""
        from invenio_records.api import Record
        from invenio_base.globals import cfg
        from inspire.modules.workflows.tasks.matching import match_by_doi

        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )

        record = Record({"dois": {"value": "10.1086/305772"}})
        res = match_by_doi(record)
        self.assertTrue(res)

        # FIXME Also test for multiple DOIs

TEST_SUITE = make_test_suite(MatchingTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
