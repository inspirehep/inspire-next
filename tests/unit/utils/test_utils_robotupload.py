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

import httpretty

from inspirehep.utils.robotupload import make_robotupload_marcxml


@httpretty.activate
def test_robotupload_bad_xml():
    """Test proper handling when bad MARCXML is sent."""
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:4000/batchuploader/robotupload/insert",
        body="[ERROR] MARCXML is not valid.\n",
        status=400
    )
    invalid_marcxml = "record></record>"
    response = make_robotupload_marcxml(
        "http://localhost:4000",
        invalid_marcxml,
        mode="insert",
    )
    assert response.status_code == 400
    assert "not valid" in response.text


@httpretty.activate
def test_robotupload_success():
    """Test proper handling when good MARCXML is sent."""
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:4000/batchuploader/robotupload/insert",
        body="[INFO] bibupload batchupload --insert /dummy/file/path\n",
        status=200
    )
    valid_marcxml = "<record></record>"
    response = make_robotupload_marcxml(
        "http://localhost:4000",
        valid_marcxml,
        mode="insert",
    )
    assert response.status_code == 200
    assert "[INFO] bibupload batchupload" in response.text


@httpretty.activate
def test_robotupload_success_append():
    """Test proper handling when good MARCXML is sent."""
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:4000/batchuploader/robotupload/append",
        body="[INFO] bibupload batchupload --append /dummy/file/path\n",
        status=200
    )
    valid_marcxml = "<record></record>"
    response = make_robotupload_marcxml(
        "http://localhost:4000",
        valid_marcxml,
        mode="append",
    )
    assert response.status_code == 200
    assert "[INFO] bibupload batchupload" in response.text


@httpretty.activate
def test_robotupload_callback_url():
    """Test passing of a callback URL."""
    body = (
        "[INFO] bibupload batchupload --insert /some/path"
        "--callback-url http://localhost"
    )
    httpretty.register_uri(
        httpretty.POST,
        "http://localhost:4000/batchuploader/robotupload/insert",
        body=body,
        status=200
    )
    valid_marcxml = "<record></record>"
    response = make_robotupload_marcxml(
        "http://localhost:4000",
        valid_marcxml,
        mode="insert",
        callback_url="http://localhost",
    )
    assert response.status_code == 200
    assert "--callback-url http://localhost" in response.text
