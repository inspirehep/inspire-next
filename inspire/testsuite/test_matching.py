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
        from invenio.base.globals import cfg
        from inspire.modules.workflows.tasks.matching import perform_request
        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )
        params = dict(p='035:"oai:arXiv.org:1505.12345"', of="id")
        obj = DummyObj()
        res = perform_request(obj, params)
        self.assertTrue(res)
        self.assertTrue("recid" in obj.extra_data)
        self.assertTrue(1234 == obj.extra_data["recid"])

    @httpretty.activate
    def test_empty_matching_result(self):
        """Test that empty matching results are handled correctly."""
        from invenio.base.globals import cfg
        from inspire.modules.workflows.tasks.matching import perform_request
        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[]",
            content_type="application/json"
        )
        params = dict(p='035:"oai:arXiv.org:1505.12345"', of="id")
        obj = DummyObj()
        res = perform_request(obj, params)
        self.assertFalse(res)
        self.assertFalse("recid" in obj.extra_data)

    @httpretty.activate
    def test_bad_matching_result(self):
        """Test that bad matching results are handled correctly."""
        from invenio.base.globals import cfg
        from inspire.modules.workflows.tasks.matching import perform_request
        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="<html></html>",
        )
        params = dict(p='035:"oai:arXiv.org:1505.12345"', of="id")
        obj = DummyObj()
        self.assertRaises(ValueError, perform_request, obj, params)

    @httpretty.activate
    def test_arxiv_results(self):
        """Test that bad matching results are handled correctly."""
        from invenio.base.globals import cfg
        from inspire.modules.workflows.tasks.matching import match_record_arxiv_remote
        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )
        obj = DummyObj()
        res = match_record_arxiv_remote(obj, "arXiv:1505.12345")
        self.assertTrue(res)

    @httpretty.activate
    def test_doi_results(self):
        """Test that bad matching results are handled correctly."""
        from invenio.base.globals import cfg
        from inspire.modules.workflows.tasks.matching import match_record_arxiv_remote
        httpretty.register_uri(
            httpretty.GET,
            cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"],
            body="[1234]",
            content_type="application/json"
        )
        obj = DummyObj()
        res = match_record_arxiv_remote(obj, "10.1086/305772")
        self.assertTrue(res)

TEST_SUITE = make_test_suite(MatchingTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
